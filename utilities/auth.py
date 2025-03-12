from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import WEBHOOK_SECRET

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme")

    if credentials.credentials != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid token")

    return credentials.credentials
