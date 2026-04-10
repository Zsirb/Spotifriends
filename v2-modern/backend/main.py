from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, playback, search
import uvicorn

app = FastAPI(title="Spotifriends API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://zsirb.hu", "http://zsirb.hu"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(playback.router, prefix="/api/playback", tags=["playback"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "Spotifriends API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
