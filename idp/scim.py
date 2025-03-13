import json
import os

from fastapi import APIRouter, HTTPException, Path, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any, Optional

from config import DATA_DIR
from utilities import auth
from utils import log, LogLevel

# SCIM Schemas
SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
SCIM_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"

# SCIM Models
class SCIMName(BaseModel):
    formatted: Optional[str]
    familyName: Optional[str]
    givenName: Optional[str]
    middleName: Optional[str] = None
    honorificPrefix: Optional[str] = None
    honorificSuffix: Optional[str] = None


class SCIMEmail(BaseModel):
    value: str
    type: Optional[str] = None
    primary: Optional[bool] = None


# Models
class SCIMUser(BaseModel):
    schemas: List[str] = Field(default=[SCIM_USER_SCHEMA])
    userName: str = Field(..., title="Unique identifier for the user")
    name: SCIMName = Field(..., title="User's name")
    displayName: str = Field(..., title="User's display name")
    emails: List[SCIMEmail] = Field(..., title="User's email addresses")
    active: bool = Field(default=True, title="User active status")
    externalId: Optional[str] = Field(None, title="External identifier for the user")


class SCIMUserUpdate(BaseModel):
    schemas: List[str] = Field(default=[SCIM_USER_SCHEMA])
    userName: Optional[str] = Field(None, title="Unique identifier for the user")
    name: Optional[SCIMName] = Field(None, title="User's name")
    displayName: Optional[str] = Field(None, title="User's display name")
    emails: Optional[List[SCIMEmail]] = Field(None, title="User's email addresses")
    active: Optional[bool] = Field(None, title="User active status")
    externalId: Optional[str] = Field(None, title="External identifier for the user")


class SCIMGroup(BaseModel):
    schemas: List[str] = [SCIM_GROUP_SCHEMA]
    displayName: str = Field(..., title="Group's display name")
    members: Optional[List[Dict[str, str]]] = None
    externalId: Optional[str] = Field(None, title="External identifier for the group")


class SCIMGroupUpdate(BaseModel):
    schemas: List[str] = [SCIM_GROUP_SCHEMA]
    displayName: Optional[str] = Field(None, title="Group's display name")
    members: Optional[List[Dict[str, str]]] = None
    externalId: Optional[str] = Field(None, title="External identifier for the group")

# File Stores
user_file_location = f"{DATA_DIR}/users.json"
group_file_location = f"{DATA_DIR}/groups.json"

# Create Files if they don't exist
if not os.path.exists(user_file_location):
    with open(user_file_location, "w") as f:
        json.dump({}, f)

if not os.path.exists(group_file_location):
    with open(group_file_location, "w") as f:
        json.dump({}, f)

# Database Functions

def db_get_user(user_id: str):
    with open(user_file_location, "r") as f:
        users = json.load(f)
    return users.get(user_id, None)

def db_get_group(group_id: str):
    with open(group_file_location, "r") as f:
        groups = json.load(f)
    return groups.get(group_id, None)

def db_create_user(user: SCIMUser):
    with open(user_file_location, "r") as f:
        users = json.load(f)
    users[user.externalId] = user.model_dump()
    with open(user_file_location, "w") as f:
        json.dump(users, f)

def db_create_group(group: SCIMGroup):
    with open(group_file_location, "r") as f:
        groups = json.load(f)
    groups[group.externalId] = group.model_dump()
    with open(group_file_location, "w") as f:
        json.dump(groups, f)

def db_update_user(user_id: str, update_data: SCIMUserUpdate):
    with open(user_file_location, "r") as f:
        users = json.load(f)
    users[user_id] = update_data.model_dump()
    with open(user_file_location, "w") as f:
        json.dump(users, f)

def db_update_group(group_id: str, update_data: SCIMGroupUpdate):
    with open(group_file_location, "r") as f:
        groups = json.load(f)
    groups[group_id] = update_data.model_dump()
    with open(group_file_location, "w") as f:
        json.dump(groups, f)

# SCIM Routes

router = APIRouter()


@router.get("/ServiceProviderConfig")
async def service_provider_config():
    return JSONResponse(
        content={
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
            "patch": {"supported": False},
            "bulk": {"supported": False},
            "filter": {"supported": False},
            "changePassword": {"supported": False},
            "sort": {"supported": False},
            "etag": {"supported": False},
            "authenticationSchemes": [
                {
                    "name": "Bearer",
                    "description": "Authentication Scheme using the Bearer Token Standard",
                    "specUri": "http://www.rfc-editor.org/info/rfc6750",
                    "documentationUri": "http://www.rfc-editor.org/info/rfc6750",
                    "type": "oauthbearertoken",
                    "primary": True
                }
            ],
            "meta": {"resourceType": "ServiceProviderConfig", "location": "/ServiceProviderConfig"}
        }
    )


# Create User
@router.post("/Users")
async def create_user(user: SCIMUser, token: str = Depends(auth.verify_token)):

    log(LogLevel.DEBUG, f"User created: {user.model_dump()}")
    log(LogLevel.INFO, f"SCIM User POST: {user.userName}")

    db_create_user(user)

    return JSONResponse(status_code=201, content={"id": user.externalId, **user.model_dump()})


# Get User
@router.get("/Users/{user_id}")
async def get_user(user_id: str, token: str = Depends(auth.verify_token)):

    user = db_get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(status_code=200, content={"id": user_id, **user})

# Update User
@router.put("/Users/{user_id}")
async def update_user(user_id: str, update_data: SCIMUserUpdate, token: str = Depends(auth.verify_token)):

    log(LogLevel.DEBUG, f"User updated: {user_id} -> {update_data.model_dump()}")
    log(LogLevel.INFO, f"SCIM User PUT: {user_id}")

    db_update_user(user_id, update_data)

    return JSONResponse(status_code=200, content={"id": update_data.externalId, **update_data.model_dump()})


@router.delete("/Users/{user_id}")
async def delete_user(user_id: str, token: str = Depends(auth.verify_token)):

    log(LogLevel.INFO, f"User removed: {user_id}")
    return JSONResponse(status_code=204, content={})


# Create Group
@router.post("/Groups")
async def create_group(group: SCIMGroup, token: str = Depends(auth.verify_token)):

    log(LogLevel.DEBUG, f"Group created: {group.model_dump()}")
    log(LogLevel.INFO, f"SCIM Group POST: {group.displayName}")

    db_create_group(group)

    return JSONResponse(status_code=201, content={"id": group.externalId, **group.model_dump()})


# Get Group
@router.get("/Groups/{group_id}")
async def get_group(group_id: str, token: str = Depends(auth.verify_token)):

    group = db_get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return JSONResponse(status_code=200, content={"id": group_id, **group})

# PUT Group
@router.put("/Groups/{group_id}")
async def update_group(group_id: str, update_data: SCIMGroupUpdate, token: str = Depends(auth.verify_token)):

    log(LogLevel.DEBUG, f"Group updated: {group_id} -> {update_data.model_dump()}")
    log(LogLevel.INFO, f"SCIM Group PUT: {update_data.displayName}")

    db_update_group(group_id, update_data)

    return JSONResponse(status_code=200, content={"id": update_data.externalId, **update_data.model_dump()})


# Delete Group
@router.delete("/Groups/{group_id}")
async def delete_group(group_id: str, token: str = Depends(auth.verify_token)):

    log(LogLevel.INFO, f"Group deleted: {group_id}")
    return JSONResponse(status_code=204, content={})
