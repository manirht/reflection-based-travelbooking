"""
LangGraph Workflow with Reflection Loop and Human-in-the-Loop
Implements the Planner -> Judge -> Planner self-correction architecture.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import supervisor_node, planner_node, judge_node


def should_continue_planning(state: AgentState) -> Literal["judge", "end"]:
    """
    Routing function after planner.
    Always route to judge for validation.
    """
    return "judge"


def should_revise(state: AgentState) -> Literal["planner", "human_approval", "end"]:
    """
    Routing function after judge.
    
    Routes:
    - If valid -> human_approval
    - If invalid and attempts < 3 -> planner (for revision)
    - If invalid and attempts >= 3 -> end (give up)
    """
    is_valid = state.get("is_valid", False)
    reflection_count = state.get("reflection_count", 0)
    
    if is_valid:
        return "human_approval"
    elif reflection_count < 3:
        # Increment reflection count and try again
        return "planner"
    else:
        # Too many attempts, give up
        return "end"


def human_approval_node(state: AgentState) -> dict:
    """
    Human-in-the-Loop checkpoint.
    In a real system, this would pause and wait for user input.
    For demo purposes, we'll auto-approve if the itinerary is valid.
    """
    from langchain_core.messages import AIMessage
    
    itinerary = state.get("itinerary_draft")
    
    # Display the itinerary for approval
    # Handle both formats: tool response format and LLM-generated format
    transport = itinerary.get('transport', {})
    hotel = itinerary.get('hotel', {})

    # Extract transport info (handle both formats)
    if 'selected_option' in transport:
        # Tool response format
        transport_type = transport.get('transport_type', 'N/A')
        transport_details = transport.get('selected_option', {})
        transport_price = transport_details.get('price', 0)
    else:
        # LLM-generated format
        transport_type = transport.get('type', 'N/A')
        transport_details = transport
        transport_price = transport.get('price', 0)

    # Extract hotel info (handle both formats)
    if 'selected_option' in hotel:
        # Tool response format
        hotel_name = hotel.get('selected_option', {}).get('name', 'N/A')
        hotel_price = hotel.get('selected_option', {}).get('price_per_night', 0)
    else:
        # LLM-generated format
        hotel_name = hotel.get('name', 'N/A')
        hotel_price = hotel.get('price_per_night', 0)

    approval_message = f"""
╔══════════════════════════════════════════════════════════════╗
║           ITINERARY READY FOR APPROVAL                        ║
╚══════════════════════════════════════════════════════════════╝

📍 Route: {state['preferences']['origin']} → {state['preferences']['destination']}
📅 Dates: {state['preferences']['travel_dates']['start']} to {state['preferences']['travel_dates']['end']}

🚗 TRANSPORT:
   Type: {transport_type}
   Details: {transport_details}

🏨 ACCOMMODATION:
   Hotel: {hotel_name}
   Type: {state['preferences']['hotel_type']}
   Price/night: ${hotel_price}

💰 TOTAL COST: ${itinerary.get('total_cost', 0)}
   Budget: ${state['preferences']['max_price']}
   Remaining: ${state['preferences']['max_price'] - itinerary.get('total_cost', 0)}

═══════════════════════════════════════════════════════════════

⏸️  WAITING FOR USER APPROVAL...
"""

    print(approval_message)

    # Wait for actual user input (PRODUCTION MODE)
    print("\n" + "="*80)
    print("Do you approve this itinerary? (yes/no): ", end="", flush=True)

    try:
        user_input = input().strip().lower()
        user_approved = user_input in ["yes", "y", "approve", "approved"]

        if user_approved:
            print("✅ Itinerary APPROVED by user")
        else:
            print("❌ Itinerary REJECTED by user")
    except (EOFError, KeyboardInterrupt):
        print("\n❌ User input interrupted - treating as REJECTED")
        user_approved = False

    return {
        "user_approved": user_approved,
        "final_itinerary": itinerary if user_approved else None,
        "messages": [AIMessage(content=f"User approval: {'✓ APPROVED' if user_approved else '✗ REJECTED'}")]
    }


def increment_reflection_count(state: AgentState) -> dict:
    """Helper to increment reflection count when routing back to planner."""
    return {
        "reflection_count": state.get("reflection_count", 0) + 1
    }


def build_graph() -> StateGraph:
    """
    Build the LangGraph workflow with reflection loop.
    
    Flow:
    1. supervisor -> planner
    2. planner -> judge
    3. judge -> (if valid) human_approval -> end
    4. judge -> (if invalid) planner (revision loop, max 3 times)
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("judge", judge_node)
    workflow.add_node("human_approval", human_approval_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add edges
    workflow.add_edge("supervisor", "planner")
    
    # Conditional edge from planner to judge
    workflow.add_conditional_edges(
        "planner",
        should_continue_planning,
        {
            "judge": "judge",
            "end": END
        }
    )
    
    # Conditional edge from judge (reflection loop)
    workflow.add_conditional_edges(
        "judge",
        should_revise,
        {
            "planner": "planner",  # Revision loop
            "human_approval": "human_approval",
            "end": END
        }
    )
    
    # Edge from human approval to end
    workflow.add_edge("human_approval", END)
    
    return workflow


def compile_graph():
    """
    Compile the graph with memory for checkpointing.
    Enables human-in-the-loop and state persistence.
    """
    workflow = build_graph()
    
    # Add memory saver for checkpointing
    memory = MemorySaver()
    
    # Compile with checkpointing enabled
    app = workflow.compile(checkpointer=memory)
    
    return app


# For visualization
def get_graph_visualization():
    """Get the Mermaid diagram of the graph."""
    workflow = build_graph()
    try:
        return workflow.get_graph().draw_mermaid()
    except:
        return """
graph TD
    START([Start]) --> supervisor[Supervisor Node]
    supervisor --> planner[Planner Node]
    planner --> judge[Judge Node]
    judge -->|Valid| human_approval[Human Approval]
    judge -->|Invalid & attempts < 3| planner
    judge -->|Invalid & attempts >= 3| END([End])
    human_approval --> END
    
    style planner fill:#e1f5ff
    style judge fill:#fff4e1
    style human_approval fill:#e8f5e9
"""

