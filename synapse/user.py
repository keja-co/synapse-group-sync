from fastapi import HTTPException
from typing import Optional

import requests
from config import MATRIX_URL, IDP_NAME, MATRIX_SERVER_NAME
from synapse import synapse_admin
from utils import LogLevel, log


def create_or_modify_user(matrix_id: str, display_name: str, external_id: str, email: Optional[str] = None):
    body = {
        "displayname": display_name,
        "external_ids": [
            {
                "auth_provider": IDP_NAME,
                "external_id": external_id
            }
        ]
    }

    if email is not None:
        body["threepids"] = [
            {
                "medium": "email",
                "address": email
            }
        ]

    synapse_response = requests.put(
        f"{MATRIX_URL}/_synapse/admin/v2/users/{matrix_id}",
        headers=synapse_admin.get_headers(),
        json=body
    )

    if synapse_response.status_code == 200:
        # User Created
        pass
    elif synapse_response.status_code == 201:
        # User Modified
        pass
    else:
        # Error
        raise HTTPException(status_code=500, detail="Error creating or modifying user.")

    return synapse_response.json()

def get_matrix_account_id(external_id: str):
    synapse_response = requests.get(
        f"{MATRIX_URL}/_synapse/admin/v1/auth_providers/{IDP_NAME}/users/{external_id}",
        headers=synapse_admin.get_headers()
    )

    if synapse_response.status_code == 200:
        return synapse_response.json()["user_id"]
    elif synapse_response.status_code == 404:
        return None
    else:
        log(LogLevel.ERROR, f"Error fetching user: {external_id}: {synapse_response.text}")
        raise HTTPException(status_code=500, detail="Error fetching user.")

# TODO: Let user specify the format
def generate_matrix_id(external_id: str):
    return f"@{external_id}:{MATRIX_SERVER_NAME}"