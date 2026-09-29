"""
Enhanced State Management for Travel Booking System
Tracks conversation history, user preferences, itinerary drafts, errors, and validation status.
"""

from typing import Annotated, TypedDict, List, Dict, Any, Optional
import operator
from langchain_core.messages import BaseMessage


class UserPreferences(TypedDict):
    """User preferences for travel booking."""
    max_price: float  # Maximum budget in USD
    time_preference: str  # e.g., "early morning", "afternoon", "evening", "flexible"
    hotel_type: str  # e.g., "5-star", "4-star", "hostel", "boutique", "budget"
    transport_mode: Optional[str]  # e.g., "flight", "train", "car", "any"
    destination: str  # Travel destination
    origin: str  # Starting location
    travel_dates: Dict[str, str]  # {"start": "2024-03-01", "end": "2024-03-05"}


class ItineraryDraft(TypedDict):
    """Structured itinerary proposal."""
    transport: Dict[str, Any]  # Transport details (type, price, time, etc.)
    hotel: Dict[str, Any]  # Hotel details (name, type, price, etc.)
    total_cost: float  # Total estimated cost
    schedule: List[Dict[str, str]]  # Daily schedule
    alternatives: Optional[List[Dict[str, Any]]]  # Alternative options if available


class AgentState(TypedDict):
    """
    Enhanced state for the Travel Booking System.
    
    Attributes:
        messages: Conversation history (annotated for automatic appending)
        preferences: User preferences for the trip
        itinerary_draft: Current itinerary proposal from the planner
        errors: List of errors encountered during tool execution
        is_valid: Flag indicating if the current itinerary passes validation
        reflection_count: Number of times the planner has been asked to revise
        user_approved: Flag for human-in-the-loop approval
        final_itinerary: The approved final itinerary
    """
    messages: Annotated[List[BaseMessage], operator.add]
    preferences: UserPreferences
    itinerary_draft: Optional[ItineraryDraft]
    errors: List[str]
    is_valid: bool
    reflection_count: int
    user_approved: bool
    final_itinerary: Optional[ItineraryDraft]


def create_initial_state(
    destination: str,
    origin: str,
    max_price: float,
    time_preference: str = "flexible",
    hotel_type: str = "4-star",
    transport_mode: Optional[str] = None,
    travel_dates: Optional[Dict[str, str]] = None
) -> AgentState:
    """
    Factory function to create initial agent state with user preferences.
    
    Args:
        destination: Travel destination
        origin: Starting location
        max_price: Maximum budget in USD
        time_preference: Preferred travel time
        hotel_type: Preferred hotel category
        transport_mode: Preferred transport mode (optional)
        travel_dates: Travel dates (optional, defaults to next week)
    
    Returns:
        Initialized AgentState
    """
    if travel_dates is None:
        travel_dates = {"start": "2024-03-15", "end": "2024-03-18"}
    
    return AgentState(
        messages=[],
        preferences=UserPreferences(
            max_price=max_price,
            time_preference=time_preference,
            hotel_type=hotel_type,
            transport_mode=transport_mode,
            destination=destination,
            origin=origin,
            travel_dates=travel_dates
        ),
        itinerary_draft=None,
        errors=[],
        is_valid=False,
        reflection_count=0,
        user_approved=False,
        final_itinerary=None
    )

