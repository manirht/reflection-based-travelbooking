"""
Comprehensive Test Script for Travel Booking System
Tests individual components and full workflow with Groq LLM.
"""

import os
import sys
from dotenv import load_dotenv
from state import create_initial_state, AgentState
from tools import search_flights, search_trains, search_hotels, search_car_rentals

# Load environment variables from .env file
load_dotenv()


def check_environment():
    """Check if required environment variables are set."""
    print("Checking environment configuration...")

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or groq_key == "your-groq-api-key-here":
        print("❌ GROQ_API_KEY not set in .env file")
        print("   Please add your Groq API key to .env file")
        print("   Get your key from: https://console.groq.com/")
        return False

    print(f"✓ GROQ_API_KEY found: {groq_key[:20]}...")
    print(f"✓ GROQ_MODEL: {os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')}")
    print()
    return True


def test_state_creation():
    """Test that state creation works correctly."""
    print("Testing state creation...")
    
    state = create_initial_state(
        origin="New York",
        destination="Boston",
        max_price=500.0,
        hotel_type="4-star"
    )
    
    assert state["preferences"]["origin"] == "New York"
    assert state["preferences"]["destination"] == "Boston"
    assert state["preferences"]["max_price"] == 500.0
    assert state["reflection_count"] == 0
    assert state["is_valid"] == False
    
    print("✓ State creation test passed!\n")


def test_flight_tool():
    """Test flight search tool."""
    print("Testing flight search tool...")
    
    # Test successful search
    result = search_flights.invoke({
        "origin": "New York",
        "destination": "Boston",
        "date": "2024-03-15",
        "time_preference": "flexible",
        "max_price": 500.0
    })
    
    assert result["status"] == "success"
    assert "selected_option" in result
    print(f"✓ Flight search successful: {result['selected_option']['airline']} - ${result['selected_option']['price']}")
    
    # Test budget exceeded
    result = search_flights.invoke({
        "origin": "New York",
        "destination": "Boston",
        "date": "2024-03-15",
        "time_preference": "flexible",
        "max_price": 100.0  # Too low
    })
    
    assert result["status"] == "error"
    assert result["error_type"] == "OUT_OF_BUDGET"
    print(f"✓ Budget validation working: {result['message']}\n")


def test_train_tool():
    """Test train search tool."""
    print("Testing train search tool...")
    
    result = search_trains.invoke({
        "origin": "New York",
        "destination": "Boston",
        "date": "2024-03-15",
        "time_preference": "flexible",
        "max_price": 200.0
    })
    
    assert result["status"] == "success"
    assert "selected_option" in result
    print(f"✓ Train search successful: {result['selected_option']['operator']} - ${result['selected_option']['price']}\n")


def test_hotel_tool():
    """Test hotel search tool."""
    print("Testing hotel search tool...")

    # Test 3-star hotel (more affordable)
    result = search_hotels.invoke({
        "location": "Boston",
        "check_in": "2024-03-15",
        "check_out": "2024-03-18",
        "hotel_type": "3-star",
        "max_price_per_night": 150.0
    })

    assert result["status"] == "success"
    assert "selected_option" in result
    print(f"✓ Hotel search successful: {result['selected_option']['name']} - ${result['selected_option']['price_per_night']}/night")

    # Test budget hotel
    result = search_hotels.invoke({
        "location": "Boston",
        "check_in": "2024-03-15",
        "check_out": "2024-03-18",
        "hotel_type": "budget",
        "max_price_per_night": 100.0
    })

    assert result["status"] == "success"
    print(f"✓ Budget hotel found: {result['selected_option']['name']} - ${result['selected_option']['price_per_night']}/night")

    # Test out of budget scenario
    result = search_hotels.invoke({
        "location": "Boston",
        "check_in": "2024-03-15",
        "check_out": "2024-03-18",
        "hotel_type": "5-star",
        "max_price_per_night": 100.0  # Too low for 5-star
    })

    assert result["status"] == "error"
    assert result["error_type"] == "OUT_OF_BUDGET"
    print(f"✓ Budget validation working: {result['message']}\n")


