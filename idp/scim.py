# /scim/v2/Users
# /scim/v2/Users/{user_id}
# /scim/v2/Groups
# /scim/v2/Groups/{group_id}

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Literal, Dict, Any

# SCIM Patch operation model
class PatchOperation(BaseModel):
    op: Literal["add", "remove"]
    path: str = "members"
    value: List[Dict[str, Any]]

class SCIMPatchRequest(BaseModel):
    schemas: List[str]
    Operations: List[PatchOperation]

SCIM_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"

router = APIRouter()

@router.get("/ServiceProviderConfig", tags=["SCIM"])
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
            "meta": {
                "resourceType": "ServiceProviderConfig",
                "location": "/ServiceProviderConfig"
            }
        }
    )

@router.patch("/Groups/{group_id}", tags=["SCIM"])
async def modify_group_users(
    group_id: str = Path(..., title="Group ID"),
    patch_request: SCIMPatchRequest = None
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
                print(f"Adding user {user_id} to group {group_id}")

            elif operation.op == "remove":
                ### Code To Run ###
                print(f"Removing user {user_id} from group {group_id}")

            else:
                raise HTTPException(status_code=400, detail="Unsupported operation")

    return {"message": "Group updated successfully"}
