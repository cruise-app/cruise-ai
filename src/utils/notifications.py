from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta
import aiohttp
from ..core.interfaces.backend import BackendInterface

class NotificationService:
    def __init__(self, backend: BackendInterface):
        self.backend = backend
        self.monitored_bookings: Dict[str, asyncio.Task] = {}
    
    async def send_notification(self, user_id: str, title: str, body: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a notification to a user."""
        try:
            # Get user's notification token
            token = await self.backend.get_user_notification_token(user_id)
            if not token:
                return {"status": "error", "message": "No notification token found for user"}
            
            # TODO: Implement actual notification sending
            # For now, just print the notification
            print(f"Notification for user {user_id}:")
            print(f"Title: {title}")
            print(f"Body: {body}")
            print(f"Data: {data}")
            
            return {"status": "success", "message": "Notification sent"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def start_monitoring(self, booking_id: str):
        """Start monitoring a booking for updates."""
        if booking_id in self.monitored_bookings:
            return
        
        # Create monitoring task
        task = asyncio.create_task(self._monitor_booking(booking_id))
        self.monitored_bookings[booking_id] = task
    
    async def stop_monitoring(self, booking_id: str):
        """Stop monitoring a booking."""
        if booking_id in self.monitored_bookings:
            task = self.monitored_bookings[booking_id]
            task.cancel()
            del self.monitored_bookings[booking_id]
    
    async def _monitor_booking(self, booking_id: str):
        """Monitor a booking for updates and send notifications."""
        try:
            while True:
                # Get booking status from Cruise's system
                booking_status = await self._get_booking_status(booking_id)
                
                if booking_status["status"] == "completed":
                    await self._send_notification(
                        booking_id,
                        "Your ride has been completed. Thank you for choosing Cruise!"
                    )
                    break
                
                # Check for delays
                if booking_status["status"] == "in_progress":
                    current_eta = booking_status["current_eta"]
                    original_eta = booking_status["original_eta"]
                    
                    if current_eta > original_eta + timedelta(minutes=5):
                        await self._send_notification(
                            booking_id,
                            f"Your driver is running about {int((current_eta - original_eta).total_seconds() / 60)} minutes late. "
                            "We apologize for the inconvenience."
                        )
                
                # Check for nearby arrival
                if booking_status["status"] == "driver_assigned":
                    if booking_status["distance_to_pickup"] < 100:  # 100 meters
                        await self._send_notification(
                            booking_id,
                            "Your driver is about to arrive. Please be ready at the pickup location."
                        )
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            # Handle task cancellation
            pass
        except Exception as e:
            # Log error and stop monitoring
            print(f"Error monitoring booking {booking_id}: {str(e)}")
            await self.stop_monitoring(booking_id)
    
    async def _get_booking_status(self, booking_id: str) -> Dict[str, Any]:
        """Get current booking status from Cruise's system."""
        # TODO: Implement actual Cruise API integration
        # This is a mock implementation
        return {
            "status": "in_progress",
            "current_eta": datetime.now() + timedelta(minutes=15),
            "original_eta": datetime.now() + timedelta(minutes=10),
            "distance_to_pickup": 500,  # meters
            "driver_location": {
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        }
    
    async def _send_notification(self, booking_id: str, message: str):
        """Send notification to the user."""
        # TODO: Implement actual notification system (push notifications, SMS, etc.)
        # This is a mock implementation
        print(f"Notification for booking {booking_id}: {message}")
        
        # Example: Send push notification
        # await self._send_push_notification(booking_id, message)
        
        # Example: Send SMS
        # await self._send_sms(booking_id, message)
    
    async def _send_push_notification(self, booking_id: str, message: str):
        """Send push notification to the user's device."""
        # TODO: Implement push notification service
        pass
    
    async def _send_sms(self, booking_id: str, message: str):
        """Send SMS to the user's phone."""
        # TODO: Implement SMS service
        pass 