import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Keys
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
if not SERPER_API_KEY:
    logger.warning("Serper API key not found in environment variables")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
logger.info(f"Using Ollama base URL: {OLLAMA_BASE_URL}")

# Application Settings
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8080"))

# Serper API Settings
SERPER_BASE_URL = "https://google.serper.dev/search"

# Ollama Settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1B")  # You can change this to your preferred model
logger.info(f"Using Ollama model: {OLLAMA_MODEL}")