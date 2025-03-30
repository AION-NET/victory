#   config.py
#   AION RWX (c) 2025 Gregory L. Magnusson BANKON
import os
from dotenv import load_dotenv, set_key
import secrets  #   For secure API key generation

#   Load environment variables from the .env file
load_dotenv()

#   Path to the .env file
ENV_FILE = ".env"

#   Local directory for file operations
BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))  #   Deployment folder

#   Load or Generate API Token
API_TOKEN = os.getenv("API_TOKEN")

def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_hex(32)

def save_api_key(api_key):
    """Save the generated API key to the .env file."""
    set_key(ENV_FILE, "API_TOKEN", api_key)
    print(f"[INFO] New API Key generated and saved to {ENV_FILE}.")

#   Generate and save API key if missing
if not API_TOKEN:
    API_TOKEN = generate_api_key()
    save_api_key(API_TOKEN)
else:
    print("[INFO] Existing API Key loaded from .env.")

#   Validate the local working directory
def validate_directory():
    """Ensure the working directory exists."""
    if not os.path.exists(BASE_DIRECTORY):
        raise ValueError(f"[ERROR] Required directory '{BASE_DIRECTORY}' does not exist.")
    else:
        print(f"[INFO] Verified directory: {BASE_DIRECTORY}")

validate_directory()
