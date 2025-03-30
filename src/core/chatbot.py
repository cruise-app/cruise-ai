from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from transformers import pipeline
from ..interfaces.chatbot import ChatbotInterface
from ..interfaces.backend import BackendInterface

class CruiseChatbot(ChatbotInterface):
    """Implementation of the Cruise chatbot using a simple state machine pattern."""
    
    def __init__(self, backend: BackendInterface, openai_api_key: str):
        self.backend = backend
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
    
    async def process_message(self, message: str, user_id: str, language: str = "en") -> str:
        """Process a user message and return a response."""
        # Analyze sentiment
        sentiment = await self.analyze_sentiment(message)
        print(f"Processing message with sentiment: {sentiment}")  # Debug log
        
        # Check for negative sentiment and escalate if needed
        if sentiment["label"] == "NEGATIVE" and sentiment["score"] > 0.5:
            print(f"Escalating due to negative sentiment: {sentiment}")  # Debug log
            # Escalate to human support
            await self.backend.escalate_to_human(user_id, message, sentiment)
            return "I understand you're feeling frustrated. I'm escalating this to our support team who will assist you shortly."
        
        # Determine intent
        intent = self._determine_intent(message.lower())
        print(f"Determined intent: {intent}")  # Debug log
        
        # Process based on intent
        if intent == "booking":
            response = await self._handle_booking(message, user_id)
        elif intent == "cancellation":
            response = await self._handle_cancellation(message, user_id)
        elif intent == "recommendations":
            response = await self._handle_recommendations(user_id)
        elif intent == "safety":
            response = await self._handle_safety_check(user_id)
        elif intent == "carpool":
            response = await self._handle_carpool(user_id)
        else:
            response = "I understand your message. How can I help you today?"
        
        # Update memory
        self.memory.chat_memory.add_user_message(message)
        self.memory.chat_memory.add_ai_message(response)
        
        return response
    
    def _determine_intent(self, message: str) -> str:
        """Determine the intent of the user's message."""
        if "book" in message or "ride" in message:
            return "booking"
        elif "cancel" in message:
            return "cancellation"
        elif "recommend" in message or "suggest" in message:
            return "recommendations"
        elif "safety" in message or "check" in message:
            return "safety"
        elif "carpool" in message or "share" in message:
            return "carpool"
        return "unknown"
    
    async def _handle_booking(self, message: str, user_id: str) -> str:
        """Handle ride booking requests."""
        # Extract booking details from message
        # This is a simple implementation - in production, you'd want more robust parsing
        if "pickup" in message.lower() and "dropoff" in message.lower():
            # Create booking
            booking = await self.book_ride(user_id, {
                "pickup": "extracted_pickup",
                "dropoff": "extracted_dropoff"
            })
            return f"Great! I've booked your ride. Your booking ID is {booking['id']}."
        else:
            return "I can help you book a ride. Please provide your pickup and dropoff locations."
    
    async def _handle_cancellation(self, message: str, user_id: str) -> str:
        """Handle ride cancellation requests."""
        # Extract booking ID from message
        # This is a simple implementation - in production, you'd want more robust parsing
        if "id" in message.lower():
            # Cancel booking
            result = await self.cancel_ride(user_id, "extracted_booking_id")
            return "I've cancelled your ride. Is there anything else I can help you with?"
        else:
            return "I can help you cancel your ride. Please provide your booking ID."
    
    async def _handle_recommendations(self, user_id: str) -> str:
        """Handle recommendation requests."""
        recommendations = await self.get_recommendations(user_id)
        if recommendations:
            return f"Based on your history, I recommend: {recommendations[0]['content']}"
        else:
            return "I don't have any specific recommendations at the moment. Would you like to book a ride?"
    
    async def _handle_safety_check(self, user_id: str) -> str:
        """Handle safety check requests."""
        safety_result = await self.perform_safety_check(user_id)
        return f"Safety check completed. Recommendations: {safety_result['recommendations']}"
    
    async def _handle_carpool(self, user_id: str) -> str:
        """Handle carpool requests."""
        opportunities = await self.get_carpool_opportunities(user_id)
        if opportunities:
            return f"I found {len(opportunities)} carpool opportunities for your route."
        else:
            return "I don't see any carpool opportunities at the moment. Would you like to book a regular ride?"
    
    async def book_ride(self, user_id: str, ride_details: Dict[str, Any]) -> Dict[str, Any]:
        """Book a ride for the user."""
        return await self.backend.create_booking({
            "user_id": user_id,
            **ride_details
        })
    
    async def cancel_ride(self, user_id: str, ride_id: str) -> Dict[str, Any]:
        """Cancel a booked ride."""
        return await self.backend.cancel_booking(ride_id)
    
    async def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized recommendations for the user."""
        user_profile = await self.backend.get_user_profile(user_id)
        ride_history = await self.backend.get_ride_history(user_id)
        
        # Create recommendation prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that provides personalized ride recommendations."),
            ("user", "Based on the user profile and ride history, provide recommendations.")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(
            user_profile=user_profile,
            ride_history=ride_history
        )
        
        return [{"type": "recommendation", "content": response}]
    
    async def analyze_sentiment(self, message: str) -> Dict[str, float]:
        """Analyze the sentiment of a message."""
        result = self.sentiment_analyzer(message)[0]
        print(f"Sentiment analysis result for '{message}': {result}")  # Debug log
        
        # Convert 5-star rating to binary sentiment
        rating = int(result["label"].split()[0])  # Extract the number from "X stars"
        is_negative = rating <= 2  # 1-2 stars are considered negative
        
        return {
            "label": "NEGATIVE" if is_negative else "POSITIVE",
            "score": result["score"]
        }
    
    async def perform_safety_check(self, user_id: str) -> Dict[str, Any]:
        """Perform proactive safety checks for the user."""
        user_profile = await self.backend.get_user_profile(user_id)
        ride_history = await self.backend.get_ride_history(user_id)
        
        # Create safety check prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a safety-focused assistant that performs proactive safety checks."),
            ("user", "Based on the user profile and ride history, perform safety checks.")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(
            user_profile=user_profile,
            ride_history=ride_history
        )
        
        return {
            "status": "completed",
            "recommendations": response
        }
    
    async def get_carpool_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get carpool opportunities based on user history."""
        return await self.backend.get_carpool_matches(user_id) 