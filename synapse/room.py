import requests
from fastapi import HTTPException

from config import MATRIX_URL, MATRIX_ADMIN_USER_ID, MATRIX_ADMIN_TOKEN
from synapse.synapse_admin import get_headers
from utils import log, LogLevel


def add_to_room(matrix_user_id, room_id):
    ensure_room_admin(room_id)

    headers = get_headers()

    log(LogLevel.INFO, f"Adding {matrix_user_id} to {room_id}.")

    matrix_response = requests.post(
        f"{MATRIX_URL}/_synapse/admin/v1/join/{room_id}",
        headers=headers,
        json={"user_id": matrix_user_id}
    )

    if matrix_response.status_code != 200:
        if matrix_response.json()["error"] == f"{matrix_user_id} is already in the room.":
            log(LogLevel.INFO, f"{matrix_user_id} is already in the room.")
            return True
        else:
            log(LogLevel.ERROR, f"Error adding {matrix_user_id} to {room_id}.")
            log(LogLevel.DEBUG, f"{matrix_response.status_code}: {matrix_response.json()}")
            return False
    else:
        log(LogLevel.INFO, f"Added {matrix_user_id} to {room_id}.")
        return True


def remove_from_room(matrix_user_id, room_id):
    ensure_room_admin(room_id)

    headers = get_headers()

    log(LogLevel.INFO, f"Removing {matrix_user_id} from {room_id}.")

    matrix_response = requests.post(
        f"{MATRIX_URL}/_matrix/client/v3/rooms/{room_id}/kick",
        json={"user_id": matrix_user_id, "reason": "Removed from group"},
        headers=headers
    )

    if matrix_response.status_code != 200:
        log(LogLevel.ERROR, f"Error removing {matrix_user_id} from {room_id}.")
        log(LogLevel.DEBUG, f"{matrix_response.status_code}: {matrix_response.json()}")
        return False
    else:
        log(LogLevel.INFO, f"Removed {matrix_user_id} from {room_id}.")
        return True

def add_to_rooms(matrix_user_id, room_ids: [str]):
    for room_id in room_ids:
        add_to_room(matrix_user_id, room_id)

def remove_from_rooms(matrix_user_id, room_ids: [str]):
    for room_id in room_ids:
        remove_from_room(matrix_user_id, room_id)

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

        # Join the room
        matrix_join_response = requests.post(
            f"{MATRIX_URL}/_matrix/client/v3/join/{room_id}",
            headers=headers
        )

        if matrix_join_response.status_code == 200:
            log(LogLevel.INFO, f"{MATRIX_ADMIN_USER_ID} is now an admin of {room_id}.")
        else:
            log(LogLevel.ERROR, f"Failed to join admin to {room_id}.")
            log(LogLevel.DEBUG, f"{matrix_join_response.status_code}: {matrix_join_response.text}")
    else:
        log(LogLevel.ERROR, f"Failed to make {MATRIX_ADMIN_USER_ID} an admin of {room_id}.")
        log(LogLevel.DEBUG, f"{matrix_admin_response.status_code}: {matrix_admin_response.text}")
    return True


# Check if matrix user is in room and admin, if not add them and make them an admin
def ensure_room_admin(room_id, matrix_admin_user=MATRIX_ADMIN_USER_ID):
    headers = get_headers()

    if not is_in_room(headers, room_id, matrix_admin_user):
        log(LogLevel.INFO, f"Adding admin ({matrix_admin_user}) to {room_id} (not currently in room).")

        make_room_admin(headers, room_id, matrix_admin_user)
    elif not is_room_admin(headers, room_id, matrix_admin_user):
        log(LogLevel.INFO, f"Adding admin ({matrix_admin_user}) to {room_id} (not currently an admin).")

        make_room_admin(headers, room_id, matrix_admin_user)
    log(LogLevel.DEBUG, f"{matrix_admin_user} is in {room_id} and is an admin.")
