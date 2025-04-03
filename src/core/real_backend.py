from typing import Dict, Any, List, Optional
import aiohttp
import os
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
        self.base_url = os.getenv("CRUISE_API_BASE_URL", "https://api.cruise.com/v1")
        self.api_key = os.getenv("CRUISE_API_KEY")
        if not self.api_key:
            raise ValueError("CRUISE_API_KEY environment variable is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an HTTP request to the Cruise API."""
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