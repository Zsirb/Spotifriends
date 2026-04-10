from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from core.spotify import auth_manager
from core.config import settings
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def web_login(data: LoginRequest, request: Request):
    print(f"Login attempt: user={data.username}, pass={data.password}")
    if data.username == settings.ADMIN_NAME and data.password == settings.ADMIN_PASSWORD:
        return {"status": "success", "role": "admin"}
    elif data.username == settings.USER_NAME and data.password == settings.USER_PASSWORD:
        return {"status": "success", "role": "user"}
    
    print(f"Login failed! Expected: {settings.ADMIN_NAME}/{settings.ADMIN_PASSWORD} or {settings.USER_NAME}/{settings.USER_PASSWORD}")
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/spotify/login")
async def spotify_login():
    return {"url": auth_manager.get_authorize_url()}

@router.get("/spotify/callback")
@router.get("/spotify/callback/")
async def spotify_callback(request: Request, code: Optional[str] = None, error: Optional[str] = None):
    print(f"Callback received! Query params: {request.query_params}")
    if error:
        return {"error": error, "detail": "Spotify returned an error"}
    
    if not code:
        return {"error": "Missing code", "detail": f"No authorization code received from Spotify. Current params: {request.query_params}"}
    
    try:
        auth_manager.get_access_token(code)
        return RedirectResponse(url="http://localhost:5173/")
    except Exception as e:
        return {"error": "Token error", "detail": str(e)}
