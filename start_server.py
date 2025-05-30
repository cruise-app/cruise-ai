#!/usr/bin/env python3
import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('chatbot_server.log')
    ]
)

logger = logging.getLogger("cruise-chatbot")

def start_server():
    """Start the FastAPI server for the Cruise chatbot."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OpenAI API key not found in environment variables!")
            logger.info("Create a .env file with OPENAI_API_KEY=your_api_key or export it in your environment")
            sys.exit(1)
        
        # Get host and port from environment or use defaults
        host = os.getenv("CHATBOT_HOST", "0.0.0.0")
        port = int(os.getenv("CHATBOT_PORT", "8000"))
        
        logger.info(f"Starting Cruise chatbot API server on {host}:{port}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Start the server
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 