from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BackendInterface(ABC):
    """Interface for communicating with Cruise's backend."""
    
    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        pass
    
    @abstractmethod
    async def get_ride_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's ride history."""
        pass
    
    @abstractmethod
    async def create_booking(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking."""
        pass
    
    @abstractmethod
    async def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel an existing booking."""
        pass
    
    @abstractmethod
    async def get_available_vehicles(self, location: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get available vehicles in a location."""
        pass
    
    @abstractmethod
    async def get_carpool_matches(self, user_id: str) -> List[Dict[str, Any]]:
        """Get potential carpool matches for a user."""
        pass
    
    @abstractmethod
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences."""
        pass

    @abstractmethod
    async def escalate_to_human(self, user_id: str, message: str, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate a conversation to human support."""
        pass 