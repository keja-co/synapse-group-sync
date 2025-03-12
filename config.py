import json
import os

from dotenv import load_dotenv

# Check if .env file exists
if os.path.exists(".env"):
    print("Found .env file, loading environment variables from file and not from system environment")
    load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

WEBHOOK_SECRET=os.environ.get("WEBHOOK_SECRET")

MATRIX_ADMIN_TOKEN=os.environ.get("MATRIX_ADMIN_TOKEN")
MATRIX_ADMIN_USER_ID=os.environ.get("MATRIX_ADMIN_USER_ID")
MATRIX_URL=os.environ.get("MATRIX_URL")
MATRIX_SERVER_NAME=os.environ.get("MATRIX_SERVER_NAME")

AUTHENTIK_API_URL=os.environ.get("AUTHENTIK_API_URL")
AUTHENTIK_TOKEN=os.environ.get("AUTHENTIK_TOKEN")

IDP_GROUP_TO_ROOM=json.loads(os.environ.get("IDP_GROUP_TO_ROOM", "{}"))