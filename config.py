import json
import os

from dotenv import load_dotenv

# Check if .env file exists
if os.path.exists(".env"):
    print("Found .env file, loading environment variables from file and not from system environment")
    load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

WEBHOOK_SECRET=os.environ.get("WEBHOOK_SECRET")
if not WEBHOOK_SECRET:
    raise RuntimeError("WEBHOOK_SECRET environment variable is not set")

MATRIX_ADMIN_TOKEN=os.environ.get("MATRIX_ADMIN_TOKEN")
if not MATRIX_ADMIN_TOKEN:
    raise RuntimeError("MATRIX_ADMIN_TOKEN environment variable is not set")
MATRIX_ADMIN_USER_ID=os.environ.get("MATRIX_ADMIN_USER_ID")
if not MATRIX_ADMIN_USER_ID:
    raise RuntimeError("MATRIX_ADMIN_USER_ID environment variable is not set")
MATRIX_URL=os.environ.get("MATRIX_URL")
if not MATRIX_URL:
    raise RuntimeError("MATRIX_URL environment variable is not set")
MATRIX_SERVER_NAME=os.environ.get("MATRIX_SERVER_NAME")
if not MATRIX_SERVER_NAME:
    raise RuntimeError("MATRIX_SERVER_NAME environment variable is not set")

DATA_DIR=os.environ.get("DATA_DIR")
if not DATA_DIR:
    raise RuntimeError("DATA_DIR environment variable is not set")

AUTHENTIK_API_URL=os.environ.get("AUTHENTIK_API_URL")
AUTHENTIK_TOKEN=os.environ.get("AUTHENTIK_TOKEN")

IDP_GROUP_TO_ROOM=json.loads(os.environ.get("IDP_GROUP_TO_ROOM", "{}"))