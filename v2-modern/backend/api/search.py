from fastapi import APIRouter, HTTPException, Query
from core.spotify import get_spotify_client

router = APIRouter()

@router.get("/")
async def search_track(q: str = Query(..., min_length=1)):
    sp = get_spotify_client()
    if not sp:
        return {"results": []}
    
    try:
        results = sp.search(q=q, limit=8, type='track')
        tracks = []
        for track in results['tracks']['items']:
            tracks.append({
                "name": track['name'], 
                "artist": track['artists'][0]['name'], 
                "uri": track['uri'], 
                "img": track['album']['images'][-1]['url'] if track['album']['images'] else ""
            })
        return {"results": tracks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/{uri}")
async def add_to_queue(uri: str):
    sp = get_spotify_client()
    if not sp:
        raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
    
    try:
        sp.add_to_queue(uri)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
