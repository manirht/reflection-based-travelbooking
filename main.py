"""
Main Execution Script for Travel Booking System
Demonstrates the self-correcting reflection architecture with pivot scenarios.
"""

import os
from state import create_initial_state
from graph import compile_graph


def example_1_budget_exceeded_pivot_to_train():
    """
    Example 1: Flight exceeds budget, system pivots to train.
    
    Scenario:
    - User wants to travel from New York to Boston
    - Budget: $300
    - Flights cost ~$320-450 (too expensive)
    - System should pivot to trains (~$120-180)
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Budget Exceeded - Pivot from Flight to Train")
    print("="*80 + "\n")
    
    # Create initial state with tight budget
    initial_state = create_initial_state(
        origin="New York",
        destination="Boston",
        max_price=300.0,  # Tight budget - flights won't fit
        time_preference="flexible",
        hotel_type="budget",
        transport_mode=None,  # Let the system choose
        travel_dates={"start": "2024-03-15", "end": "2024-03-18"}
    )
    
    # Compile and run the graph
    app = compile_graph()
    
    print("🚀 Starting travel planning process...\n")
    print(f"📋 Requirements:")
    print(f"   - Route: New York → Boston")
    print(f"   - Budget: $300 (STRICT)")
    print(f"   - Hotel: budget")
    print(f"   - Dates: 2024-03-15 to 2024-03-18")
    print(f"\n{'─'*80}\n")
    
    # Run the graph
    config = {"configurable": {"thread_id": "example_1"}}
    
    for step_output in app.stream(initial_state, config):
        node_name = list(step_output.keys())[0]
        node_state = step_output[node_name]
        
        print(f"\n🔄 Node: {node_name.upper()}")
        print("─" * 80)
        
        # Display relevant information from each node
        if "messages" in node_state and node_state["messages"]:
            last_message = node_state["messages"][-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
                if len(content) > 500:
                    print(f"{content[:500]}...")
                else:
                    print(content)
        
        if "is_valid" in node_state:
            print(f"\n✓ Validation Status: {'PASSED' if node_state['is_valid'] else 'FAILED'}")
        
        if "reflection_count" in node_state and node_state["reflection_count"] > 0:
            print(f"\n🔁 Reflection Attempt: {node_state['reflection_count']}")
        
        print()
    
    print("\n" + "="*80)
    print("EXAMPLE 1 COMPLETE")
    print("="*80 + "\n")


def example_2_hotel_type_mismatch():
    """
    Example 2: User wants 5-star hotel but budget only allows 4-star.
    
    Scenario:
    - User wants luxury 5-star hotel
    - Budget: $800
    - 5-star hotels cost ~$1050+ (too expensive)
    - System should suggest 4-star alternative
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Hotel Type Adjustment - 5-star to 4-star")
    print("="*80 + "\n")
    
    initial_state = create_initial_state(
        origin="Los Angeles",
        destination="San Francisco",
        max_price=800.0,
        time_preference="early morning",
        hotel_type="5-star",  # Expensive preference
        transport_mode="flight",
        travel_dates={"start": "2024-04-01", "end": "2024-04-04"}
    )
    
    app = compile_graph()
    
    print("🚀 Starting travel planning process...\n")
    print(f"📋 Requirements:")
    print(f"   - Route: Los Angeles → San Francisco")
    print(f"   - Budget: $800")
    print(f"   - Hotel: 5-star (may need adjustment)")
    print(f"   - Transport: flight preferred")
    print(f"   - Time: early morning")
    print(f"\n{'─'*80}\n")
    
    config = {"configurable": {"thread_id": "example_2"}}
    
    for step_output in app.stream(initial_state, config):
        node_name = list(step_output.keys())[0]
        node_state = step_output[node_name]
        
        print(f"\n🔄 Node: {node_name.upper()}")
        print("─" * 80)
        
        if "messages" in node_state and node_state["messages"]:
            last_message = node_state["messages"][-1]
            if hasattr(last_message, 'content'):
                print(last_message.content[:500] if len(last_message.content) > 500 else last_message.content)
        
        if "errors" in node_state and node_state["errors"]:
            print(f"\n⚠️  Errors: {node_state['errors']}")
        
        print()
    
    print("\n" + "="*80)
    print("EXAMPLE 2 COMPLETE")
    print("="*80 + "\n")


def example_3_successful_booking():
    """
    Example 3: Everything works perfectly on first attempt.
    
    Scenario:
    - Reasonable budget
    - Flexible preferences
    - Should succeed without revisions
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Successful Booking - No Revisions Needed")
    print("="*80 + "\n")
    
    initial_state = create_initial_state(
        origin="Chicago",
        destination="Miami",
        max_price=1500.0,  # Generous budget
        time_preference="flexible",
        hotel_type="4-star",
        transport_mode=None,
        travel_dates={"start": "2024-05-10", "end": "2024-05-13"}
    )
    
    app = compile_graph()
    
    print("🚀 Starting travel planning process...\n")
    print(f"📋 Requirements:")
    print(f"   - Route: Chicago → Miami")
    print(f"   - Budget: $1500 (generous)")
    print(f"   - Hotel: 4-star")
    print(f"   - Dates: 2024-05-10 to 2024-05-13")
    print(f"\n{'─'*80}\n")
    
    config = {"configurable": {"thread_id": "example_3"}}
    
    for step_output in app.stream(initial_state, config):
        node_name = list(step_output.keys())[0]
        node_state = step_output[node_name]
        
        print(f"\n🔄 Node: {node_name.upper()}")
        print("─" * 80)
        
        if "messages" in node_state and node_state["messages"]:
            last_message = node_state["messages"][-1]
            if hasattr(last_message, 'content'):
                print(last_message.content[:500] if len(last_message.content) > 500 else last_message.content)
        
        if "final_itinerary" in node_state and node_state["final_itinerary"]:
            print("\n✅ FINAL ITINERARY APPROVED!")
        
        print()
    
    print("\n" + "="*80)
    print("EXAMPLE 3 COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Set your OpenAI API key
    # Option 1: Set environment variable
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    # Option 2: Load from .env file
    # from dotenv import load_dotenv
    # load_dotenv()
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*15 + "TRAVEL BOOKING SYSTEM - REFLECTION ARCHITECTURE" + " "*15 + "║")
    print("╚" + "="*78 + "╝")
    
    # Run examples
    try:
        example_1_budget_exceeded_pivot_to_train()
    except Exception as e:
        print(f"❌ Example 1 failed: {e}")
    
    # Uncomment to run additional examples
    # try:
    #     example_2_hotel_type_mismatch()
    # except Exception as e:
    #     print(f"❌ Example 2 failed: {e}")
    
    # try:
    #     example_3_successful_booking()
    # except Exception as e:
    #     print(f"❌ Example 3 failed: {e}")

