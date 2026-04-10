import spotipy
from spotipy.oauth2 import SpotifyOAuth
from core.config import settings

SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

auth_manager = SpotifyOAuth(
    client_id=settings.SPOTIPY_CLIENT_ID,
    client_secret=settings.SPOTIPY_CLIENT_SECRET,
    redirect_uri=settings.SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    show_dialog=False
)

def get_spotify_client():
    token_info = auth_manager.validate_token(auth_manager.get_cached_token())
    if not token_info:
        return None
    return spotipy.Spotify(auth=token_info['access_token'])
