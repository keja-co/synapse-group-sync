from fastapi import FastAPI, Request, HTTPException
import requests
from utils import bcolors, verify_secret, get_user_groups, get_matrix_user, get_user, get_user_id, ensure_room_admin
from config import MATRIX_ADMIN_TOKEN, MATRIX_URL, MATRIX_SERVER_NAME, IDP_GROUP_TO_ROOM, WEBHOOK_SECRET, LOG_LEVEL, \
    MATRIX_ADMIN_USER_ID

print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Starting Synapse Group Sync")

print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Loaded Mappings:")

for mapped_group in IDP_GROUP_TO_ROOM:
    print(
        f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Group: {mapped_group} {bcolors.OKBLUE}->{bcolors.ENDC} Rooms: {IDP_GROUP_TO_ROOM[mapped_group]}")
app = FastAPI()


@app.get("/")
async def root():
    return {"status": "success"}


@app.get("/health")
async def health():
    return {"status": "success"}


# Adds a user to a room in Synapse (does not remove users)
@app.post("/sync/matrix")
async def matrix_sync(request: Request):
    data = await request.json()

    verify_secret(data.get("secret"))

    user = get_user(data)
    user_id = get_user_id(user)
    if not user_id:
        raise HTTPException(status_code=400, detail="No user provided")

    matrix_user = get_matrix_user(user_id)
    user_groups = get_user_groups(user)

    headers = {"Authorization": f"Bearer {MATRIX_ADMIN_TOKEN}"}

    # Add User to Rooms

    for group, rooms in IDP_GROUP_TO_ROOM.items():
        if group in user_groups:
            for room_id in rooms:
                ensure_room_admin(room_id)

                print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Adding {matrix_user} to {room_id}.")

                matrix_response = requests.post(
                    f"{MATRIX_URL}/_synapse/admin/v1/join/{room_id}",
                    headers=headers,
                    json={"user_id": matrix_user}
                )

                if matrix_response.status_code != 200:
                    if matrix_response.json()["error"] == f"{matrix_user} is already in the room.":
                        print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} {matrix_user} is already in the room.")
                        continue

                    print(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} Error adding {matrix_user} to {room_id}.")
                    if LOG_LEVEL == "DEBUG":
                        print(f"{bcolors.FAIL}DEBUG:{bcolors.ENDC} {matrix_response.json()}")
                    raise HTTPException(status_code=500, detail="Failed to add user to room")

                if matrix_response.status_code == 200:
                    print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Added {matrix_user} to {room_id}.")

    return {"status": "success"}


# Removes a user from a room in Synapse
@app.post("/sync/matrix/remove")
async def matrix_sync_remove(request: Request):
    data = await request.json()

    verify_secret(data.get("secret"))

    user_id = data.get("user", {}).get("username")

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

    headers = {"Authorization": f"Bearer {MATRIX_ADMIN_TOKEN}"}

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
        print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Removing {matrix_user} from {room_id}.")
        matrix_response = requests.post(
            f"{MATRIX_URL}/_matrix/client/v3/rooms/{room_id}/kick",
            json={"user_id": matrix_user, "reason": "Removed from group"},
            headers=headers
        )

        if matrix_response.status_code != 200:
            print(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} Error removing {matrix_user} from {room_id}.")
            if LOG_LEVEL == "DEBUG":
                print(f"{bcolors.FAIL}DEBUG:{bcolors.ENDC} {matrix_response.json()}")
            raise HTTPException(status_code=500, detail="Failed to remove user from room")

        if matrix_response.status_code == 200:
            print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Removed {matrix_user} from {room_id}.")

        return {"status": "success"}
