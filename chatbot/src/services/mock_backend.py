from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.interfaces.backend import BackendInterface

class MockBackend(BackendInterface):
    """Mock implementation of the backend interface for testing."""
    
    def __init__(self):
        self._users = {}
        self._bookings = {}
        self._vehicles = []
        self._initialize_mock_data()
        self.notification_tokens = {
            "test_user": "mock_device_token_123",
            "john_doe": "mock_device_token_456",
            "zeyad": "mock_device_token_789"
        }
    
    def _initialize_mock_data(self):
        # Initialize mock users
        self._users = {
            "user1": {
                "id": "user1",
                "name": "John Doe",
                "email": "john@example.com",
                "preferences": {
                    "language": "en",
                    "payment_method": "credit_card",
                    "favorite_locations": ["home", "work"]
                }
            },
            "user2": {
                "id": "user2",
                "name": "Jane Smith",
                "email": "jane@example.com",
                "preferences": {
                    "language": "ar",
                    "payment_method": "wallet",
                    "favorite_locations": ["university", "gym"]
                }
            }
        }
        
        # Initialize mock vehicles
        self._vehicles = [
            {
                "id": "v1",
                "type": "sedan",
                "location": {"lat": 25.2048, "lng": 55.2708},
                "available": True
            },
            {
                "id": "v2",
                "type": "suv",
                "location": {"lat": 25.2048, "lng": 55.2708},
                "available": True
            }
        ]
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        return self._users.get(user_id, {})
    
    async def get_ride_history(self, user_id: str) -> List[Dict[str, Any]]:
        # Generate mock ride history
        return [
            {
                "id": f"ride_{i}",
                "user_id": user_id,
                "pickup": {"lat": 25.2048, "lng": 55.2708},
                "dropoff": {"lat": 25.2048, "lng": 55.2708},
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "status": "completed"
            }
            for i in range(5)
        ]
    
    async def create_booking(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        booking_id = f"booking_{len(self._bookings) + 1}"
        booking = {
            "id": booking_id,
            **booking_details,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self._bookings[booking_id] = booking
        return booking
    
    async def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        if booking_id in self._bookings:
            self._bookings[booking_id]["status"] = "cancelled"
            return self._bookings[booking_id]
        return {"error": "Booking not found"}
    
    async def get_available_vehicles(self, location: Dict[str, float]) -> List[Dict[str, Any]]:
        return self._vehicles
    
    async def get_carpool_matches(self, user_id: str) -> List[Dict[str, Any]]:
        # Generate mock carpool matches
        return [
            {
                "id": f"match_{i}",
                "user_id": f"user_{i}",
                "route": {
                    "start": {"lat": 25.2048, "lng": 55.2708},
                    "end": {"lat": 25.2048, "lng": 55.2708}
                },
                "time": (datetime.now() + timedelta(hours=i)).isoformat()
            }
            for i in range(3)
        ]
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        if user_id in self._users:
            self._users[user_id]["preferences"].update(preferences)
            return self._users[user_id]
        return {"error": "User not found"}

    async def escalate_to_human(self, user_id: str, message: str, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of human escalation."""
        ticket_id = f"ticket_{len(self._bookings) + 1}"
        ticket = {
            "id": ticket_id,
            "user_id": user_id,
            "message": message,
            "sentiment": sentiment,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self._bookings[ticket_id] = ticket
        return ticket

    async def get_user_notification_token(self, user_id: str) -> Optional[str]:
        """Get mock notification token."""
        return self.notification_tokens.get(user_id) 