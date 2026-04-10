from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.database import get_db, User, init_db
from core.spotify import get_auth_manager
from core.config import settings
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import jwt
import datetime
import json

router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = settings.FLASK_SECRET # Reusing for JWT
ALGORITHM = "HS256"

class AuthRequest(BaseModel):
    username: str
    password: str

# Dependency to get current user from JWT
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        user = db.query(User).filter(User.username == username).first()
        return user
    except:
        return None

@router.post("/register")
async def register(data: AuthRequest, db: Session = Depends(get_db)):
    try:
        print(f"Registration attempt for: {data.username}")
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(status_code=400, detail="Már létező felhasználónév!")
        
        # Bcrypt has a 72-byte limit for passwords
        truncated_password = data.password[:72]
        hashed = pwd_context.hash(truncated_password)
        new_user = User(username=data.username, hashed_password=hashed)
        db.add(new_user)
        db.commit()
        print(f"Successfully registered: {data.username}")
        return {"status": "success", "message": "Regisztráció sikeres!"}
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Szerver hiba: {str(e)}")

@router.post("/login")
async def login(data: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Hibás adatok!")
    
    # Generate JWT
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    token = jwt.encode({"sub": user.username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="session_token", value=token, httponly=True)
    return {"status": "success", "token": token} # Frontend uses cookie mostly

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("session_token")
    return response

@router.delete("/account")
async def delete_account(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401)
    db.delete(user)
    db.commit()
    return {"status": "success"}

@router.get("/spotify/login")
async def spotify_login(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    # Store user ID in state to link back after callback
    auth_manager = get_auth_manager()
    return {"url": auth_manager.get_authorize_url(state=user.username)}

@router.get("/spotify/callback")
async def spotify_callback(code: str, state: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == state).first()
    if not user:
        return RedirectResponse(url=f"https://zsirb.hu/?error=UserNotFound")
    
    try:
        auth_manager = get_auth_manager()
        token_info = auth_manager.get_access_token(code)
        user.spotify_token = json.dumps(token_info)
        db.commit()
        return RedirectResponse(url="https://zsirb.hu/")
    except Exception as e:
        return RedirectResponse(url=f"https://zsirb.hu/?error={str(e)}")

@router.get("/spotify/logout")
async def spotify_logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401)
    user.spotify_token = None
    db.commit()
    return {"status": "success"}
