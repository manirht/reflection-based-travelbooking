# Travel Booking System - Reflection-Based Architecture

A **production-ready**, self-correcting autonomous travel booking system built with **LangGraph** and **Groq**. This system integrates with RapidAPI Booking.com15 for flights, hotels, and car rentals, and demonstrates advanced agentic patterns including reflection loops, multi-modal transport planning, and human-in-the-loop approval.

## 🏗️ Architecture Overview

This system implements a **Reflection-based Architecture** where a Judge node validates the Planner's output and triggers revisions when constraints are violated.

### Key Components

1. **Supervisor Node** - The orchestrator that parses user preferences and coordinates the workflow
2. **Planner Node** - The worker that generates travel itineraries using available tools
3. **Judge Node** - The reflection layer that validates proposals against user constraints
4. **Human Approval** - A checkpoint for final user confirmation before booking

### Self-Correction Loop

```
User Request → Supervisor → Planner → Judge
                              ↑         ↓
                              └─────────┘
                            (if invalid, max 3 attempts)
                                   ↓
                            Human Approval → Complete
```

## 🎯 Features

### ✅ Enhanced State Management
- **TypedDict-based state** tracking conversation history, preferences, and validation status
- **User preferences** including budget, time preferences, hotel type, and transport mode
- **Error tracking** for tool failures and constraint violations
- **Reflection counter** to limit revision attempts

### ✅ Real API Integrations
- **RapidAPI Booking.com15** - Unified API for flights, hotels, and car rentals
- **Groq** - Fast LLM inference for agent reasoning
- **Hardcoded Train Data** - Demo train options (no API required)

### ✅ Multi-Modal Transport
- **Flights** - Fast but potentially expensive (via RapidAPI)
- **Trains** - Slower but budget-friendly (hardcoded demo data)
- **Car Rentals** - Flexible for road trips (via RapidAPI)

### ✅ Dynamic Hotel Search
- Supports multiple categories: 5-star, 4-star, 3-star, boutique, hostel, budget
- Price filtering based on user budget
- Real-time availability via RapidAPI Booking.com15

### ✅ Intelligent Failure Handling
- **Budget exceeded** - Automatically pivots to cheaper alternatives
- **API errors** - Retry logic with exponential backoff (using tenacity)
- **Missing API keys** - Clear error messages with setup instructions
- **Constraint violations** - Judge provides specific feedback for revision

### ✅ Human-in-the-Loop
- Displays complete itinerary before finalization
- **Manual approval required** - System waits for user input (yes/no)
- Shows budget breakdown and remaining balance

## 📁 Project Structure

```
.
├── state.py          # Enhanced AgentState with preferences tracking
├── tools.py          # Pydantic-validated tools (flights, trains, cars, hotels)
├── api_clients.py    # API client classes for external services
├── nodes.py          # Supervisor, Planner, and Judge nodes
├── graph.py          # LangGraph workflow with reflection loop
├── main.py           # Example execution scenarios
├── .env.example      # Template for environment variables
├── requirements.txt  # Python dependencies
├── SETUP.md          # Detailed setup instructions
└── README.md         # This file
```

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

This installs:
- `langgraph` - State machine framework
- `langchain-groq` - Groq LLM integration (fast inference)
- `pydantic` - Data validation
- `requests` & `httpx` - HTTP clients for API calls
- `tenacity` - Retry logic with exponential backoff
- `python-dotenv` - Environment variable management

### Environment Setup

**IMPORTANT**: This system requires real API keys to function.

1. **Copy the environment template:**

```bash
cp .env.example .env
```

2. **Edit `.env` and add your API keys:**

```bash
# Required: Groq API Key (for LLM)
# Get your free API key at: https://console.groq.com/
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_TEMPERATURE=0

# Required: RapidAPI Booking.com15 (for flights, hotels, cars)
# Subscribe at: https://rapidapi.com/DataCrawler/api/booking-com15
RAPIDAPI_KEY=your-rapidapi-key-here
RAPIDAPI_HOST=booking-com15.p.rapidapi.com
RAPIDAPI_BASE_URL=https://booking-com15.p.rapidapi.com/api/v1

# Note: Trains use hardcoded demo data (no API key needed)
```

