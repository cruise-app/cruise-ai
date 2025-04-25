# Cruise Chatbot

An intelligent chatbot service for the Cruise ride-hailing platform.

## Features

- Natural language processing for user queries
- Integration with OpenAI's GPT model
- Real-time conversation handling
- Integration with other Cruise microservices

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Other Cruise microservices (car-rental, etc.)

## Setup

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

4. Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
```

5. Start the service:
```bash
python chatbot.py
```

## Testing

Run tests:
```bash
pytest
```

## Integration

The chatbot integrates with other Cruise microservices:
- Car Rental Service
- User Service
- Payment Service

## License

MIT 