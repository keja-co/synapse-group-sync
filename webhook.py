import requests
from fastapi import APIRouter, Request, HTTPException

from config import MATRIX_ADMIN_TOKEN, IDP_GROUP_TO_ROOM, MATRIX_URL, LOG_LEVEL
from utils import verify_secret, get_user, get_user_id, get_matrix_user, get_user_groups, bcolors
from synapse.room import add_to_room, remove_from_room

router = APIRouter()


# Adds a user to a room in Synapse (does not remove users)
@router.post("/sync/matrix", tags=["sync"])
async def matrix_sync(request: Request):
    data = await request.json()

    verify_secret(data.get("secret"))

    user = get_user(data)
    user_id = get_user_id(user)
    if not user_id:
        raise HTTPException(status_code=400, detail="No user provided")

    matrix_user = get_matrix_user(user_id)
    user_groups = get_user_groups(user)

    # Add User to Rooms
    for group, rooms in IDP_GROUP_TO_ROOM.items():
        if group in user_groups:
            for room_id in rooms:
                status = add_to_room(matrix_user, room_id)
    return {"status": "processing sync..."}


# Removes a user from a room in Synapse
@router.post("/sync/matrix/remove", tags=["sync"])
async def matrix_sync_remove(request: Request):
    data = await request.json()

    verify_secret(data.get("secret"))

    user = get_user(data)
    user_id = get_user_id(user)
    if not user_id:
        raise HTTPException(status_code=400, detail="No user provided")

    matrix_user = get_matrix_user(user_id)
    # These are the groups to remove the user from
    remove_groups = user.get("remove_groups", [])
    user_groups = get_user_groups(user)

    if not remove_groups:
        raise HTTPException(status_code=400, detail="No remove_groups provided")

    rooms_to_remove = []
    for group, rooms in IDP_GROUP_TO_ROOM.items():
        if group in remove_groups:
            for room_id in rooms:
                # Check if the user is allowed to be in the room because of another group
                allowed = False
                for other_group, other_rooms in IDP_GROUP_TO_ROOM.items():
                    if other_group != group and other_group in user_groups and room_id in other_rooms:
                        allowed = True
                        break
                if not allowed:
                    rooms_to_remove.append(room_id)

    for room_id in rooms_to_remove:
        status = remove_from_room(matrix_user, room_id)

    return {"status": "processing sync..."}