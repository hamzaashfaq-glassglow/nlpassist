import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "nlpassist"

# RAG Configuration
TOP_K = int(os.getenv("TOP_K", 3))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 1.6))
MAX_GENERATION_LENGTH = int(os.getenv("MAX_GENERATION_LENGTH", 400))

# API Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
DEBUG = True

# Logging Configuration
LOG_ALL_QUERIES = True
LOG_LEVEL = "INFO"

# Security Configuration
API_KEY = os.getenv('API_KEY', 'nlp-assistant-secret-key-change-in-production')
REQUIRE_API_KEY = os.getenv('REQUIRE_API_KEY', 'false').lower() == 'true'
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
RATE_LIMIT_GLOBAL = os.getenv('RATE_LIMIT_GLOBAL', '100 per hour')
RATE_LIMIT_ASK = os.getenv('RATE_LIMIT_ASK', '20 per minute')
RATE_LIMIT_CHAT = os.getenv('RATE_LIMIT_CHAT', '50 per minute')

# Input Validation
MAX_QUESTION_LENGTH = 500
MAX_TITLE_LENGTH = 100
