from fastapi import APIRouter, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional
from utilities import auth
from utils import log, LogLevel

# SCIM Schemas
SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
SCIM_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"

# Models
class SCIMUser(BaseModel):
    schemas: List[str] = [SCIM_USER_SCHEMA]
    userName: str
    name: Dict[str, str]
    emails: List[Dict[str, str]]
    active: bool = True
    externalId: Optional[str] = None

class SCIMUserUpdate(BaseModel):
    schemas: List[str] = [SCIM_USER_SCHEMA]
    active: Optional[bool] = None
    name: Optional[Dict[str, str]] = None
    emails: Optional[List[Dict[str, str]]] = None

class SCIMGroup(BaseModel):
    schemas: List[str] = [SCIM_GROUP_SCHEMA]
    displayName: str
    members: Optional[List[Dict[str, str]]] = None

class PatchOperation(BaseModel):
    op: str
    path: Optional[str] = "members"
    value: Optional[List[Dict[str, Any]]] = None

class SCIMPatchRequest(BaseModel):
    schemas: List[str]
    Operations: List[PatchOperation]


router = APIRouter()

@router.get("/ServiceProviderConfig")
async def service_provider_config():
    return JSONResponse(
        content={
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
            "patch": {"supported": True},
            "bulk": {"supported": False},
            "filter": {"supported": False},
            "changePassword": {"supported": False},
            "sort": {"supported": False},
            "etag": {"supported": False},
            "authenticationSchemes": [],
            "meta": {"resourceType": "ServiceProviderConfig", "location": "/ServiceProviderConfig"}
        }
    )

# Create User
@router.post("/Users")
async def create_user(user: SCIMUser, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.INFO, "User created: {user}")
    return JSONResponse(status_code=201, content=user)

# Update User
@router.put("/Users/{userId}")
async def update_user(user_id: str, update_data: SCIMUserUpdate, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.INFO, "User updated: {user_id} -> {update_data}")
    return {update_data}


@router.delete("/Users/{userId}")
async def delete_user(user_id: str, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.INFO, "User removed: {user_id}")
    return JSONResponse(status_code=204, content={})

# Create Group
@router.post("/Groups")
async def create_group(group: SCIMGroup, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.INFO, "Group created: {group}")
    return JSONResponse(status_code=201, content=group)

# Update Group Membership
@router.patch("/Groups/{group_id}", tags=["SCIM"])
async def modify_group_users(
    group_id: str = Path(..., title="Group ID"),
    patch_request: SCIMPatchRequest = None,
    token: str = Depends(auth.verify_token)
):
    # Validate SCIM Schema
    if SCIM_GROUP_SCHEMA not in patch_request.schemas:
        raise HTTPException(status_code=400, detail="Invalid SCIM schema")

    for operation in patch_request.Operations:
        if operation.path != "members":
            raise HTTPException(status_code=400, detail="Only 'members' modifications are supported")

        for member in operation.value:
            user_id = member.get("value")
            if not user_id:
                raise HTTPException(status_code=400, detail="Each member must have a 'value' (user ID)")

            if operation.op == "add":
                ### Code To Run ###
                log(LogLevel.INFO, "Adding user {user_id} to group {group_id}")

            elif operation.op == "remove":
                ### Code To Run ###
                log(LogLevel.INFO, "Removing user {user_id} from group {group_id}")

            else:
                raise HTTPException(status_code=400, detail="Unsupported operation")

    return {"message": "Group updated successfully"}

# Delete Group
@router.delete("/Groups/{groupId}")
async def delete_group(group_id: str, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.INFO, "Group deleted: {group_id}")
    return JSONResponse(status_code=204, content={})