from fastapi import HTTPException

from config import WEBHOOK_SECRET, MATRIX_SERVER_NAME


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Verify Secret
def verify_secret(provided_secret):
    if not provided_secret:
        raise HTTPException(status_code=400, detail="No secret provided")

    if provided_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret provided")

    return True

# Get Matrix User
def get_matrix_user(user_id):
    return f"@{user_id}:{MATRIX_SERVER_NAME}"

# Get User
def get_user(data):
    return data.get("user", {})

# Get User ID
def get_user_id(user_data):
    return user_data.get("username")

# Get User Groups
def get_user_groups(user_data):
    return user_data.get("groups", [])