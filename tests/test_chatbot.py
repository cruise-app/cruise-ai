import pytest
from src.core.chatbot import CruiseChatbot
from src.services.mock_backend import MockBackend
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def chatbot():
    backend = MockBackend()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return CruiseChatbot(backend, openai_api_key)

@pytest.mark.asyncio
async def test_process_message(chatbot):
    """Test basic message processing."""
    response = await chatbot.process_message(
        "Hello, I need a ride",
        "user1",
        "en"
    )
    assert response is not None
    assert isinstance(response, str)

@pytest.mark.asyncio
async def test_book_ride(chatbot):
    """Test ride booking functionality."""
    ride_details = {
        "pickup": {"lat": 25.2048, "lng": 55.2708},
        "dropoff": {"lat": 25.2048, "lng": 55.2708},
        "vehicle_type": "sedan"
    }
    booking = await chatbot.book_ride("user1", ride_details)
    assert booking is not None
    assert "id" in booking
    assert booking["status"] == "pending"

@pytest.mark.asyncio
async def test_cancel_ride(chatbot):
    """Test ride cancellation functionality."""
    # First book a ride
    ride_details = {
        "pickup": {"lat": 25.2048, "lng": 55.2708},
        "dropoff": {"lat": 25.2048, "lng": 55.2708},
        "vehicle_type": "sedan"
    }
    booking = await chatbot.book_ride("user1", ride_details)
    
    # Then cancel it
    cancellation = await chatbot.cancel_ride("user1", booking["id"])
    assert cancellation is not None
    assert cancellation["status"] == "cancelled"

@pytest.mark.asyncio
async def test_get_recommendations(chatbot):
    """Test recommendation generation."""
    recommendations = await chatbot.get_recommendations("user1")
    assert recommendations is not None
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

@pytest.mark.asyncio
async def test_analyze_sentiment(chatbot):
    """Test sentiment analysis."""
    sentiment = await chatbot.analyze_sentiment("I love the service!")
    assert sentiment is not None
    assert "label" in sentiment
    assert "score" in sentiment

@pytest.mark.asyncio
async def test_safety_check(chatbot):
    """Test safety check functionality."""
    safety_check = await chatbot.perform_safety_check("user1")
    assert safety_check is not None
    assert "status" in safety_check
    assert "recommendations" in safety_check

@pytest.mark.asyncio
async def test_carpool_opportunities(chatbot):
    """Test carpool opportunity suggestions."""
    opportunities = await chatbot.get_carpool_opportunities("user1")
    assert opportunities is not None
    assert isinstance(opportunities, list)
    assert len(opportunities) > 0

@pytest.mark.asyncio
async def test_multilingual_support(chatbot):
    """Test multilingual message processing."""
    response = await chatbot.process_message(
        "مرحبا، أحتاج إلى رحلة",
        "user2",
        "ar"
    )
    assert response is not None
    assert isinstance(response, str) 