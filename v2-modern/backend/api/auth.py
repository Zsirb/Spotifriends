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
    if data.username == settings.ADMIN_NAME and data.password == settings.ADMIN_PASSWORD:
        return {"status": "success", "role": "admin"}
    elif data.username == settings.USER_NAME and data.password == settings.USER_PASSWORD:
        return {"status": "success", "role": "user"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/spotify/login")
async def spotify_login():
    return {"url": auth_manager.get_authorize_url()}

@router.get("/spotify/callback")
async def spotify_callback(code: str):
    auth_manager.get_access_token(code)
    return RedirectResponse(url="http://localhost:5173/")
