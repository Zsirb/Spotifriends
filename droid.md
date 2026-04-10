# Spotifriends v2: Authentication & API Architecture 🎵

## 1. API Key Strategy (Single Developer Key)
**CRITICAL RULE:** End-users will **never** generate, see, or input their own Spotify API keys. 
The application relies entirely on a single master "Client ID" and "Client Secret" owned by the developer.

* **Developer Setup:** The developer registers "Spotifriends v2" in the Spotify Developer Dashboard.
* **Secure Storage:** The resulting `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are stored securely as environment variables (e.g., in a `.env` file) on the **FastAPI backend**. These keys must never be hardcoded or exposed to the React frontend.

## 2. User Login Flow (OAuth 2.0)
When a user clicks **"Spotify Csatlakoztatás"** (Connect Spotify), the system executes a standard OAuth 2.0 Authorization Code flow. The CLI should implement the following steps:

1.  **Trigger:** User clicks the connection button on the React/Vite frontend.
2.  **Redirect:** The frontend hits a FastAPI endpoint (e.g., `/api/auth/login`). The backend uses the master `SPOTIFY_CLIENT_ID` to generate a Spotify authorization URL and redirects the user's browser to Spotify's official, secure login page.
3.  **User Action:** The user logs in with their standard Spotify email and password on Spotify's servers and clicks "Agree" to grant Spotifriends v2 permission to control their playback.
4.  **Callback:** Spotify redirects the user back to a FastAPI callback URL (e.g., `/api/auth/callback`) along with a temporary authorization `code`.
5.  **Token Exchange:** FastAPI securely sends this `code`, along with the `SPOTIFY_CLIENT_SECRET`, back to Spotify. Spotify responds with an **Access Token** and a **Refresh Token** bound to that specific user.
6.  **Session Management:** FastAPI stores these tokens (in a database or via secure HTTP-only cookies) and returns a session state to the frontend.
7.  **Action Execution:** When the user searches, plays, or skips, the frontend tells FastAPI. FastAPI grabs that user's specific Access Token, attaches it to the request, and forwards it to the Spotify Web API.

## 3. Deployment Constraints & The 25-User Limit
When deploying this application (e.g., via Cloudflare Tunnels to `zsirb.hu`), the following Spotify API limitations must be accounted for:

* **Development Mode:** All new Spotify API applications start in "Development Mode."
* **The Limit:** In this mode, the app is strictly capped at a maximum of **25 unique users**.
* **Whitelisting Required:** For any user to successfully complete the "Spotify Csatlakoztatás" flow, the developer **must manually add** the user's registered Spotify email address to the "User Management" section of the Spotify Developer Dashboard.
* **Error Handling:** The CLI should implement frontend error handling for unauthorized users (those not on the 25-person whitelist), politely informing them that the app is currently in a closed beta or limited deployment.