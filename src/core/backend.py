from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
from ..core.interfaces.backend import BackendInterface
from ..utils.notifications import NotificationService
from ..utils.location import LocationService

class CruiseBackend(BackendInterface):
    def __init__(self, cruise_api_key: str):
        self.cruise_api_key = cruise_api_key
        self.notification_service = NotificationService()
        self.location_service = LocationService()
    
    async def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking with location validation."""
        # Validate and geocode locations
        pickup_location = await self.location_service.validate_and_geocode(booking_data["pickup"])
        dropoff_location = await self.location_service.validate_and_geocode(booking_data["dropoff"])
        
        # Calculate route and estimated time
        route = await self.location_service.calculate_route(pickup_location, dropoff_location)
        
        # Create booking in Cruise's system
        cruise_booking = await self._create_cruise_booking({
            **booking_data,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "estimated_duration": route["duration"],
            "distance": route["distance"]
        })
        
        # Set up monitoring for this booking
        await self._setup_booking_monitoring(cruise_booking["id"])
        
        return cruise_booking
    
    async def _create_cruise_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create booking in Cruise's system."""
        # TODO: Implement actual Cruise API integration
        # This is a mock implementation
        return {
            "id": f"CRUISE_{datetime.now().timestamp()}",
            "status": "confirmed",
            "pickup_time": booking_data.get("time", datetime.now().isoformat()),
            "pickup_location": booking_data["pickup_location"],
            "dropoff_location": booking_data["dropoff_location"],
            "estimated_duration": booking_data["estimated_duration"],
            "distance": booking_data["distance"]
        }
    
    async def _setup_booking_monitoring(self, booking_id: str):
        """Set up monitoring for a booking."""
        # Start monitoring driver location and ETA
        await self.notification_service.start_monitoring(booking_id)
    
    async def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a booking and notify relevant parties."""
        # Cancel in Cruise's system
        result = await self._cancel_cruise_booking(booking_id)
        
        # Stop monitoring
        await self.notification_service.stop_monitoring(booking_id)
        
        return result
    
    async def _cancel_cruise_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel booking in Cruise's system."""
        # TODO: Implement actual Cruise API integration
        return {"status": "cancelled", "booking_id": booking_id}
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile from Cruise's system."""
        # TODO: Implement actual Cruise API integration
        return {
            "id": user_id,
            "name": "John Doe",
            "preferences": {
                "language": "en",
                "notifications": True
            }
        }
    
    async def get_ride_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's ride history from Cruise's system."""
        # TODO: Implement actual Cruise API integration
        return []
    
    async def get_carpool_matches(self, user_id: str) -> List[Dict[str, Any]]:
        """Get potential carpool matches for a user."""
        # TODO: Implement actual carpool matching logic
        return []

    async def escalate_to_human(self, user_id: str, message: str, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate a conversation to human support."""
        # Create escalation ticket
        ticket = {
            "id": f"ESCALATION_{datetime.now().timestamp()}",
            "user_id": user_id,
            "message": message,
            "sentiment": sentiment,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Send notification to support team
        await self.notification_service.send_notification(
            "support_team",
            "New Escalation",
            f"User {user_id} needs support. Sentiment: {sentiment['label']} ({sentiment['score']:.2f})"
        )
        
        # Send notification to user
        await self.notification_service.send_notification(
            user_id,
            "Support Team Assigned",
            "Our support team has been notified and will assist you shortly."
        )
        
        return ticket 