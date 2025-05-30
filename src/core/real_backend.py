from typing import Dict, Any, List, Optional
import aiohttp
import os
import uuid
import json
from dotenv import load_dotenv
from ..interfaces.backend import BackendInterface
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RealBackend(BackendInterface):
    """Real backend implementation for Cruise integration."""
    
    def __init__(self):
        # Using localhost for development to avoid external API calls
        self.base_url = os.getenv("CRUISE_API_BASE_URL", "http://localhost:8001/mock-api/v1")
        self.api_key = os.getenv("CRUISE_API_KEY", "development_key")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # For development, use mock data
        self.use_mock = True
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an HTTP request to the Cruise API."""
        if self.use_mock:
            logger.info(f"Using mock data for {method} request to {endpoint}")
            return await self._get_mock_data(endpoint, kwargs)
            
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/{endpoint}"
            try:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise ValueError("Invalid API key")
                    elif response.status == 404:
                        raise ValueError("Resource not found")
                    else:
                        error_text = await response.text()
                        raise ValueError(f"API request failed: {error_text}")
            except aiohttp.ClientError as e:
                logger.error(f"Network error: {str(e)}")
                raise
    
    async def _get_mock_data(self, endpoint: str, request_data: Dict[str, Any]) -> Any:
        """Return mock data for development purposes."""
        if endpoint.startswith("users/") and endpoint.endswith("/rides"):
            return self._mock_ride_history()
        elif endpoint.startswith("users/") and endpoint.endswith("/carpool-matches"):
            return self._mock_carpool_matches()
        elif endpoint.startswith("users/"):
            return self._mock_user_profile()
        elif endpoint == "bookings":
            return self._mock_create_booking(request_data.get("json", {}))
        elif endpoint.startswith("bookings/") and endpoint.endswith("/cancel"):
            return self._mock_cancel_booking()
        elif endpoint == "vehicles/available":
            return self._mock_available_vehicles()
        elif endpoint == "support/escalate":
            return self._mock_escalate_to_human(request_data.get("json", {}))
        else:
            logger.warning(f"No mock data available for endpoint: {endpoint}")
            return {}
    
    def _mock_user_profile(self) -> Dict[str, Any]:
        """Return mock user profile data."""
        return {
            "id": "user_1234",
            "name": "Zeyad Tamer",
            "email": "zeyad@example.com",
            "phone": "+1234567890",
            "preferences": {
                "language": "en",
                "payment_method": "credit_card",
                "car_type": "standard"
            },
            "membership": {
                "level": "gold",
                "since": "2023-01-15",
                "points": 450
            }
        }
    
    def _mock_ride_history(self) -> List[Dict[str, Any]]:
        """Return mock ride history data."""
        return [
            {
                "id": "ride_6789",
                "pickup": "Downtown Station",
                "dropoff": "Airport Terminal 1",
                "date": "2023-06-15T14:30:00Z",
                "status": "completed",
                "fare": 25.50,
                "car_type": "standard"
            },
            {
                "id": "ride_5678",
                "pickup": "Home",
                "dropoff": "Office",
                "date": "2023-06-10T08:15:00Z",
                "status": "completed",
                "fare": 15.75,
                "car_type": "comfort"
            },
            {
                "id": "ride_4567",
                "pickup": "Shopping Mall",
                "dropoff": "Home",
                "date": "2023-06-05T18:45:00Z",
                "status": "completed",
                "fare": 18.25,
                "car_type": "standard"
            }
        ]
    
    def _mock_create_booking(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Return mock booking creation data."""
        booking_id = f"booking_{uuid.uuid4().hex[:6]}"
        return {
            "id": booking_id,
            "status": "confirmed",
            "pickup": booking_details.get("pickup", "Default Pickup"),
            "dropoff": booking_details.get("dropoff", "Default Dropoff"),
            "estimated_arrival": "2023-06-30T15:45:00Z",
            "driver": {
                "name": "John Driver",
                "rating": 4.8,
                "car": "Toyota Camry",
                "plate": "ABC123"
            },
            "fare": {
                "amount": 24.50,
                "currency": "USD"
            }
        }
    
    def _mock_cancel_booking(self) -> Dict[str, Any]:
        """Return mock booking cancellation data."""
        return {
            "id": "booking_abcdef",
            "status": "cancelled",
            "cancellation_fee": 0,
            "refund_amount": 24.50
        }
    
    def _mock_available_vehicles(self) -> List[Dict[str, Any]]:
        """Return mock available vehicles data."""
        return [
            {
                "id": "vehicle_123",
                "type": "standard",
                "model": "Toyota Camry",
                "eta_minutes": 5,
                "fare": 24.50
            },
            {
                "id": "vehicle_456",
                "type": "comfort",
                "model": "Honda Accord",
                "eta_minutes": 7,
                "fare": 32.75
            },
            {
                "id": "vehicle_789",
                "type": "luxury",
                "model": "Mercedes S-Class",
                "eta_minutes": 12,
                "fare": 45.00
            }
        ]
    
    def _mock_carpool_matches(self) -> List[Dict[str, Any]]:
        """Return mock carpool matches data."""
        return [
            {
                "id": "carpool_123",
                "driver": "John Doe",
                "pickup": "Downtown Station",
                "dropoff": "Airport Terminal 1",
                "time": "2023-06-30T15:45:00Z",
                "seats": 2,
                "price": 15.0
            }
        ]
    
    def _mock_escalate_to_human(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return mock escalation response."""
        return {
            "status": "escalated",
            "ticket_id": f"ticket_{uuid.uuid4().hex[:6]}",
            "estimated_response_time": "5 minutes"
        }
    
    # Backend interface implementations
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information from Cruise."""
        return await self._make_request("GET", f"users/{user_id}")
    
    async def get_ride_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's ride history from Cruise."""
        return await self._make_request("GET", f"users/{user_id}/rides")
    
    async def create_booking(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking in Cruise."""
        return await self._make_request("POST", "bookings", json=booking_details)
    
    async def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel an existing booking in Cruise."""
        return await self._make_request("POST", f"bookings/{booking_id}/cancel")
    
    async def get_available_vehicles(self, location: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get available vehicles in a location from Cruise."""
        return await self._make_request("GET", "vehicles/available", params=location)
    
    async def get_carpool_matches(self, user_id: str) -> List[Dict[str, Any]]:
        """Get potential carpool matches for a user from Cruise."""
        return await self._make_request("GET", f"users/{user_id}/carpool-matches")
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences in Cruise."""
        return await self._make_request("PATCH", f"users/{user_id}/preferences", json=preferences)
    
    async def escalate_to_human(self, user_id: str, message: str, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate a conversation to human support in Cruise."""
        payload = {
            "user_id": user_id,
            "message": message,
            "sentiment": sentiment
        }
        return await self._make_request("POST", "support/escalate", json=payload) 