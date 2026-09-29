"""
Specialized Agent Nodes for Travel Booking System
Includes Supervisor, Planner, and Judge (Reflection Layer) nodes.
"""

from typing import Dict, Any, List
import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from state import AgentState, ItineraryDraft
from tools import ALL_TOOLS

# Load environment variables
load_dotenv()

# Initialize the LLM with Groq API key from environment
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in environment variables. "
        "Please set it in your .env file. "
        "Copy .env.example to .env and add your Groq API key. "
        "Get your API key from: https://console.groq.com/"
    )

model_name = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
temperature = float(os.getenv("GROQ_TEMPERATURE", "0"))

print(f"🤖 Initializing Groq with model: {model_name}")

llm = ChatGroq(
    model=model_name,
    temperature=temperature,
    api_key=api_key
)
llm_with_tools = llm.bind_tools(ALL_TOOLS)


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    Supervisor Node - The Brain
    Parses user input, manages task list, and routes to specialists.
    """
    preferences = state["preferences"]
    
    # Create a comprehensive briefing for the planner
    system_prompt = f"""You are the Supervisor of a travel booking system.
    
User Preferences:
- Origin: {preferences['origin']}
- Destination: {preferences['destination']}
- Travel Dates: {preferences['travel_dates']['start']} to {preferences['travel_dates']['end']}
- Maximum Budget: ${preferences['max_price']}
- Time Preference: {preferences['time_preference']}
- Hotel Type: {preferences['hotel_type']}
- Transport Mode: {preferences.get('transport_mode', 'any')}

Your task is to coordinate the planning process. You will:
1. Brief the Planner agent with these requirements
2. Monitor the Judge's feedback
3. Ensure the final itinerary meets all constraints

Current Status: Initiating planning phase."""

    message = HumanMessage(content=system_prompt)
    
    return {
        "messages": [message]
    }


def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner Agent - The Worker
    Generates cohesive travel plans using available tools.
    Handles multi-modal transport and adapts based on Judge feedback.
    """
    preferences = state["preferences"]
    errors = state.get("errors", [])
    reflection_count = state.get("reflection_count", 0)
    
    # Check if this is a revision attempt
    is_revision = reflection_count > 0
    
    # Build the planning prompt
    if is_revision:
        last_feedback = [msg for msg in state["messages"] if "JUDGE FEEDBACK" in str(msg.content)]
        feedback_text = last_feedback[-1].content if last_feedback else "No specific feedback"
        
        system_prompt = f"""You are a Travel Planner Agent. This is revision attempt #{reflection_count}.

PREVIOUS ATTEMPT FAILED. Judge Feedback:
{feedback_text}

You MUST address the issues raised. Consider:
1. If transport was too expensive, try alternative modes (train instead of flight, or car rental)
2. If hotel was too expensive, try a different hotel category
3. Ensure total cost is UNDER ${preferences['max_price']}

Use the available tools to search for better options."""
    else:
        system_prompt = f"""You are a Travel Planner Agent. Create a comprehensive travel itinerary.

Requirements:
- Origin: {preferences['origin']}
- Destination: {preferences['destination']}
- Dates: {preferences['travel_dates']['start']} to {preferences['travel_dates']['end']}
- Maximum Budget: ${preferences['max_price']} (STRICT LIMIT)
- Time Preference: {preferences['time_preference']}
- Hotel Type: {preferences['hotel_type']}
- Preferred Transport: {preferences.get('transport_mode', 'any - choose the best option')}

Available Tools:
1. search_flights - For air travel
2. search_trains - For rail travel (usually cheaper but slower)
3. search_car_rentals - For road trips
4. search_hotels - For accommodation

IMPORTANT: 
- Always check prices against the budget
- If one transport mode is too expensive, try alternatives
- Create a complete itinerary with transport + hotel
- Return a structured JSON summary at the end"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Please create the best travel plan within ${preferences['max_price']} budget.")
    ]
    
    # Invoke the model with tools
    response = llm_with_tools.invoke(messages)
    
    # Process tool calls if any
    tool_messages = []
    if hasattr(response, 'tool_calls') and response.tool_calls:
        from langgraph.prebuilt import ToolNode
        tool_node = ToolNode(ALL_TOOLS)
        
        # Execute tools
        tool_results = tool_node.invoke({"messages": [response]})
        tool_messages = tool_results.get("messages", [])
        
        # Get final response after tool execution
        all_messages = messages + [response] + tool_messages
        final_response = llm.invoke(all_messages + [
            HumanMessage(content="Based on the tool results, create a final itinerary summary in JSON format with: transport, hotel, total_cost, and schedule.")
        ])
    else:
        final_response = response
    
    # Try to extract structured itinerary from response
    itinerary_draft = _parse_itinerary_from_response(final_response.content, preferences)
    
    return {
        "messages": [response] + tool_messages + [final_response],
        "itinerary_draft": itinerary_draft,
        "reflection_count": reflection_count
    }


def judge_node(state: AgentState) -> Dict[str, Any]:
    """
    Judge Node - The Reflection Layer
    Reviews the Planner's output and validates against user preferences.
    """
    preferences = state["preferences"]
    itinerary_draft = state.get("itinerary_draft")
    
    if not itinerary_draft:
        return {
            "is_valid": False,
            "errors": ["No itinerary draft found"],
            "messages": [AIMessage(content="JUDGE FEEDBACK: No itinerary was generated. Please create a complete plan.")]
        }
    
    # Validation checks
    validation_errors = []
    total_cost = itinerary_draft.get("total_cost", 0)
    
    # Check 1: Budget validation
    if total_cost > preferences["max_price"]:
        validation_errors.append(
            f"Budget exceeded: ${total_cost} > ${preferences['max_price']}. "
            f"You must reduce costs by ${total_cost - preferences['max_price']}."
        )
    
    # Check 2: Hotel type validation
    hotel_info = itinerary_draft.get("hotel", {})
    if hotel_info:
        # Check if hotel has either 'selected_option' (from tool) or 'name' (from LLM)
        selected_hotel = hotel_info.get("selected_option", {})
        hotel_name = hotel_info.get("name")
        if not selected_hotel and not hotel_name:
            validation_errors.append("No hotel selected in the itinerary.")
    
    # Check 3: Transport validation
    transport_info = itinerary_draft.get("transport", {})
    if not transport_info:
        validation_errors.append("Transport booking failed or is missing.")
    elif transport_info.get("status") == "error":
        validation_errors.append("Transport booking failed or is missing.")
    elif not transport_info.get("type") and not transport_info.get("operator"):
        # Check if transport has meaningful data (either 'type' or 'operator' field)
        validation_errors.append("Transport booking failed or is missing.")
    
    # Determine if valid
    is_valid = len(validation_errors) == 0
    
    if is_valid:
        feedback_message = f"""JUDGE FEEDBACK: ✓ APPROVED

