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
- 🔌 Direct integration with Cruise's backend API

## Architecture

The system is built with a modular architecture:

```
src/
├── api/                 # FastAPI endpoints
├── core/               # Core business logic
│   ├── interfaces/     # Interface definitions
│   ├── chatbot.py     # Main chatbot implementation
│   └── real_backend.py # Real Cruise backend integration
├── services/          # External service integrations
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

## Integration with Cruise App

### Backend Integration

The chatbot is now fully integrated with Cruise's backend API. To use it:

1. Set up your Cruise API credentials:
```bash
CRUISE_API_KEY=your_cruise_api_key
CRUISE_API_BASE_URL=https://api.cruise.com/v1  # or your specific environment URL
```

2. The chatbot will automatically:
   - Authenticate with Cruise's API
   - Handle user profiles and ride history
   - Manage bookings and cancellations
   - Process carpool matches
   - Handle user preferences
   - Manage support escalations

### API Endpoints

The following endpoints are available for integration:

- `GET /`: Health check
- `POST /chat`: Process chat messages
- `POST /book-ride`: Create a new ride booking
- `POST /cancel-ride/{ride_id}`: Cancel an existing ride
- `GET /recommendations/{user_id}`: Get personalized recommendations
- `GET /safety-check/{user_id}`: Perform safety checks
- `GET /carpool-opportunities/{user_id}`: Get carpool opportunities
- `POST /test-notification`: Test notification system
- `GET /docs`: Swagger UI documentation

### Testing

1. Start the FastAPI server:
```bash
uvicorn src.api.main:app --reload --port 8001
```

2. Open the Swagger UI at http://127.0.0.1:8001/docs

3. Test the integration:
   - Use the `/chat` endpoint to test conversation flow
   - Use `/book-ride` to test booking creation
   - Use `/cancel-ride/{ride_id}` to test cancellation
   - Use `/recommendations/{user_id}` to test personalized suggestions

## Environment Variables

Required environment variables:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
CRUISE_API_KEY=your_cruise_api_key
CRUISE_API_BASE_URL=https://api.cruise.com/v1
FIREBASE_CREDENTIALS=path_to_firebase_credentials.json
```

## Error Handling

The system includes comprehensive error handling for:
- API authentication failures
- Network connectivity issues
- Invalid requests
- Rate limiting
- Resource not found errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 