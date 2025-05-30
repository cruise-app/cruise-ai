from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from transformers import pipeline
from ..interfaces.chatbot import ChatbotInterface
from ..interfaces.backend import BackendInterface
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CruiseChatbot(ChatbotInterface):
    """Implementation of the Cruise chatbot using a simple state machine pattern."""
    
    def __init__(self, backend: BackendInterface, openai_api_key: str):
        self.backend = backend
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        self.memory = {}  # User ID to memory mapping
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
    
    def _get_user_memory(self, user_id: str) -> ConversationBufferMemory:
        """Get or create memory for a user."""
        if user_id not in self.memory:
            self.memory[user_id] = ConversationBufferMemory(
                memory_key="chat_history", 
                return_messages=True
            )
        return self.memory[user_id]
    
    async def process_message(self, message: str, user_id: str, language: str = "en") -> str:
        """Process a user message and return a response."""
        try:
            memory = self._get_user_memory(user_id)
            
            # Auto-detect language if not specified
            detected_language = language
            if language == "en" and any('\u0600' <= c <= '\u06FF' for c in message):
                detected_language = "ar"
                logger.info(f"Detected Arabic language in message")
            
            # Analyze sentiment
            sentiment = await self.analyze_sentiment(message)
            logger.info(f"Processing message with sentiment: {sentiment}")
            
            # Check for negative sentiment and escalate if needed
            if sentiment.get("label") == "NEGATIVE" and sentiment.get("score", 0) > 0.5:
                logger.info(f"Escalating due to negative sentiment: {sentiment}")
                # Escalate to human support
                try:
                    await self.backend.escalate_to_human(user_id, message, sentiment)
                    if detected_language == "ar":
                        return "أفهم أنك قد تشعر بالإحباط. سأقوم بتصعيد هذا الأمر إلى فريق الدعم لدينا الذي سيساعدك قريبًا. في غضون ذلك، هل هناك شيء محدد يمكنني مساعدتك به؟"
                    else:
                        return "I understand you're feeling frustrated. I'm escalating this to our support team who will assist you shortly. In the meantime, is there anything specific I can help you with?"
                except Exception as e:
                    logger.error(f"Error during escalation: {str(e)}")
                    if detected_language == "ar":
                        return "ألاحظ أنك تبدو منزعجًا. أود أن أوصلك بفريق الدعم لدينا، لكنني أواجه صعوبات تقنية. يرجى المحاولة مرة أخرى أو الاتصال بخط الدعم على 1-800-CRUISE-HELP للحصول على مساعدة فورية."
                    else:
                        return "I notice you seem upset. I'd like to connect you with our support team, but I'm having technical difficulties. Please try again or call our support line at 1-800-CRUISE-HELP for immediate assistance."
            
            # Determine intent
            intent = self._determine_intent(message.lower())
            logger.info(f"Determined intent: {intent}")
            
            # Process based on intent
            if intent == "booking":
                response = await self._handle_booking(message, user_id, detected_language)
            elif intent == "cancellation":
                response = await self._handle_cancellation(message, user_id, detected_language)
            elif intent == "recommendations":
                response = await self._handle_recommendations(user_id, detected_language)
            elif intent == "safety":
                response = await self._handle_safety_check(user_id, detected_language)
            elif intent == "carpool":
                response = await self._handle_carpool(user_id, detected_language)
            else:
                # Use LLM for general queries
                system_prompt = """You are Cruise's AI assistant for their ride-hailing app. Be helpful, concise, and friendly.
                Focus on helping users book rides, check ride status, find carpools, and other transportation needs.
                If you don't know something, be honest and suggest contacting customer support.
                Always prioritize customer safety and satisfaction.
                Respond to greetings in a warm, welcoming way.
                You MUST respond in the same language as the user's query.
                If the user writes in Arabic, you MUST respond in Arabic.
                If the user writes in English, respond in English."""
                
                chat_history = memory.chat_memory.messages if hasattr(memory, 'chat_memory') else []
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    *[(msg.type, msg.content) for msg in chat_history],
                    ("user", f"The user sent this message in {detected_language} language: {message}")
                ])
                
                chain = LLMChain(llm=self.llm, prompt=prompt)
                response = await chain.arun(language=detected_language)
            
            # Update memory
            memory.chat_memory.add_user_message(message)
            memory.chat_memory.add_ai_message(response)
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            if any('\u0600' <= c <= '\u06FF' for c in message):
                return "آسف، واجهت خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى أو الاتصال بفريق الدعم للحصول على المساعدة."
            else:
                return "I'm sorry, I encountered an error while processing your request. Please try again or contact our support team for assistance."
    
    def _determine_intent(self, message: str) -> str:
        """Determine the intent of the user's message using keywords and regex patterns."""
        # Define patterns for different intents
        booking_patterns = [
            r"\b(book|order|get|need|want|request|schedule)\s+.*\b(ride|car|taxi|vehicle|transportation)\b",
            r"\btake me to\b",
            r"\bpick me up\b",
            r"\bfrom\s+.+\s+to\s+.+\b"
        ]
        
        cancellation_patterns = [
            r"\b(cancel|stop|abort|terminate)\s+.*\b(ride|booking|trip|order)\b",
            r"\bi want to cancel\b",
            r"\bdon't need the ride\b"
        ]
        
        recommendation_patterns = [
            r"\b(recommend|suggest|advise|what should|propose)\b",
            r"\bwhat's good\b",
            r"\bwhat do you recommend\b"
        ]
        
        safety_patterns = [
            r"\b(safety|safe|security|secure)\b",
            r"\bcheck safety\b",
            r"\bhow safe\b"
        ]
        
        carpool_patterns = [
            r"\b(carpool|pool|share|car sharing|shared ride)\b",
            r"\bshare a ride\b",
            r"\bsplit the cost\b"
        ]
        
        # Check patterns for each intent
        for pattern in booking_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "booking"
        
        for pattern in cancellation_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "cancellation"
        
        for pattern in recommendation_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "recommendations"
        
        for pattern in safety_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "safety"
        
        for pattern in carpool_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return "carpool"
        
        return "unknown"
    
    async def _handle_booking(self, message: str, user_id: str, language: str) -> str:
        """Handle ride booking requests."""
        # Try to extract locations from the message
        locations = self._extract_locations(message)
        
        if locations.get("pickup") and locations.get("dropoff"):
            # We have both pickup and dropoff locations
            try:
                # Create booking
                booking = await self.book_ride(user_id, {
                    "pickup": {"name": locations["pickup"], "latitude": 0.0, "longitude": 0.0},
                    "dropoff": {"name": locations["dropoff"], "latitude": 0.0, "longitude": 0.0}
                })
                
                if language == "ar":
                    return f"رائع! لقد حجزت رحلتك من {locations['pickup']} إلى {locations['dropoff']}. رقم حجزك هو {booking['id']}. سيصل سائقك {booking['driver']['name']} بسيارة {booking['driver']['car']} (لوحة: {booking['driver']['plate']}) في غضون {booking.get('eta_minutes', '10-15')} دقيقة تقريبًا."
                else:
                    return f"Great! I've booked your ride from {locations['pickup']} to {locations['dropoff']}. Your booking ID is {booking['id']}. Your driver {booking['driver']['name']} will arrive in a {booking['driver']['car']} (plate: {booking['driver']['plate']}) in approximately {booking.get('eta_minutes', '10-15')} minutes."
            except Exception as e:
                logger.error(f"Error booking ride: {str(e)}")
                if language == "ar":
                    return f"لم أتمكن من إكمال حجزك بسبب مشكلة فنية. يرجى المحاولة مرة أخرى أو الاتصال بالدعم إذا استمرت المشكلة."
                else:
                    return f"I couldn't complete your booking due to a technical issue. Please try again or contact support if the problem persists."
        
        elif locations.get("pickup"):
            # We have pickup but no dropoff
            if language == "ar":
                return f"أرى أنك تريد أن يتم استلامك من {locations['pickup']}. إلى أين ترغب في الذهاب؟"
            else:
                return f"I see you want to be picked up at {locations['pickup']}. Where would you like to go?"
            
        elif locations.get("dropoff"):
            # We have dropoff but no pickup
            if language == "ar":
                return f"أرى أنك تريد الذهاب إلى {locations['dropoff']}. من أين ترغب في أن يتم استلامك؟"
            else:
                return f"I see you want to go to {locations['dropoff']}. Where would you like to be picked up from?"
            
        else:
            # Couldn't extract locations
            if language == "ar":
                return "يمكنني مساعدتك في حجز رحلة. يرجى إخباري بمواقع الاستلام والإنزال الخاصة بك."
            else:
                return "I can help you book a ride. Please let me know your pickup and dropoff locations."
    
    def _extract_locations(self, message: str) -> Dict[str, str]:
        """Extract pickup and dropoff locations from the message."""
        locations = {}
        
        # Look for "from" or "at" followed by location
        pickup_patterns = [
            r"from\s+([^\.]+?)(?:\s+to|\s*$)",
            r"at\s+([^\.]+?)(?:\s+to|\s*$)",
            r"pickup(?:\s+(?:from|at))?\s+([^\.]+?)(?:\s+to|\s*$)",
            r"pick me up (?:from|at)?\s+([^\.]+?)(?:\s+to|\s*$)"
        ]
        
        # Look for "to" followed by location
        dropoff_patterns = [
            r"to\s+([^\.]+?)(?:\s*$|\s*\.|$)",
            r"destination(?:\s+(?:is|at))?\s+([^\.]+?)(?:\s*$|\s*\.|$)",
            r"take me to\s+([^\.]+?)(?:\s*$|\s*\.|$)"
        ]
        
        # Check if message contains two locations separated by "to"
        if " to " in message.lower():
            parts = message.lower().split(" to ", 1)
            if len(parts) == 2:
                # Get the last few words before "to" for pickup
                pickup_words = parts[0].strip().split(" ")
                pickup_candidate = " ".join(pickup_words[-min(3, len(pickup_words)):])
                
                # Get the first few words after "to" for dropoff
                dropoff_words = parts[1].strip().split(" ")
                dropoff_candidate = " ".join(dropoff_words[:min(3, len(dropoff_words))])
                
                # Check if the extracted parts seem like locations
                if len(pickup_candidate) > 2 and " " in pickup_candidate:
                    locations["pickup"] = pickup_candidate
                if len(dropoff_candidate) > 2 and " " in dropoff_candidate:
                    locations["dropoff"] = dropoff_candidate
        
        # If we already have locations from the simple split, return them
        if locations.get("pickup") and locations.get("dropoff"):
            return locations
        
        # Try to extract pickup location using regex
        for pattern in pickup_patterns:
            match = re.search(pattern, message.lower())
            if match:
                locations["pickup"] = match.group(1).strip()
                break
        
        # Try to extract dropoff location using regex
        for pattern in dropoff_patterns:
            match = re.search(pattern, message.lower())
            if match:
                locations["dropoff"] = match.group(1).strip()
                break
        
        return locations
    
    async def _handle_cancellation(self, message: str, user_id: str, language: str) -> str:
        """Handle ride cancellation requests."""
        # Extract booking ID from message - more sophisticated in production
        booking_id_pattern = r"(?:id|booking|reference)\s*(?:is|:|\#)?\s*([a-zA-Z0-9_]+)"
        booking_id_match = re.search(booking_id_pattern, message, re.IGNORECASE)
        
        if booking_id_match:
            booking_id = booking_id_match.group(1)
            try:
                # Cancel booking
                result = await self.cancel_ride(user_id, booking_id)
                if language == "ar":
                    return f"لقد ألغيت رحلتك (معرف الحجز: {booking_id}). تم رد {result.get('refund_amount', 0)} إلى حسابك. هل هناك أي شيء آخر يمكنني مساعدتك به؟"
                else:
                    return f"I've cancelled your ride (Booking ID: {booking_id}). {result.get('refund_amount', 0)} has been refunded to your account. Is there anything else I can help you with?"
            except Exception as e:
                logger.error(f"Error cancelling ride: {str(e)}")
                if language == "ar":
                    return "لم أتمكن من إلغاء رحلتك بسبب مشكلة فنية. يرجى المحاولة مرة أخرى أو الاتصال بالدعم إذا استمرت المشكلة."
                else:
                    return "I couldn't cancel your ride due to a technical issue. Please try again or contact support if the problem persists."
        else:
            # Get the user's booking history as a fallback
            try:
                ride_history = await self.backend.get_ride_history(user_id)
                if ride_history and len(ride_history) > 0:
                    active_rides = [ride for ride in ride_history if ride.get("status") not in ["cancelled", "completed"]]
                    if active_rides:
                        latest_ride = active_rides[0]
                        if language == "ar":
                            return f"لقد وجدت رحلتك النشطة إلى {latest_ride.get('dropoff', 'وجهتك')}. لإلغائها، يرجى الرد بـ 'نعم، ألغِ' أو قدم معرف الحجز."
                        else:
                            return f"I found your active ride to {latest_ride.get('dropoff', 'your destination')}. To cancel it, please reply with 'Yes, cancel' or provide the booking ID."
                    else:
                        if language == "ar":
                            return "لا أرى أي رحلات نشطة لك. إذا كان لديك معرف حجز، يرجى تقديمه حتى أتمكن من مساعدتك في إلغاء الرحلة الصحيحة."
                        else:
                            return "I don't see any active rides for you. If you have a booking ID, please provide it so I can help you cancel the correct ride."
                else:
                    if language == "ar":
                        return "لم أتمكن من العثور على أي سجل للرحلات. يرجى تقديم معرف الحجز الخاص بك حتى أتمكن من مساعدتك في إلغاء الرحلة الصحيحة."
                    else:
                        return "I couldn't find any ride history. Please provide your booking ID so I can help you cancel the correct ride."
            except Exception as e:
                logger.error(f"Error getting ride history: {str(e)}")
                if language == "ar":
                    return "يمكنني مساعدتك في إلغاء رحلتك. يرجى تقديم معرف الحجز الخاص بك."
                else:
                    return "I can help you cancel your ride. Please provide your booking ID."
    
    async def _handle_recommendations(self, user_id: str, language: str) -> str:
        """Handle recommendation requests."""
        try:
            recommendations = await self.get_recommendations(user_id)
            if recommendations and len(recommendations) > 0:
                if language == "ar":
                    return f"بناءً على سجلك، أوصي بما يلي: {recommendations[0]['content']}"
                else:
                    return f"Based on your history, I recommend: {recommendations[0]['content']}"
            else:
                if language == "ar":
                    return "ليس لدي أي توصيات محددة في الوقت الحالي. هل ترغب في حجز رحلة إلى إحدى وجهاتك المفضلة؟"
                else:
                    return "I don't have any specific recommendations at the moment. Would you like to book a ride to one of your favorite destinations?"
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            if language == "ar":
                return "أواجه مشكلة في الوصول إلى توصياتك في الوقت الحالي. هل ترغب في مساعدتك في حجز رحلة بدلاً من ذلك؟"
            else:
                return "I'm having trouble accessing your recommendations right now. Would you like me to help you book a ride instead?"
    
    async def _handle_safety_check(self, user_id: str, language: str) -> str:
        """Handle safety check requests."""
        try:
            safety_result = await self.perform_safety_check(user_id)
            if language == "ar":
                return f"اكتمل فحص السلامة. التوصيات: {safety_result['recommendations']['ar']}"
            else:
                return f"Safety check completed. Recommendations: {safety_result['recommendations']['en']}"
        except Exception as e:
            logger.error(f"Error performing safety check: {str(e)}")
            if language == "ar":
                return "لم أتمكن من إكمال فحص السلامة في هذا الوقت. يرجى المحاولة مرة أخرى لاحقًا أو الاتصال بالدعم إذا كانت لديك مخاوف تتعلق بالسلامة."
            else:
                return "I couldn't complete the safety check at this time. Please try again later or contact support if you have safety concerns."
    
    async def _handle_carpool(self, user_id: str, language: str) -> str:
        """Handle carpool requests."""
        try:
            opportunities = await self.get_carpool_opportunities(user_id)
            if opportunities and len(opportunities) > 0:
                if language == "ar":
                    reply = f"وجدت {len(opportunities)} فرصة مشاركة سيارة لمسارك. "
                    if len(opportunities) == 1:
                        opp = opportunities[0]
                        reply += f"هناك رحلة مع {opp.get('driver', 'سائق')} من {opp.get('pickup', 'موقع الاستلام')} إلى {opp.get('dropoff', 'موقع الإنزال')} في {opp.get('time', 'الوقت المحدد')}."
                    return reply
                else:
                    reply = f"I found {len(opportunities)} carpool opportunities for your route. "
                    if len(opportunities) == 1:
                        opp = opportunities[0]
                        reply += f"There's a ride with {opp.get('driver', 'a driver')} from {opp.get('pickup', 'pickup')} to {opp.get('dropoff', 'dropoff')} at {opp.get('time', 'the specified time')}."
                    return reply
            else:
                if language == "ar":
                    return "لا أرى أي فرص لمشاركة السيارة في الوقت الحالي. هل ترغب في حجز رحلة عادية بدلاً من ذلك؟"
                else:
                    return "I don't see any carpool opportunities at the moment. Would you like to book a regular ride instead?"
        except Exception as e:
            logger.error(f"Error getting carpool opportunities: {str(e)}")
            if language == "ar":
                return "أواجه مشكلة في التحقق من خيارات مشاركة السيارة الآن. هل ترغب في حجز رحلة عادية بدلاً من ذلك؟"
            else:
                return "I'm having trouble checking carpool options right now. Would you like to book a regular ride instead?"
    
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
    
    async def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze the sentiment of a message."""
        try:
            result = self.sentiment_analyzer(message)[0]
            logger.info(f"Sentiment analysis result for '{message}': {result}")
            
            # Convert 5-star rating to binary sentiment
            rating = int(result["label"].split()[0])  # Extract the number from "X stars"
            
            # Check for angry words directly
            angry_words = ["angry", "mad", "upset", "furious", "frustrated", "annoyed", "irritated"]
            is_angry = any(word in message.lower() for word in angry_words)
            
            # Determine final sentiment
            if is_angry or rating <= 2:  # 1-2 stars is negative
                sentiment = "NEGATIVE"
                score = 0.8 if is_angry else (3 - rating) / 2  # Score from 0.5 to 1.0
            else:
                sentiment = "POSITIVE"
                score = (rating - 3) / 2  # Score from 0.0 to 1.0
            
            return {"label": sentiment, "score": score}
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"label": "NEUTRAL", "score": 0.5}  # Default to neutral on error
    
    async def perform_safety_check(self, user_id: str) -> Dict[str, Any]:
        """Perform a safety check for the user."""
        # In a real implementation, this would check ride data, driver info, etc.
        return {
            "status": "completed",
            "issues": [],
            "recommendations": {
                "en": "Make sure to check the vehicle details and driver ID before starting your journey.",
                "ar": "تأكد من التحقق من تفاصيل السيارة وهوية السائق قبل بدء رحلتك."
            }
        }
    
    async def get_carpool_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get potential carpool opportunities for the user."""
        return await self.backend.get_carpool_matches(user_id) 