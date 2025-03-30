# Cruise AI Customer Support Bot

An AI-powered customer support chatbot for Cruise, featuring multilingual support, sentiment analysis, and real-time notifications.

## Features

- 🤖 AI-powered responses using GPT-3.5
- 🌍 Multilingual support (English, Arabic)
- 😊 Sentiment analysis for user messages
- 📱 Real-time notifications for ride updates
- 🗺️ Location services with Google Maps integration
- 🔄 Automatic escalation to human support
- 📊 Analytics and monitoring

## Architecture

The system is built with a modular architecture:

```
src/
├── api/                 # FastAPI endpoints
├── core/               # Core business logic
│   ├── interfaces/     # Interface definitions
│   ├── chatbot.py     # Main chatbot implementation
│   └── backend.py     # Backend service interface
├── services/          # External service integrations
│   └── mock_backend.py # Mock implementation for testing
└── utils/             # Utility functions
    ├── notifications.py # Notification service
    ├── location.py    # Location services
    └── firebase.py    # Firebase integration
```

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd cruise-ai-support
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

## Testing

### Starting the Server

1. Start the FastAPI server:
```bash
uvicorn src.api.main:app --reload --port 8001
```

2. Open the Swagger UI at http://127.0.0.1:8001/docs

### Testing the Chatbot

1. Use the `/chat` endpoint with a POST request:
```json
{
    "message": "I need a ride",
    "user_id": "test_user",
    "language": "en"
}
```

2. Test different scenarios:
   - Happy messages: "I am very happy with the service"
   - Negative messages: "This is terrible, I hate it"
   - Neutral messages: "I am feeling a bit disappointed"

### Testing Notifications

1. Use the `/test-notification` endpoint with a POST request:
```json
{
    "user_id": "test_user",
    "title": "Test Notification",
    "body": "This is a test notification",
    "data": {
        "type": "test"
    }
}
```

2. Available test users:
   - "test_user" (token: mock_device_token_123)
   - "john_doe" (token: mock_device_token_456)
   - "zeyad" (token: mock_device_token_789)

### Testing Ride Booking

1. Use the `/book-ride` endpoint with a POST request:
```json
{
    "pickup": {
        "lat": 25.2048,
        "lng": 55.2708
    },
    "dropoff": {
        "lat": 25.2048,
        "lng": 55.2708
    },
    "vehicle_type": "sedan",
    "scheduled_time": "2024-03-30T10:00:00Z"
}
```

2. The system will:
   - Validate the locations
   - Create a booking
   - Start monitoring for updates
   - Send notifications for status changes

## API Endpoints

- `GET /`: Health check
- `POST /chat`: Process chat messages
- `POST /test-notification`: Test notification system
- `POST /book-ride`: Create a new ride booking
- `GET /docs`: Swagger UI documentation

## Environment Variables

Required environment variables:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
CRUISE_API_KEY=your_cruise_api_key
FIREBASE_CREDENTIALS=path_to_firebase_credentials.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 