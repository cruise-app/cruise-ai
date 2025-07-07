import os
import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    cred_path = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_path:
        raise ValueError("FIREBASE_CREDENTIALS environment variable not set")
    
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
    
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

async def send_push_notification(token: str, title: str, body: str, data: dict = None):
    """Send a push notification to a specific device."""
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=token
        )
        response = messaging.send(message)
        return {"success": True, "message_id": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def send_multicast_notification(tokens: list, title: str, body: str, data: dict = None):
    """Send push notifications to multiple devices."""
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            tokens=tokens
        )
        response = messaging.send_multicast(message)
        return {
            "success": True,
            "success_count": response.success_count,
            "failure_count": response.failure_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)} 