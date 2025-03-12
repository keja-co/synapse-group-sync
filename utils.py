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


# Check if matrix user is in room and admin
def is_in_room(headers, room_id, matrix_user):
    log(LogLevel.DEBUG, f"Checking if {matrix_user} is in {room_id}.")

    joined_rooms = requests.get(
        f"{MATRIX_URL}/_matrix/client/v3/joined_rooms",
        headers=headers
    )

    log(LogLevel.DEBUG, f"Joined rooms: {joined_rooms.json()}")

    if room_id in joined_rooms.json().get("joined_rooms", []):
        log(LogLevel.DEBUG, f"Room {room_id} joined.")
        return True

    log(LogLevel.DEBUG, f"Room {room_id} not joined.")
    return False


def is_room_admin(headers, room_id, matrix_user):
    log(LogLevel.DEBUG, f"Checking if {matrix_user} is an admin of {room_id}.")

    room_power_levels = requests.get(
        f"{MATRIX_URL}/_matrix/client/v3/rooms/{room_id}/state/m.room.power_levels",
        headers=headers
    )

    log(LogLevel.DEBUG, f"Room power levels: {room_power_levels.json()}")

    if matrix_user in room_power_levels.json().get("users", {}):
        if room_power_levels.json().get("users").get(matrix_user) >= 100:
            log(LogLevel.DEBUG, f"{matrix_user} is an admin of {room_id}.")
            return True

    log(LogLevel.DEBUG, f"{matrix_user} is not an admin of {room_id}.")
    return False


# Make provided matrix user an admin of the room
def make_room_admin(headers, room_id, matrix_user):
    log(LogLevel.INFO, f"Adding {MATRIX_ADMIN_USER_ID} to {room_id}.")

    # Check if this admin user is already in the room, if not join it and become room admin
    matrix_admin_response = requests.post(
        f"{MATRIX_URL}/_synapse/admin/v1/rooms/{room_id}/make_room_admin",
        headers=headers,
        json={"user_id": MATRIX_ADMIN_USER_ID}
    )

    # Attempt to accept the invite for the admin user
    if matrix_admin_response.status_code == 200:
        log(LogLevel.INFO, f"{MATRIX_ADMIN_USER_ID} is now an admin of {room_id}.")
    else:
        log(LogLevel.ERROR, f"Failed to make {MATRIX_ADMIN_USER_ID} an admin of {room_id}.")
        log(LogLevel.DEBUG, f"{matrix_admin_response.status_code}: {matrix_admin_response.text}")
    return True


# Check if matrix user is in room and admin, if not add them and make them an admin
def ensure_room_admin(room_id, matrix_admin_user=MATRIX_ADMIN_USER_ID):
    headers = {"Authorization": f"Bearer {MATRIX_ADMIN_TOKEN}"}

    if not is_in_room(headers, room_id, matrix_admin_user):
        log(LogLevel.INFO, f"Adding admin ({matrix_admin_user}) to {room_id} (not currently in room).")

        make_room_admin(headers, room_id, matrix_admin_user)
    elif not is_room_admin(headers, room_id, matrix_admin_user):
        log(LogLevel.INFO, f"Adding admin ({matrix_admin_user}) to {room_id} (not currently an admin).")

        make_room_admin(headers, room_id, matrix_admin_user)
    log(LogLevel.DEBUG, f"{matrix_admin_user} is in {room_id} and is an admin.")
