import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SPOTIPY_CLIENT_ID: str = os.getenv("SPOTIPY_CLIENT_ID", "")
    SPOTIPY_CLIENT_SECRET: str = os.getenv("SPOTIPY_CLIENT_SECRET", "")
    SPOTIPY_REDIRECT_URI: str = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8080/callback")
    
    ADMIN_NAME: str = os.getenv("ADMIN_NAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    USER_NAME: str = os.getenv("USER_NAME", "user")
    USER_PASSWORD: str = os.getenv("USER_PASSWORD", "user")
    
    FLASK_SECRET: str = os.getenv("FLASK_SECRET", "secret")
    
    class Config:
        env_file = ".env"

settings = Settings()
