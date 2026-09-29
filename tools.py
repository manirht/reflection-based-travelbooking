"""
Pydantic-Validated Tools for Travel Booking System
Uses hardcoded data for all travel options (flights, hotels, trains, car rentals).
No external API calls are made.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class FlightSearchInput(BaseModel):
    """Input schema for flight search."""
    origin: str = Field(description="Departure city")
    destination: str = Field(description="Arrival city")
    date: str = Field(description="Travel date in YYYY-MM-DD format")
    time_preference: str = Field(default="flexible", description="Time preference: early morning, afternoon, evening, flexible")
    max_price: Optional[float] = Field(default=None, description="Maximum price in USD")


class TrainSearchInput(BaseModel):
    """Input schema for train search."""
    origin: str = Field(description="Departure city")
    destination: str = Field(description="Arrival city")
    date: str = Field(description="Travel date in YYYY-MM-DD format")
    time_preference: str = Field(default="flexible", description="Time preference: early morning, afternoon, evening, flexible")
    max_price: Optional[float] = Field(default=None, description="Maximum price in USD")


class CarRentalSearchInput(BaseModel):
    """Input schema for car rental search."""
    location: str = Field(description="Pickup location")
    start_date: str = Field(description="Rental start date in YYYY-MM-DD format")
    end_date: str = Field(description="Rental end date in YYYY-MM-DD format")
    car_type: str = Field(default="economy", description="Car type: economy, compact, suv, luxury")
    max_price: Optional[float] = Field(default=None, description="Maximum price per day in USD")


class HotelSearchInput(BaseModel):
    """Input schema for hotel search."""
    location: str = Field(description="Hotel location/city")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format")
    hotel_type: str = Field(description="Hotel category: 5-star, 4-star, 3-star, hostel, boutique, budget")
    max_price_per_night: Optional[float] = Field(default=None, description="Maximum price per night in USD")


@tool(args_schema=FlightSearchInput)
def search_flights(
    origin: str,
    destination: str,
    date: str,
    time_preference: str = "flexible",
    max_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Search for available flights between two cities.
    Using hardcoded data for demonstration.

    Args:
        origin: IATA airport code (e.g., "JFK" for New York)
        destination: IATA airport code (e.g., "LAX" for Los Angeles)
        date: Departure date in YYYY-MM-DD format
        time_preference: Time preference (early morning, afternoon, evening, flexible)
        max_price: Maximum price in USD

    Returns:
        Dict with flight options or error information
    """
    # Hardcoded flight options for demonstration
    flight_options = [
        {
            "airline": "Delta Airlines",
            "flight_number": "DL1234",
            "departure_time": "06:00 AM",
            "arrival_time": "09:30 AM",
            "price": 350.00,
            "duration": "3h 30m",
            "class": "Economy",
            "type": "early morning"
        },
        {
            "airline": "United Airlines",
            "flight_number": "UA5678",
            "departure_time": "02:00 PM",
            "arrival_time": "05:15 PM",
            "price": 280.00,
            "duration": "3h 15m",
            "class": "Economy",
            "type": "afternoon"
        },
        {
            "airline": "JetBlue",
            "flight_number": "B6910",
            "departure_time": "07:30 PM",
            "arrival_time": "10:45 PM",
            "price": 220.00,
            "duration": "3h 15m",
            "class": "Economy",
            "type": "evening"
        },
        {
            "airline": "Southwest",
            "flight_number": "WN2468",
            "departure_time": "11:00 AM",
            "arrival_time": "02:20 PM",
            "price": 300.00,
            "duration": "3h 20m",
            "class": "Economy",
            "type": "flexible"
        }
    ]

    # Filter by time preference
    if time_preference != "flexible":
        filtered_flights = [f for f in flight_options if f["type"] == time_preference or f["type"] == "flexible"]
        if filtered_flights:
            flight_options = filtered_flights

    # Filter by max price
    if max_price:
        flight_options = [f for f in flight_options if f["price"] <= max_price]

    if not flight_options:
        return {
            "status": "error",
            "error_type": "OUT_OF_BUDGET" if max_price else "NO_RESULTS",
            "message": f"No flights found from {origin} to {destination} within budget of ${max_price}" if max_price else f"No flights found from {origin} to {destination}",
            "suggestion": "Consider train or car rental as an alternative"
        }

    # Select best option (cheapest)
    best_flight = min(flight_options, key=lambda x: x["price"])
    alternatives = [f for f in flight_options if f != best_flight][:2]

    return {
        "status": "success",
        "transport_type": "flight",
        "origin": origin,
        "destination": destination,
        "date": date,
        "selected_option": best_flight,
        "alternatives": alternatives
    }


