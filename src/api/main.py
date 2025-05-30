from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
import logging
import traceback
from ..core.chatbot import CruiseChatbot
from ..core.real_backend import RealBackend
from ..utils.notifications import NotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Cruise AI Customer Support",
    description="AI-powered customer support chatbot for Cruise",
    version="1.0.0"
)

# Add CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Initialize dependencies
def get_chatbot():
    try:
        backend = RealBackend()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        return CruiseChatbot(backend, openai_api_key)
    except Exception as e:
        logger.error(f"Error initializing chatbot: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to initialize chatbot: {str(e)}")

# Pydantic models
class Message(BaseModel):
    message: str
    user_id: str
    language: str = "en"

class RideDetails(BaseModel):
    pickup: Dict[str, Any]
    dropoff: Dict[str, Any]
    vehicle_type: Optional[str] = None
    scheduled_time: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    details: Dict[str, Any]

# Add new Pydantic model for notification request
class NotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None

# API endpoints
@app.get("/")
async def root():
    """Root endpoint to verify the API is running."""
    return {"status": "ok", "message": "Cruise AI Customer Support API is running"}

@app.post("/chat")
async def chat(
    message: Message,
    chatbot: CruiseChatbot = Depends(get_chatbot)
) -> Dict[str, str]:
    """Process a chat message and return a response."""
    try:
        logger.info(f"Processing chat message for user {message.user_id}")
        
        # Auto-detect Arabic if not specified
        language = message.language
        if language == "en" and any('\u0600' <= c <= '\u06FF' for c in message.message):
            language = "ar"
            logger.info(f"API detected Arabic language in message")
        
        response = await chatbot.process_message(
            message.message,
            message.user_id,
            language
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return error in appropriate language
        if any('\u0600' <= c <= '\u06FF' for c in message.message):
            error_msg = "عذراً، حدث خطأ أثناء معالجة رسالتك. يرجى المحاولة مرة أخرى."
        else:
            error_msg = f"Sorry, an error occurred: {str(e)}"
            
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/book-ride")
async def book_ride(
    ride_details: RideDetails,
    user_id: str,
    chatbot: CruiseChatbot = Depends(get_chatbot)
) -> BookingResponse:
    """Book a new ride."""
    try:
        logger.info(f"Booking ride for user {user_id}")
        booking = await chatbot.book_ride(user_id, ride_details.dict())
        return BookingResponse(
            booking_id=booking["id"],
            status=booking["status"],
            details=booking
        )
    except Exception as e:
        logger.error(f"Error booking ride: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel-ride/{ride_id}")
async def cancel_ride(
    ride_id: str,
    user_id: str,
    chatbot: CruiseChatbot = Depends(get_chatbot)
) -> BookingResponse:
    """Cancel an existing ride."""
    try:
        logger.info(f"Canceling ride {ride_id} for user {user_id}")
        booking = await chatbot.cancel_ride(user_id, ride_id)
        return BookingResponse(
            booking_id=booking["id"],
            status=booking["status"],
            details=booking
        )
    except Exception as e:
        logger.error(f"Error canceling ride: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    chatbot: CruiseChatbot = Depends(get_chatbot)
) -> List[Dict[str, Any]]:
    """Get personalized recommendations for a user."""
    try:
        logger.info(f"Getting recommendations for user {user_id}")
        return await chatbot.get_recommendations(user_id)
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/safety-check/{user_id}")
async def safety_check(
    user_id: str,
    chatbot: CruiseChatbot = Depends(get_chatbot)
) -> Dict[str, Any]:
    """Perform safety checks for a user."""
    try:
        logger.info(f"Performing safety check for user {user_id}")
        return await chatbot.perform_safety_check(user_id)
    except Exception as e:
        logger.error(f"Error performing safety check: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/carpool-opportunities/{user_id}")
async def get_carpool_opportunities(
    user_id: str,
    chatbot: CruiseChatbot = Depends(get_chatbot)
) -> List[Dict[str, Any]]:
    """Get carpool opportunities for a user."""
    try:
        logger.info(f"Getting carpool opportunities for user {user_id}")
        return await chatbot.get_carpool_opportunities(user_id)
    except Exception as e:
        logger.error(f"Error getting carpool opportunities: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Add new endpoint for testing notifications
@app.post("/test-notification")
async def test_notification(
    request: NotificationRequest,
    notification_service: NotificationService = Depends(lambda: NotificationService(RealBackend()))
) -> Dict[str, Any]:
    """Test endpoint for sending notifications."""
    try:
        logger.info(f"Sending test notification to user {request.user_id}")
        result = await notification_service.send_notification(
            user_id=request.user_id,
            title=request.title,
            body=request.body,
            data=request.data
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the API is healthy."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 