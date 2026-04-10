from fastapi import APIRouter, HTTPException, Query
from core.spotify import get_spotify_client
from typing import Optional

router = APIRouter()

@router.get("/status")
async def get_status():
    sp = get_spotify_client()
    if not sp:
        return {"active": False, "authenticated": False}
    
    try:
        current = sp.current_playback()
        if current and current['item']:
            track = current['item']
            return {
                "active": True,
                "authenticated": True,
                "track_name": track['name'],
                "artist_name": track['artists'][0]['name'],
                "album_art": track['album']['images'][0]['url'] if track['album']['images'] else "",
                "is_playing": current['is_playing'],
                "volume": current['device']['volume_percent'],
                "progress_ms": current['progress_ms'],
                "duration_ms": track['duration_ms']
            }
    except Exception as e:
        print(f"Status error: {e}")
    
    return {"active": False, "authenticated": True}

@router.get("/control/{action}")
async def control_playback(action: str):
    sp = get_spotify_client()
    if not sp:
        raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
    
    try:
        if action == 'play_pause':
            curr = sp.current_playback()
            if curr and curr['is_playing']:
                sp.pause_playback()
            else:
                sp.start_playback()
        elif action == 'next':
            sp.next_track()
        elif action == 'previous':
            sp.previous_track()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/seek/{pos_ms}")
async def seek_playback(pos_ms: int):
    sp = get_spotify_client()
    if not sp:
        raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
    try:
        sp.seek_track(pos_ms)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/volume/{percent}")
async def set_volume(percent: int):
    sp = get_spotify_client()
    if not sp:
        raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
    try:
        sp.volume(percent)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
