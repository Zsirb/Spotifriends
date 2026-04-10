import os
import sys
import socket
import time
import logging
import subprocess
import threading
from functools import wraps
from flask import Flask, request, redirect, render_template_string, jsonify, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Silence Flask/Werkzeug logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Load environment variables
load_dotenv('.env', override=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "nagyon_titkos_kulcs_a_sessionhoz")

# --- SPOTIFY CONFIG ---
SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"
auth_manager = SpotifyOAuth(
    client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
    client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.environ.get("SPOTIPY_REDIRECT_URI"),
    scope=SCOPE,
    show_dialog=False
)

def get_spotify_client():
    token_info = auth_manager.validate_token(auth_manager.get_cached_token())
    if not token_info:
        return None
    return spotipy.Spotify(auth=token_info['access_token'])

def require_password(admin_only=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role = session.get('role')
            if not role:
                return redirect('/web_login')
            if admin_only and role != 'admin':
                return "Unauthorized: Admin access required", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- HTML TEMPLATES ---

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bejelentkezés</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Montserrat', sans-serif; background: #121212; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #181818; padding: 2.5rem; border-radius: 16px; width: 320px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #333; }
        input { width: 100%; padding: 0.8rem; margin: 0.5rem 0; background: #282828; border: 1px solid #333; color: white; border-radius: 8px; outline: none; box-sizing: border-box; transition: border-color 0.2s; }
        input:focus { border-color: #1DB954; }
        button { background: #1DB954; color: white; border: none; padding: 0.8rem 2rem; border-radius: 30px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 1rem; transition: transform 0.1s, background 0.2s; }
        button:active { transform: scale(0.98); background: #1ed760; }
        .error { color: #ff6b6b; font-size: 0.8rem; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Belépés</h1>
        <p style="color: #b3b3b3;">Add meg az adataidat!</p>
        <form action="/web_login" method="post">
            <input type="text" name="username" placeholder="Felhasználónév" autofocus required>
            <input type="password" name="password" placeholder="Jelszó" required>
            {% if error %}<p class="error">Hibás adatok!</p>{% endif %}
            <button type="submit">Belépés</button>
        </form>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Vezérlő</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --spotify-green: #1DB954; --bg-dark: #121212; --card-dark: #181818; --text-light: #FFFFFF; --text-gray: #B3B3B3; --hover-bg: #282828; }
        body { font-family: 'Montserrat', sans-serif; background-color: var(--bg-dark); color: var(--text-light); display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 2rem 0; overflow-x: hidden; }
        
        #bg-container { position: fixed; top: -50px; left: -50px; width: calc(100% + 100px); height: calc(100% + 100px); z-index: -2; background-size: cover; background-position: center; filter: blur(60px) brightness(0.4); transition: background-image 1.2s ease-in-out; }
        #bg-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; background: radial-gradient(circle, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.85) 100%); }

        .player-card { background-color: rgba(24, 24, 24, 0.8); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); padding: 2.5rem; border-radius: 20px; width: 380px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.8); position: relative; border: 1px solid rgba(255,255,255,0.08); transition: transform 0.3s ease; }
        #album-art { width: 250px; height: 250px; background-color: #282828; margin: 0 auto 1.5rem; border-radius: 12px; background-size: cover; background-position: center; box-shadow: 0 12px 30px rgba(0,0,0,0.6); transition: background-image 0.6s ease; }
        
        .track-info h1 { font-size: 1.25rem; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 700; letter-spacing: -0.5px; }
        .track-info p { color: var(--text-gray); font-size: 0.9rem; margin: 0.4rem 0 1.2rem; font-weight: 400; }
        
        .progress-container { margin-bottom: 1.5rem; }
        .time-info { display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-gray); margin-top: 6px; font-weight: 700; }
        
        input[type=range] { width: 100%; height: 5px; accent-color: var(--spotify-green); background: #404040; border-radius: 5px; appearance: none; cursor: pointer; transition: background 0.2s; }
        input[type=range]::-webkit-slider-thumb { appearance: none; width: 12px; height: 12px; background: white; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        
        .controls { display: flex; justify-content: space-around; align-items: center; margin-bottom: 2rem; }
        .btn { background: none; border: none; color: var(--text-light); cursor: pointer; font-size: 1.8rem; transition: transform 0.15s, color 0.2s; outline: none; display: flex; align-items: center; justify-content: center; }
        .btn:hover { color: var(--spotify-green); transform: scale(1.15); }
        .btn:active { transform: scale(0.95); }
        .btn-play { font-size: 3.5rem; color: var(--spotify-green); }
        
        .volume-container { display: flex; align-items: center; gap: 12px; color: var(--text-gray); padding: 0 10px; margin-bottom: 2rem; }
        
        .search-section { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1.5rem; text-align: left; }
        .search-input { width: 100%; padding: 0.9rem 1.1rem; background: rgba(40,40,40,0.6); border: 1px solid transparent; border-radius: 10px; color: white; font-family: inherit; outline: none; transition: all 0.3s; box-sizing: border-box; }
        .search-input:focus { border-color: var(--spotify-green); background: rgba(50,50,50,0.8); }
        
        .results-list { list-style: none; padding: 0; margin-top: 1rem; max-height: 200px; overflow-y: auto; }
        .result-item { display: flex; align-items: center; padding: 0.6rem; border-radius: 8px; cursor: pointer; transition: background 0.2s; margin-bottom: 0.4rem; }
        .result-item:hover { background: var(--hover-bg); }
        .result-img { width: 42px; height: 42px; border-radius: 4px; margin-right: 12px; background-size: cover; flex-shrink: 0; }
        .result-info { flex-grow: 1; min-width: 0; }
        .result-name { font-size: 0.85rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .result-artist { font-size: 0.75rem; color: var(--text-gray); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .add-btn { background: var(--spotify-green); border: none; color: white; border-radius: 50%; width: 26px; height: 26px; cursor: pointer; font-weight: bold; font-size: 1.1rem; flex-shrink: 0; transition: transform 0.1s; }
        .add-btn:active { transform: scale(0.9); }
        
        .status { font-size: 0.8rem; color: var(--spotify-green); margin-top: 12px; min-height: 1.2em; text-align: center; font-weight: 700; }
        .login-btn { display: inline-block; background-color: var(--spotify-green); color: white; text-decoration: none; padding: 1.1rem 2.2rem; border-radius: 40px; font-weight: bold; text-transform: uppercase; letter-spacing: 1.5px; transition: transform 0.2s, background 0.2s; }
        .login-btn:hover { transform: scale(1.05); background: #1ed760; }
        
        .admin-controls { margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1.2rem; }
        .restart-btn { background: rgba(51,51,51,0.6); color: #aaa; border: 1px solid #444; padding: 0.6rem 1.2rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; font-weight: 700; }
        .restart-btn:hover { background: #444; color: white; border-color: #666; }
        
        .logout { position: absolute; top: 15px; right: 15px; color: #666; text-decoration: none; font-size: 0.75rem; font-weight: 700; transition: color 0.2s; }
        .logout:hover { color: #aaa; }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
    </style>
</head>
<body>
    <div id="bg-container"></div>
    <div id="bg-overlay"></div>
    <div class="player-card">
        <a href="/logout" class="logout">Kijelentkezés</a>
        {% if not logged_in %}
            <h1 style="margin-top: 0">Spotify Vezérlő</h1>
            <p style="color: var(--text-gray); margin-bottom: 2.5rem;">Csatlakoztasd a Spotify fiókodat a kezdéshez.</p>
            <a href="/login" class="login-btn">Spotify Csatlakoztatás</a>
        {% else %}
            <div id="album-art"></div>
            <div class="track-info">
                <h1 id="track-name">Betöltés...</h1>
                <p id="artist-name">...</p>
            </div>
            <div class="progress-container">
                <input type="range" class="progress-bar" id="seek-bar" min="0" max="100" value="0" oninput="isSeeking=true" onchange="seek(this.value)">
                <div class="time-info">
                    <span id="current-time">0:00</span>
                    <span id="total-time">0:00</span>
                </div>
            </div>
            <div class="controls">
                <button class="btn" onclick="control('previous')" title="Előző">⏮</button>
                <button class="btn btn-play" id="play-btn" onclick="control('play_pause')" title="Lejátszás/Szünet">▶</button>
                <button class="btn" onclick="control('next')" title="Következő">⏭</button>
            </div>
            <div class="volume-container">
                <span style="font-size: 1.2rem">🔈</span>
                <input type="range" class="vol-slider" id="vol-slider" min="0" max="100" value="50" onchange="setVolume(this.value)">
                <span style="font-size: 1.2rem">🔊</span>
            </div>
            <div class="search-section">
                <input type="text" class="search-input" id="search-box" placeholder="Keresés és hozzáadás..." oninput="searchTrack(this.value)">
                <ul class="results-list" id="results"></ul>
            </div>
            <p class="status" id="status-msg"></p>
            
            {% if role == 'admin' %}
            <div class="admin-controls">
                <button class="restart-btn" onclick="restartServer()">Szerver újraindítása</button>
            </div>
            {% endif %}
        {% endif %}
    </div>

    <script>
        let currentProgress = 0; let duration = 0; let isPlaying = false; let isSeeking = false; let searchTimeout;
        
        function formatTime(ms) { 
            if (!ms || ms < 0) return "0:00"; 
            const min = Math.floor(ms / 60000); 
            const sec = Math.floor((ms % 60000) / 1000); 
            return min + ":" + (sec < 10 ? '0' : '') + sec; 
        }

        async function updateStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                if (data.active) {
                    document.getElementById('track-name').innerText = data.track_name;
                    document.getElementById('artist-name').innerText = data.artist_name;
                    
                    const artUrl = data.album_art || '';
                    if (artUrl) {
                        document.getElementById('album-art').style.backgroundImage = `url(${artUrl})`;
                        document.getElementById('bg-container').style.backgroundImage = `url(${artUrl})`;
                    }
                    
                    document.getElementById('play-btn').innerText = data.is_playing ? '⏸' : '▶';
                    duration = data.duration_ms; 
                    isPlaying = data.is_playing;
                    
                    if (!isSeeking) {
                        // "Jump Protection": Only sync if the difference is > 2 seconds
                        // This prevents the slider from "snapping" every 3 seconds due to network lag
                        if (Math.abs(currentProgress - data.progress_ms) > 2000) {
                            currentProgress = data.progress_ms;
                        }
                        document.getElementById('seek-bar').max = duration; 
                        document.getElementById('total-time').innerText = formatTime(duration);
                        document.getElementById('vol-slider').value = data.volume;
                    }
                }
            } catch (e) { console.error("Status update error", e); }
        }

        // Ultra-smooth progress bar update (every 50ms = 20fps)
        setInterval(() => { 
            if (isPlaying && !isSeeking && currentProgress < duration) { 
                currentProgress += 50; 
                const seekBar = document.getElementById('seek-bar');
                seekBar.value = currentProgress; 
                document.getElementById('current-time').innerText = formatTime(currentProgress); 
            } 
        }, 50);

        // Fetch server status every 3 seconds
        setInterval(updateStatus, 3000); 
        updateStatus();
        
        async function searchTrack(query) {
            clearTimeout(searchTimeout); 
            const list = document.getElementById('results');
            if (query.length < 3) { list.innerHTML = ""; return; }
            
            searchTimeout = setTimeout(async () => {
                const res = await fetch('/api/search/' + encodeURIComponent(query));
                const data = await res.json();
                list.innerHTML = "";
                data.results.forEach(track => {
                    const li = document.createElement('li'); 
                    li.className = 'result-item';
                    li.innerHTML = `
                        <div class="result-img" style="background-image: url('${track.img}')"></div>
                        <div class="result-info">
                            <div class="result-name">${track.name}</div>
                            <div class="result-artist">${track.artist}</div>
                        </div>
                        <button class="add-btn" onclick="addToQueue('${track.uri}', '${track.name.replace(/'/g, "\\'")}')">+</button>`;
                    list.appendChild(li);
                });
            }, 400);
        }

        async function addToQueue(uri, name) {
            const status = document.getElementById('status-msg');
            status.innerText = "Hozzáadás...";
            status.style.color = "var(--text-gray)";
            
            const res = await fetch('/api/queue/' + uri);
            if (res.ok) { 
                status.innerText = `Hozzáadva: ${name}`; 
                status.style.color = "var(--spotify-green)"; 
                document.getElementById('search-box').value = ""; 
                document.getElementById('results').innerHTML = ""; 
            } else { 
                status.innerText = "Hiba a hozzáadáskor."; 
                status.style.color = "#ff6b6b"; 
            }
            setTimeout(() => status.innerText = "", 4000);
        }

        async function control(action) { 
            await fetch('/control/' + action); 
            setTimeout(updateStatus, 300); // Small delay to allow Spotify to update
        }

        async function seek(val) { 
            isSeeking = false; 
            currentProgress = parseInt(val);
            await fetch('/seek/' + val); 
        }

        async function setVolume(val) { 
            await fetch('/volume/' + val); 
        }

        async function restartServer() {
            if (confirm("Biztosan újraindítod a szervert?")) {
                document.body.innerHTML = `
                    <div style="text-align:center; margin-top: 20vh">
                        <h1 style="color:var(--spotify-green)">Szerver újraindul...</h1>
                        <p style="color:#aaa">Kérlek várj kb. 10 másodpercet, majd frissíts rá az oldalra.</p>
                    </div>`;
                fetch('/api/restart');
                setTimeout(() => location.reload(), 12000);
            }
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/web_login', methods=['GET', 'POST'])
def web_login():
    if request.method == 'POST':
        uname = request.form.get('username')
        pwd = request.form.get('password')
        
        if uname == os.environ.get('ADMIN_NAME') and pwd == os.environ.get('ADMIN_PASSWORD'):
            session['role'] = 'admin'
            return redirect('/')
        elif uname == os.environ.get('USER_NAME') and pwd == os.environ.get('USER_PASSWORD'):
            session['role'] = 'user'
            return redirect('/')
            
        return render_template_string(LOGIN_PAGE, error=True)
    return render_template_string(LOGIN_PAGE, error=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/web_login')

@app.route('/')
@require_password()
def index():
    sp = get_spotify_client()
    return render_template_string(HTML_TEMPLATE, logged_in=(sp is not None), role=session.get('role'))

@app.route('/api/status')
@require_password()
def api_status():
    sp = get_spotify_client()
    if not sp: return jsonify({"active": False})
    try:
        current = sp.current_playback()
        if current and current['item']:
            track = current['item']
            return jsonify({
                "active": True,
                "track_name": track['name'],
                "artist_name": track['artists'][0]['name'],
                "album_art": track['album']['images'][0]['url'] if track['album']['images'] else "",
                "is_playing": current['is_playing'],
                "volume": current['device']['volume_percent'],
                "progress_ms": current['progress_ms'],
                "duration_ms": track['duration_ms']
            })
    except: pass
    return jsonify({"active": False})

@app.route('/api/search/<query>')
@require_password()
def api_search(query):
    sp = get_spotify_client()
    if not sp: return jsonify({"results": []})
    results = sp.search(q=query, limit=8, type='track')
    tracks = []
    for track in results['tracks']['items']:
        tracks.append({
            "name": track['name'], 
            "artist": track['artists'][0]['name'], 
            "uri": track['uri'], 
            "img": track['album']['images'][-1]['url'] if track['album']['images'] else ""
        })
    return jsonify({"results": tracks})

@app.route('/api/queue/<uri>')
@require_password()
def api_queue(uri):
    sp = get_spotify_client()
    if not sp: return "Error", 401
    try:
        sp.add_to_queue(uri)
        return "OK"
    except: return "Error", 404

@app.route('/api/devices')
@require_password(admin_only=True)
def api_devices():
    sp = get_spotify_client()
    if not sp: return jsonify({"devices": []})
    try:
        return jsonify(sp.devices())
    except: return jsonify({"devices": []})

@app.route('/api/transfer/<device_id>')
@require_password(admin_only=True)
def api_transfer(device_id):
    sp = get_spotify_client()
    if not sp: return "Error", 401
    try:
        sp.transfer_playback(device_id, force_play=True)
        return "OK"
    except: return "Error", 404

@app.route('/api/restart')
@require_password(admin_only=True)
def api_restart():
    def restart():
        time.sleep(1)
        subprocess.Popen([sys.executable] + sys.argv, close_fds=True)
        os._exit(0)
    
    threading.Thread(target=restart).start()
    return "Restarting..."

@app.route('/login')
@require_password()
def login():
    return redirect(auth_manager.get_authorize_url())

@app.route('/callback')
def callback():
    auth_manager.get_access_token(request.args.get("code"))
    return redirect('/')

@app.route('/control/<action>')
@require_password()
def playback_control(action):
    sp = get_spotify_client()
    if not sp: return "Error", 401
    try:
        if action == 'play_pause':
            curr = sp.current_playback()
            if curr and curr['is_playing']: sp.pause_playback()
            else: sp.start_playback()
        elif action == 'next': sp.next_track()
        elif action == 'previous': sp.previous_track()
        return "OK"
    except: return "No device", 404

@app.route('/seek/<int:pos_ms>')
@require_password()
def seek_control(pos_ms):
    sp = get_spotify_client()
    if sp:
        try: 
            sp.seek_track(pos_ms)
            return "OK"
        except: return "Error", 404
    return "Error", 401

@app.route('/volume/<int:percent>')
@require_password()
def volume_control(percent):
    sp = get_spotify_client()
    if sp:
        try: 
            sp.volume(percent)
            return "OK"
        except: return "Error", 404
    return "Error", 401

# --- MAIN BLOCK ---

if __name__ == '__main__':
    port = 8080
    mypid = os.getpid()
    
    # Port cleanup
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.close()
    except socket.error:
        print(f"\n[PORT] A {port} port foglalt. Felszabadítás...")
        if sys.platform != "win32":
            os.system(f"lsof -ti:{port} | grep -v {mypid} | xargs kill -9 2>/dev/null")
            time.sleep(1)

    # Local IP detection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except: local_ip = "localhost"

    print(f"Helyi elérés: http://{local_ip}:{port}")
    print(f"Gép elérése:  http://localhost:{port}")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=port, threaded=True)
