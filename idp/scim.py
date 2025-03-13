from fastapi import APIRouter, HTTPException, Path, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any, Optional
from utilities import auth
from utils import log, LogLevel

# SCIM Schemas
SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
SCIM_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"


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
    schemas: List[str] = [SCIM_USER_SCHEMA]
    active: Optional[bool] = None
    name: Optional[Dict[str, str]] = None
    emails: Optional[List[Dict[str, str]]] = None


class SCIMGroup(BaseModel):
    schemas: List[str] = [SCIM_GROUP_SCHEMA]
    displayName: str = Field(..., title="Group's display name")
    members: Optional[List[Dict[str, str]]] = None
    externalId: Optional[str] = Field(None, title="External identifier for the group")


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
    ### Code To Run ###
    log(LogLevel.DEBUG, f"User created: {user.model_dump()}")
    log(LogLevel.INFO, f"SCIM User POST: {user.userName}")
    return JSONResponse(status_code=201, content={"id": user.externalId, **user.model_dump()})


# Update User
@router.put("/Users/{userId}")
async def update_user(user_id: str, update_data: SCIMUserUpdate, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.DEBUG, f"User updated: {user_id} -> {update_data.model_dump()}")
    log(LogLevel.INFO, f"SCIM User PUT: {user_id}")
    return {update_data}


@router.delete("/Users/{userId}")
async def delete_user(user_id: str, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.INFO, f"User removed: {user_id}")
    return JSONResponse(status_code=204, content={})


# Create Group
@router.post("/Groups")
async def create_group(group: SCIMGroup, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.DEBUG, f"Group created: {group.model_dump()}")
    log(LogLevel.INFO, f"SCIM Group POST: {group.displayName}")
    return JSONResponse(status_code=201, content={"id": group.externalId, **group.model_dump()})


# Update Group Membership
# @router.patch("/Groups/{group_id}", tags=["SCIM"])
# async def modify_group_users(
#         group_id: str = Path(..., title="Group ID"),
#         patch_request: SCIMPatchRequest = None,
#         token: str = Depends(auth.verify_token)
# ):
#     # Validate SCIM Schema
#     if SCIM_GROUP_SCHEMA not in patch_request.schemas:
#         raise HTTPException(status_code=400, detail="Invalid SCIM schema")
#
#     for operation in patch_request.Operations:
#         if operation.path != "members":
#             raise HTTPException(status_code=400, detail="Only 'members' modifications are supported")
#
#         for member in operation.value:
#             user_id = member.get("value")
#             if not user_id:
#                 raise HTTPException(status_code=400, detail="Each member must have a 'value' (user ID)")
#
#             if operation.op == "add":
#                 ### Code To Run ###
#                 log(LogLevel.INFO, f"Adding user {user_id} to group {group_id}")
#
#             elif operation.op == "remove":
#                 ### Code To Run ###
#                 log(LogLevel.INFO, f"Removing user {user_id} from group {group_id}")
#
#             else:
#                 raise HTTPException(status_code=400, detail="Unsupported operation")
#
#     return {"message": "Group updated successfully"}

# Debug Patch Log (use request.json() to get the data)
@router.patch("/Groups/{group_id}")
async def modify_group_users(group_id: str, request: Request, token: str = Depends(auth.verify_token)):
    data = await request.json()
    log(LogLevel.INFO, f"SCIM Group PATCH: {group_id}")
    log(LogLevel.DEBUG, f"Group Patch Request: {data}")
    return JSONResponse(status_code=204, content={})


# Delete Group
@router.delete("/Groups/{groupId}")
async def delete_group(group_id: str, token: str = Depends(auth.verify_token)):
    ### Code To Run ###
    log(LogLevel.INFO, f"Group deleted: {group_id}")
    return JSONResponse(status_code=204, content={})
