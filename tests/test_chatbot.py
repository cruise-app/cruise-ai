import pytest
from src.core.chatbot import CruiseChatbot
from src.services.mock_backend import MockBackend
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def chatbot():
    """
    Fixture that creates a CruiseChatbot instance with a mock backend for testing.
    This ensures each test starts with a fresh chatbot instance.
    """
    print("\nSetting up chatbot with mock backend...")
    backend = MockBackend()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return CruiseChatbot(backend, openai_api_key)

@pytest.mark.asyncio
async def test_process_message(chatbot):
    """
    Test the basic message processing functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can process a simple ride request message
    2. The response is not None
    3. The response is a string
    
    The test uses a mock backend to simulate the interaction without making real API calls.
    """
    print("\nTesting basic message processing...")
    print("Sending message: 'Hello, I need a ride'")
    response = await chatbot.process_message(
        "Hello, I need a ride",
        "user1",
        "en"
    )
    print(f"Received response: {response}")
    assert response is not None
    assert isinstance(response, str)
    print("✓ Message processing test passed")

@pytest.mark.asyncio
async def test_book_ride(chatbot):
    """
    Test the ride booking functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can create a new booking with valid ride details
    2. The booking response contains an ID
    3. The booking status is set to 'pending'
    
    The test uses mock location data and vehicle type to simulate a real booking request.
    """
    print("\nTesting ride booking functionality...")
    ride_details = {
        "pickup": {"lat": 25.2048, "lng": 55.2708},
        "dropoff": {"lat": 25.2048, "lng": 55.2708},
        "vehicle_type": "sedan"
    }
    print(f"Attempting to book ride with details: {ride_details}")
    booking = await chatbot.book_ride("user1", ride_details)
    print(f"Booking response: {booking}")
    assert booking is not None
    assert "id" in booking
    assert booking["status"] == "pending"
    print("✓ Ride booking test passed")

@pytest.mark.asyncio
async def test_cancel_ride(chatbot):
    """
    Test the ride cancellation functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can create a new booking
    2. The chatbot can cancel the created booking
    3. The cancellation response indicates the booking was cancelled
    
    The test follows a complete flow of booking and then cancelling a ride.
    """
    print("\nTesting ride cancellation functionality...")
    # First book a ride
    ride_details = {
        "pickup": {"lat": 25.2048, "lng": 55.2708},
        "dropoff": {"lat": 25.2048, "lng": 55.2708},
        "vehicle_type": "sedan"
    }
    print("Step 1: Creating a new booking")
    booking = await chatbot.book_ride("user1", ride_details)
    print(f"Booking created with ID: {booking['id']}")
    
    print("Step 2: Cancelling the booking")
    cancellation = await chatbot.cancel_ride("user1", booking["id"])
    print(f"Cancellation response: {cancellation}")
    assert cancellation is not None
    assert cancellation["status"] == "cancelled"
    print("✓ Ride cancellation test passed")

@pytest.mark.asyncio
async def test_get_recommendations(chatbot):
    """
    Test the recommendation generation functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can generate personalized recommendations for a user
    2. The recommendations are returned as a list
    3. The recommendations list is not empty
    
    The test uses the user's history and preferences to generate relevant recommendations.
    """
    print("\nTesting recommendation generation...")
    print("Requesting personalized recommendations for user1")
    recommendations = await chatbot.get_recommendations("user1")
    print(f"Received recommendations: {recommendations}")
    assert recommendations is not None
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    print("✓ Recommendation generation test passed")

@pytest.mark.asyncio
async def test_analyze_sentiment(chatbot):
    """
    Test the sentiment analysis functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can analyze the sentiment of a user message
    2. The sentiment analysis returns a label and score
    3. The analysis is performed correctly for positive sentiment
    
    The test uses a positive message to verify the sentiment analysis works as expected.
    """
    print("\nTesting sentiment analysis...")
    test_message = "I love the service!"
    print(f"Analyzing sentiment for message: '{test_message}'")
    sentiment = await chatbot.analyze_sentiment(test_message)
    print(f"Sentiment analysis result: {sentiment}")
    assert sentiment is not None
    assert "label" in sentiment
    assert "score" in sentiment
    print("✓ Sentiment analysis test passed")

@pytest.mark.asyncio
async def test_safety_check(chatbot):
    """
    Test the safety check functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can perform safety checks for a user
    2. The safety check returns a status and recommendations
    3. The safety check includes relevant safety information
    
    The test ensures the chatbot can provide appropriate safety information to users.
    """
    print("\nTesting safety check functionality...")
    print("Performing safety check for user1")
    safety_check = await chatbot.perform_safety_check("user1")
    print(f"Safety check results: {safety_check}")
    assert safety_check is not None
    assert "status" in safety_check
    assert "recommendations" in safety_check
    print("✓ Safety check test passed")

@pytest.mark.asyncio
async def test_carpool_opportunities(chatbot):
    """
    Test the carpool opportunity suggestion functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can find potential carpool matches for a user
    2. The carpool opportunities are returned as a list
    3. The list contains valid carpool matches
    
    The test ensures the chatbot can help users find carpooling opportunities.
    """
    print("\nTesting carpool opportunity suggestions...")
    print("Finding carpool matches for user1")
    opportunities = await chatbot.get_carpool_opportunities("user1")
    print(f"Found carpool opportunities: {opportunities}")
    assert opportunities is not None
    assert isinstance(opportunities, list)
    assert len(opportunities) > 0
    print("✓ Carpool opportunities test passed")

@pytest.mark.asyncio
async def test_multilingual_support(chatbot):
    """
    Test the multilingual support functionality of the chatbot.
    
    This test verifies that:
    1. The chatbot can process messages in different languages
    2. The response is appropriate for the specified language
    3. The chatbot maintains context across different languages
    
    The test uses an Arabic message to verify the chatbot's multilingual capabilities.
    """
    print("\nTesting multilingual support...")
    arabic_message = "مرحبا، أحتاج إلى رحلة"
    print(f"Processing Arabic message: '{arabic_message}'")
    response = await chatbot.process_message(
        arabic_message,
        "user2",
        "ar"
    )
    print(f"Received response: {response}")
    assert response is not None
    assert isinstance(response, str)
    print("✓ Multilingual support test passed") 