@tool(args_schema=TrainSearchInput)
def search_trains(
    origin: str,
    destination: str,
    date: str,
    time_preference: str = "flexible",
    max_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Search for available train routes between two cities.
    Using hardcoded data for demonstration.

    Args:
        origin: Station name or code
        destination: Station name or code
        date: Travel date in YYYY-MM-DD format
        time_preference: Time preference (early morning, afternoon, evening, flexible)
        max_price: Maximum price in USD

    Returns:
        Dict with train options or error information
    """
    # Hardcoded train options for demonstration
    train_options = [
        {
            "operator": "Express Rail",
            "train_number": "ER101",
            "departure_time": "07:00 AM",
            "arrival_time": "01:30 PM",
            "price": 180.00,
            "duration": "6h 30m",
            "class": "First Class",
            "type": "early morning"
        },
        {
            "operator": "Express Rail",
            "train_number": "ER205",
            "departure_time": "02:00 PM",
            "arrival_time": "08:15 PM",
            "price": 150.00,
            "duration": "6h 15m",
            "class": "Standard",
            "type": "afternoon"
        },
        {
            "operator": "Night Express",
            "train_number": "NE301",
            "departure_time": "10:30 PM",
            "arrival_time": "06:00 AM",
            "price": 120.00,
            "duration": "7h 30m",
            "class": "Sleeper",
            "type": "evening"
        },
        {
            "operator": "Regional Rail",
            "train_number": "RR450",
            "departure_time": "11:00 AM",
            "arrival_time": "06:30 PM",
            "price": 95.00,
            "duration": "7h 30m",
            "class": "Economy",
            "type": "flexible"
        }
    ]

    # Filter by time preference
    if time_preference != "flexible":
        filtered_trains = [t for t in train_options if t["type"] == time_preference or t["type"] == "flexible"]
        if filtered_trains:
            train_options = filtered_trains

    # Filter by max price
    if max_price:
        train_options = [t for t in train_options if t["price"] <= max_price]

    if not train_options:
        return {
            "status": "error",
            "error_type": "OUT_OF_BUDGET" if max_price else "NO_RESULTS",
            "message": f"No trains found from {origin} to {destination} within budget of ${max_price}" if max_price else f"No trains found from {origin} to {destination}",
            "suggestion": "Consider car rental as an alternative"
        }

    # Select best option (cheapest)
    best_train = min(train_options, key=lambda x: x["price"])
    alternatives = [t for t in train_options if t != best_train][:2]

    return {
        "status": "success",
        "transport_type": "train",
        "origin": origin,
        "destination": destination,
        "date": date,
        "selected_option": best_train,
        "alternatives": alternatives
    }


@tool(args_schema=CarRentalSearchInput)
def search_car_rentals(
    location: str,
    start_date: str,
    end_date: str,
    car_type: str = "economy",
    max_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Search for car rental options.
    Using hardcoded data for demonstration.

    Args:
        location: Pickup location
        start_date: Rental start date in YYYY-MM-DD format
        end_date: Rental end date in YYYY-MM-DD format
        car_type: Car category (economy, compact, suv, luxury)
        max_price: Maximum total price in USD

    Returns:
        Dict with car rental options or error information
    """
    # Hardcoded car rental options for demonstration
    car_options = [
        {
            "company": "Enterprise",
            "car_model": "Toyota Corolla",
            "car_type": "economy",
            "price_per_day": 45.00,
            "total_price": 135.00,  # 3 days
            "features": ["Automatic", "Air Conditioning", "Bluetooth"]
        },
        {
            "company": "Hertz",
            "car_model": "Honda Civic",
            "car_type": "compact",
            "price_per_day": 55.00,
            "total_price": 165.00,  # 3 days
            "features": ["Automatic", "Air Conditioning", "GPS", "Bluetooth"]
        },
        {
            "company": "Budget",
            "car_model": "Ford Escape",
            "car_type": "suv",
            "price_per_day": 75.00,
            "total_price": 225.00,  # 3 days
            "features": ["Automatic", "Air Conditioning", "GPS", "4WD"]
        },
        {
            "company": "Avis",
            "car_model": "BMW 3 Series",
            "car_type": "luxury",
            "price_per_day": 120.00,
            "total_price": 360.00,  # 3 days
            "features": ["Automatic", "Premium Sound", "GPS", "Leather Seats"]
        }
    ]

    # Filter by car type
    if car_type:
        car_options = [c for c in car_options if c["car_type"] == car_type.lower()]

    # Filter by max price
    if max_price:
        car_options = [c for c in car_options if c["total_price"] <= max_price]

    if not car_options:
        return {
            "status": "error",
            "error_type": "OUT_OF_BUDGET" if max_price else "NO_RESULTS",
            "message": f"No car rentals found in {location} within budget of ${max_price}" if max_price else f"No car rentals found in {location}",
            "suggestion": "Consider a different car type or increase budget"
        }

    # Select best option (cheapest)
    best_car = min(car_options, key=lambda x: x["total_price"])
    alternatives = [c for c in car_options if c != best_car][:2]

    return {
        "status": "success",
        "transport_type": "car_rental",
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "selected_option": best_car,
        "alternatives": alternatives
    }


@tool(args_schema=HotelSearchInput)
def search_hotels(
    location: str,
    check_in: str,
    check_out: str,
    hotel_type: str,
    max_price_per_night: Optional[float] = None
) -> Dict[str, Any]:
    """
    Search for hotels in a city.
    Using hardcoded data for demonstration.

    Args:
        location: City or location name
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        hotel_type: Hotel category (5-star, 4-star, 3-star, hostel, boutique, budget)
        max_price_per_night: Maximum price per night in USD

    Returns:
        Dict with hotel options or error information
    """
    # Hardcoded hotel options for demonstration
    hotel_options = {
        "budget": [
            {"name": "Budget Inn Boston", "price_per_night": 65.00, "rating": 3.5, "amenities": ["WiFi", "Breakfast"]},
            {"name": "Economy Lodge", "price_per_night": 75.00, "rating": 3.8, "amenities": ["WiFi", "Parking"]},
            {"name": "Traveler's Rest", "price_per_night": 55.00, "rating": 3.2, "amenities": ["WiFi"]},
        ],
        "3-star": [
            {"name": "Comfort Hotel Boston", "price_per_night": 120.00, "rating": 4.0, "amenities": ["WiFi", "Gym", "Breakfast"]},
            {"name": "City Center Inn", "price_per_night": 135.00, "rating": 4.2, "amenities": ["WiFi", "Pool", "Parking"]},
        ],
        "4-star": [
            {"name": "Grand Boston Hotel", "price_per_night": 220.00, "rating": 4.5, "amenities": ["WiFi", "Gym", "Pool", "Restaurant"]},
            {"name": "Executive Suites", "price_per_night": 250.00, "rating": 4.6, "amenities": ["WiFi", "Spa", "Concierge"]},
        ],
        "5-star": [
            {"name": "Luxury Palace Boston", "price_per_night": 450.00, "rating": 4.9, "amenities": ["WiFi", "Spa", "Fine Dining", "Concierge"]},
        ],
        "hostel": [
            {"name": "Backpackers Hostel", "price_per_night": 35.00, "rating": 3.0, "amenities": ["WiFi", "Shared Kitchen"]},
        ],
        "boutique": [
            {"name": "Artisan Boutique Hotel", "price_per_night": 180.00, "rating": 4.4, "amenities": ["WiFi", "Art Gallery", "Breakfast"]},
        ]
    }

    # Get hotels for the requested type
    available_hotels = hotel_options.get(hotel_type, hotel_options["budget"])

    # Filter by max price if specified
    if max_price_per_night:
        available_hotels = [h for h in available_hotels if h["price_per_night"] <= max_price_per_night]

    if not available_hotels:
        return {
            "status": "error",
            "error_type": "OUT_OF_BUDGET",
            "message": f"No {hotel_type} hotels found in {location} within ${max_price_per_night} per night",
            "suggestion": "Consider increasing budget or choosing a different hotel type"
        }

    # Select best option (cheapest with good rating)
    best_hotel = min(available_hotels, key=lambda x: x["price_per_night"])
    alternatives = [h for h in available_hotels if h != best_hotel][:2]

    return {
        "status": "success",
        "location": location,
        "check_in": check_in,
        "check_out": check_out,
        "hotel_type": hotel_type,
        "selected_option": best_hotel,
        "alternatives": alternatives
    }


# Export all tools
ALL_TOOLS = [search_flights, search_trains, search_car_rentals, search_hotels]

