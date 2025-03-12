import os

from fastapi import FastAPI, Request, HTTPException
import requests
import json
from utils import bcolors
from config import MATRIX_ADMIN_TOKEN, MATRIX_URL, MATRIX_SERVER_NAME, IDP_GROUP_TO_ROOM, WEBHOOK_SECRET, LOG_LEVEL

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


@app.post("/sync/matrix")
async def matrix_sync(request: Request):
    data = await request.json()

    provided_secret = data.get("secret")
    if not provided_secret:
        raise HTTPException(status_code=400, detail="No secret provided")

    if provided_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret provided")

    user_id = data.get("user", {}).get("username")
    if not user_id:
        raise HTTPException(status_code=400, detail="No user provided")

    matrix_user = f"@{user_id}:{MATRIX_SERVER_NAME}"
    user_groups = data.get("user", {}).get("groups", [])

    headers = {"Authorization": f"Bearer {MATRIX_ADMIN_TOKEN}"}

    for group, rooms in IDP_GROUP_TO_ROOM.items():
        if group in user_groups:
            for room_id in rooms:
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