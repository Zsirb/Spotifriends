# Spotifriends

## Project Overview
Spotifriends is a Python-based web application that provides a custom interface for controlling Spotify playback. It consists of two main components:
- **`spotifriends.py`**: A Flask-based web application that allows users to log in with Spotify, control playback (play/pause, next, previous, seek, volume), and search for tracks to add to the queue. It uses `spotipy` for Spotify API interaction and is designed to be exposed via a Cloudflare tunnel.
- **`main.py`**: A secondary Flask application that displays a simple "Budapest Pontos Idő" (Budapest Exact Time) clock.

The project uses a dark theme inspired by Spotify's aesthetic and includes an admin-only role for server management tasks like restarting the application.

## Technologies
- **Backend**: Python, Flask, Waitress (for `main.py`)
- **APIs**: Spotify Web API (via `spotipy`)
- **Tunneling**: Cloudflare Tunnel (External setup)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **Environment Management**: `python-dotenv`

## Building and Running

### Prerequisites
- Python 3.x
- A Spotify Developer account and a registered application (for `client_id`, `client_secret`, and `redirect_uri`).
- Cloudflare `cloudflared` CLI installed and configured for tunneling.

### Environment Setup
Create a `.env` file in the root directory with the following variables:
```env
# Spotify Configuration
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8080/callback

# Application Credentials
ADMIN_NAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
USER_NAME=your_user_username
USER_PASSWORD=your_user_password
FLASK_SECRET=your_flask_secret_key
```

### Key Commands
- **Run Spotify Controller**: `python spotifriends.py`
  - This starts the Flask server on port 8080.
- **Run Time Server**: `python main.py`
  - This starts a Waitress server on port 6767.
- **Install Dependencies**: 
  ```bash
  pip install flask spotipy python-dotenv waitress
  ```

## Development Conventions
- **Authentication**: The application uses a custom `require_password` decorator for session-based authentication and role-based access control (Admin vs. User).
- **Frontend**: UI is embedded directly as string templates within the Python files for simplicity.
- **Logging**: Flask/Werkzeug logs are silenced in `spotifriends.py` to keep the console output clean.
- **Error Handling**: Basic try-except blocks are used around Spotify API calls to handle cases where no active device is found.
