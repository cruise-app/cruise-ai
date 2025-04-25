# 🤖 Cruise AI Chatbot

Welcome to the Cruise AI Chatbot! This intelligent chatbot service enhances the Cruise ride-hailing experience by providing instant, natural language support to our users.

## ✨ Features

- 💬 Natural language processing for user queries
- 🧠 Powered by OpenAI's GPT model
- 🌍 Multilingual support
- 🔄 Real-time conversation handling
- 🔌 Seamless integration with Cruise microservices
- 📊 Analytics and monitoring
- 🔔 Smart notifications
- 🎯 Context-aware responses

## 🛠️ Tech Stack

- **Backend**: Python with FastAPI
- **AI**: OpenAI GPT
- **Database**: MongoDB
- **Testing**: Pytest
- **API Documentation**: Swagger/OpenAPI

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- MongoDB
- Other Cruise microservices (car-rental, etc.)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/zarzourr/cruise-bot.git
cd cruise-bot
```

2. Create and activate virtual environment:
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
# Edit .env with your configuration
```

5. Start the service:
```bash
python chatbot.py
```

## 📡 API Documentation

### Chat Endpoint
```http
POST /api/chat
```
Request Body:
```json
{
  "message": "string",
  "userId": "string",
  "context": {
    "language": "en",
    "platform": "mobile"
  }
}
```

### Health Check
```http
GET /health
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_chatbot.py
```

## 📦 Project Structure

```
cruise-bot/
├── src/
│   ├── api/          # FastAPI endpoints
│   │   └── chatbot.py   # Main chatbot implementation
│   ├── services/     # External service integrations
│   └── utils/        # Utility functions
├── tests/            # Test files
└── docs/             # Documentation
```

## 🔌 Integration

The chatbot integrates with other Cruise microservices:
- 🚗 Car Rental Service
- 👤 User Service
- 💳 Payment Service
- 📱 Mobile App

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all our contributors
- Powered by OpenAI's amazing technology
- Built with ❤️ by the Cruise team 