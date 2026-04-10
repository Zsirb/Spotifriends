import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
from core.config import settings
from core.database import User

SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

def get_auth_manager():
    return SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True
    )

def get_spotify_client(user: User):
    if not user.spotify_token:
        return None
    
    token_info = json.loads(user.spotify_token)
    auth_manager = get_auth_manager()
    
    # Refresh token if expired
    if auth_manager.is_token_expired(token_info):
        token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
        # Token update is handled in auth callback or on-the-fly if needed
        # For simplicity, we assume caller updates user object in DB if token changed
        
    return spotipy.Spotify(auth=token_info['access_token'])
