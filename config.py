import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Credentials
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Application Settings
LOG_CHECK_INTERVAL = int(os.getenv("LOG_CHECK_INTERVAL", "60"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", "5"))  # number of errors before alerting

# File Paths
CONFIG_PATH = "registered_apps.json"
LOG_DIR = "logs"

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True) 