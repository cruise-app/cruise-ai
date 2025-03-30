from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class ChatbotInterface(ABC):
    """Base interface for the Cruise chatbot."""
    
    @abstractmethod
    async def process_message(self, message: str, user_id: str, language: str = "en") -> str:
        """Process a user message and return a response."""
        pass
    
    @abstractmethod
    async def book_ride(self, user_id: str, ride_details: Dict[str, Any]) -> Dict[str, Any]:
        """Book a ride for the user."""
        pass
    
    @abstractmethod
    async def cancel_ride(self, user_id: str, ride_id: str) -> Dict[str, Any]:
        """Cancel a booked ride."""
        pass
    
    @abstractmethod
    async def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized recommendations for the user."""
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, message: str) -> Dict[str, float]:
        """Analyze the sentiment of a message."""
        pass
    
    @abstractmethod
    async def perform_safety_check(self, user_id: str) -> Dict[str, Any]:
        """Perform proactive safety checks for the user."""
        pass
    
    @abstractmethod
    async def get_carpool_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get carpool opportunities based on user history."""
        pass 