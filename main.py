from fastapi import FastAPI, APIRouter, Request, Depends, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from utils import bcolors, LogLevel, log
from config import IDP_GROUP_TO_ROOM

from idp import scim
import webhook

print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Starting Synapse Group Sync")

print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Loaded Mappings:")

for mapped_group in IDP_GROUP_TO_ROOM:
    print(
        f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Group: {mapped_group} {bcolors.OKBLUE}->{bcolors.ENDC} Rooms: {IDP_GROUP_TO_ROOM[mapped_group]}")
app = FastAPI()

router = APIRouter()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log(LogLevel.ERROR, f"Validation error:\n{exc}")
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"error": "Validation error"})


@router.get("/", tags=["root"])
async def root():
    return {"status": "success"}


@router.get("/health", tags=["health"])
async def health():
    return {"status": "success"}


app.include_router(router)
app.include_router(webhook.router)
app.include_router(scim.router, prefix="/scim/v2")
