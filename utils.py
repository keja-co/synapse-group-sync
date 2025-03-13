import requests
from fastapi import HTTPException
from enum import Enum

from config import WEBHOOK_SECRET, MATRIX_SERVER_NAME, MATRIX_ADMIN_USER_ID, MATRIX_URL, LOG_LEVEL, MATRIX_ADMIN_TOKEN


# Enum for log levels
class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    ERROR = 3


def log(level=LogLevel.INFO, message=""):
    if level == LogLevel.DEBUG:
        if LOG_LEVEL == "DEBUG":
            print(f"{bcolors.OKBLUE}DEBUG:{bcolors.ENDC} {message}")
    elif level == LogLevel.INFO:
        print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} {message}")
    elif level == LogLevel.ERROR:
        print(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} {message}")
    else:
        print(f"UNKNOWN: {message}")


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