def test_car_rental_tool():
    """Test car rental tool."""
    print("Testing car rental tool...")
    
    result = search_car_rentals.invoke({
        "location": "Boston",
        "start_date": "2024-03-15",
        "end_date": "2024-03-18",
        "car_type": "economy",
        "max_price": 200.0
    })
    
    assert result["status"] == "success"
    assert "selected_option" in result
    print(f"✓ Car rental successful: {result['selected_option']['car_model']} - ${result['selected_option']['total_price']} total\n")


def test_graph_structure():
    """Test that the graph compiles without errors."""
    print("Testing graph compilation...")
    
    try:
        from graph import compile_graph
        app = compile_graph()
        print("✓ Graph compiled successfully!\n")
        return True
    except Exception as e:
        print(f"✗ Graph compilation failed: {e}\n")
        return False


def test_llm_initialization():
    """Test that Groq LLM initializes correctly."""
    print("Testing Groq LLM initialization...")

    try:
        from nodes import llm
        print(f"✓ Groq LLM initialized successfully!")
        print(f"  Model: {os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')}")
        print()
        return True
    except Exception as e:
        print(f"✗ LLM initialization failed: {e}\n")
        return False


def test_simple_workflow():
    """Test a simple end-to-end workflow."""
    print("Testing simple workflow (budget trip)...")
    print("This will test the full system with Groq LLM and hardcoded data.")
    print()

    try:
        from graph import compile_graph

        # Create a simple test case
        initial_state = create_initial_state(
            origin="New York",
            destination="Boston",
            max_price=300.0,
            time_preference="flexible",
            hotel_type="budget",
            transport_mode=None,
            travel_dates={"start": "2024-03-15", "end": "2024-03-18"}
        )

        app = compile_graph()
        config = {"configurable": {"thread_id": "test_simple"}}

        print("🚀 Running workflow...")
        print("   (This may take 30-60 seconds with LLM calls)")
        print()

        step_count = 0
        max_steps = 10  # Prevent infinite loops

        for step_output in app.stream(initial_state, config):
            step_count += 1
            if step_count > max_steps:
                print(f"⚠️  Workflow exceeded {max_steps} steps, stopping test")
                break

            node_name = list(step_output.keys())[0]
            print(f"   Step {step_count}: {node_name}")

            # Check if we reached human approval
            if node_name == "human_approval":
                print()
                print("✓ Workflow reached human approval stage!")
                print("✓ Simple workflow test passed!")
                print()
                return True

        print("⚠️  Workflow completed without reaching approval")
        return False

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("TRAVEL BOOKING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")

    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please configure .env file first.")
        sys.exit(1)

    try:
        # Component tests
        print("="*80)
        print("PART 1: COMPONENT TESTS")
        print("="*80 + "\n")

        test_state_creation()
        test_flight_tool()
        test_train_tool()
        test_hotel_tool()
        test_car_rental_tool()
        test_graph_structure()
        test_llm_initialization()

        print("="*80)
        print("✅ ALL COMPONENT TESTS PASSED!")
        print("="*80 + "\n")

        # Integration test
        print("="*80)
        print("PART 2: INTEGRATION TEST")
        print("="*80 + "\n")

        print("⚠️  NOTE: This test will make real API calls to Groq.")
        print("   It will use your Groq API tokens.")
        print()

        user_input = input("Do you want to run the integration test? (yes/no): ").strip().lower()

        if user_input in ["yes", "y"]:
            print()
            if test_simple_workflow():
                print("="*80)
                print("✅ ALL TESTS PASSED (INCLUDING INTEGRATION)!")
                print("="*80 + "\n")
            else:
                print("="*80)
                print("⚠️  INTEGRATION TEST HAD ISSUES")
                print("="*80 + "\n")
        else:
            print("\n⏭️  Skipping integration test")
            print("="*80)
            print("✅ COMPONENT TESTS PASSED!")
            print("="*80 + "\n")

        print("System is ready. Run 'python main.py' for full examples.")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

