from fastapi import Depends, HTTPException, Security
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from app.settings import settings

bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer),
):
    if credentials.credentials != settings.API_TOKEN.get_secret_value():
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user": "admin"}