3. **See SETUP.md for detailed instructions on obtaining each API key.**

### Running the System

```bash
python main.py
```

**Note**: The system will now:
- Make real API calls to RapidAPI Booking.com15 for flights, hotels, and cars
- Use Groq for fast LLM inference (free tier available)
- Use hardcoded data for train searches (no API needed)
- Wait for manual user approval (type "yes" or "no")
- Charge API usage against your accounts (Groq and RapidAPI have free tiers)

## 📊 Example Scenarios

### Example 1: Budget Exceeded - Pivot to Train

**Scenario**: User wants to travel from New York to Boston with a $300 budget.

**Expected Behavior**:
1. Planner tries to book a flight (~$320-450)
2. Judge rejects due to budget violation
3. Planner pivots to train (~$120-180)
4. Judge approves
5. Human approval checkpoint
6. Booking complete

### Example 2: Hotel Type Adjustment

**Scenario**: User wants a 5-star hotel but budget only allows 4-star.

**Expected Behavior**:
1. Planner books 5-star hotel (~$1050 for 3 nights)
2. Judge rejects due to total cost exceeding budget
3. Planner downgrades to 4-star (~$540)
4. Judge approves
5. Booking complete

### Example 3: Successful First Attempt

**Scenario**: Generous budget with flexible preferences.

**Expected Behavior**:
1. Planner creates optimal itinerary
2. Judge approves immediately
3. No revisions needed
4. Booking complete

## 🔧 Customization

### Adding New Tools

Add new tools in `tools.py`:

```python
@tool(args_schema=YourInputSchema)
def your_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """Your tool description."""
    # Implementation
    return {"status": "success", "data": ...}
```

### Modifying Validation Logic

Update the `judge_node` in `nodes.py` to add custom validation rules:

```python
def judge_node(state: AgentState) -> Dict[str, Any]:
    # Add your custom validation
    if custom_condition:
        validation_errors.append("Your error message")
    # ...
```

### Adjusting Reflection Limits

Modify the `should_revise` function in `graph.py`:

```python
def should_revise(state: AgentState) -> Literal["planner", "human_approval", "end"]:
    max_attempts = 5  # Change from 3 to 5
    # ...
```

## 🧪 Testing

The system includes built-in failure simulation for testing:

- **OUT_OF_BUDGET** errors when prices exceed limits
- **NOT_AVAILABLE** errors for unavailable options
- **INVALID_TYPE** errors for unsupported categories

## 🎨 Visualization

The Mermaid diagram shows the complete workflow including:
- Node relationships
- Conditional routing
- Self-correction loop
- Tool connections

## 📝 Key Design Patterns

### 1. Reflection Pattern
The Judge node acts as a critic, providing structured feedback that the Planner uses to improve its output.

### 2. Tool Abstraction
All tools follow a consistent Pydantic schema pattern for validation and error handling.

### 3. State Immutability
State updates are additive (using `operator.add` for messages) to maintain conversation history.

### 4. Graceful Degradation
The system tries alternatives before giving up, with a maximum retry limit to prevent infinite loops.

## 🔒 Production Considerations

For production deployment, consider:

1. **API Rate Limiting** - Add retry logic and backoff strategies
2. **Real API Integration** - Replace mock tools with actual booking APIs
3. **User Authentication** - Add user session management
4. **Payment Processing** - Integrate payment gateways
5. **Error Monitoring** - Add logging and alerting
6. **Database Persistence** - Store bookings and user preferences
7. **Async Processing** - Use async tools for better performance

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [Pydantic Validation](https://docs.pydantic.dev/)

## 🤝 Contributing

This is a demonstration project. Feel free to extend it with:
- Additional transport modes (buses, ferries)
- Activity planning and recommendations
- Weather-based suggestions
- Multi-city itineraries
- Group booking support

## 📄 License

MIT License - Feel free to use this as a learning resource or starting point for your own projects.

