from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ChatbotInterface(ABC):
    """Interface for the Cruise chatbot."""
    
    @abstractmethod
    async def process_message(self, message: str, user_id: str, language: str = "en") -> str:
        """Process a user message and return a response."""
        pass
    
    @abstractmethod
    async def book_ride(self, user_id: str, ride_details: Dict[str, Any]) -> Dict[str, Any]:
        """Book a new ride."""
        pass
    
    @abstractmethod
    async def cancel_ride(self, user_id: str, booking_id: str) -> Dict[str, Any]:
        """Cancel an existing ride."""
        pass
    
    @abstractmethod
    async def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user."""
        pass 