The itinerary meets all requirements:
- Total Cost: ${total_cost} (within budget of ${preferences['max_price']})
- Transport: {transport_info.get('transport_type', 'N/A')} arranged
- Hotel: {hotel_info.get('selected_option', {}).get('name', 'N/A')} booked

Proceeding to human approval."""
    else:
        feedback_message = f"""JUDGE FEEDBACK: ✗ REJECTED

Issues found:
{chr(10).join(f"- {error}" for error in validation_errors)}

Please revise the itinerary to address these issues."""
    
    return {
        "is_valid": is_valid,
        "errors": validation_errors if not is_valid else [],
        "messages": [AIMessage(content=feedback_message)]
    }


def _parse_itinerary_from_response(response_text: str, preferences: Dict) -> ItineraryDraft:
    """Helper function to parse itinerary from LLM response."""
    # This is a simplified parser - in production, you'd use more robust JSON extraction
    try:
        # Try to find JSON in the response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())

            # Handle nested "itinerary" key if present
            if "itinerary" in data and isinstance(data["itinerary"], dict):
                data = data["itinerary"]

            # Extract data with fallbacks
            transport = data.get("transport", {})
            hotel = data.get("hotel", {})

            # Debug logging
            print(f"\n🔍 DEBUG - Parsed transport: {transport}")
            print(f"🔍 DEBUG - Parsed hotel: {hotel}")

            return ItineraryDraft(
                transport=transport,
                hotel=hotel,
                total_cost=data.get("total_cost", 0),
                schedule=data.get("schedule", []),
                alternatives=data.get("alternatives")
            )
    except Exception as e:
        print(f"\n⚠️ WARNING - Failed to parse itinerary: {e}")
        print(f"Response text: {response_text[:500]}")

    # Fallback: return empty draft
    print("\n⚠️ WARNING - Returning empty itinerary draft")
    return ItineraryDraft(
        transport={},
        hotel={},
        total_cost=0,
        schedule=[],
        alternatives=None
    )

