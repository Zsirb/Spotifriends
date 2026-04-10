import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (backend root)
backend_root = os.path.dirname(current_dir)
# Load .env from the backend root
env_path = os.path.join(backend_root, '.env')
load_dotenv(env_path)

class Settings(BaseSettings):
    SPOTIPY_CLIENT_ID: str = os.getenv("SPOTIPY_CLIENT_ID", "")
    SPOTIPY_CLIENT_SECRET: str = os.getenv("SPOTIPY_CLIENT_SECRET", "")
    SPOTIPY_REDIRECT_URI: str = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8000/api/auth/spotify/callback")
    
    ADMIN_NAME: str = os.getenv("ADMIN_NAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    USER_NAME: str = os.getenv("USER_NAME", "user")
    USER_PASSWORD: str = os.getenv("USER_PASSWORD", "user")
    
    FLASK_SECRET: str = os.getenv("FLASK_SECRET", "secret")
    
    class Config:
        env_file = ".env"

settings = Settings()
