import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize logger for configuration
logger = logging.getLogger(__name__)

# Retrieve the Gemini API key
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    logger.critical("GEMINI_API_KEY not found in environment variables.")
    raise ValueError("Missing GEMINI_API_KEY in environment variables.")

logger.info("GEMINI_API_KEY loaded successfully.")
