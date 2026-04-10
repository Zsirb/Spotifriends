from flask import Flask
import datetime
import pytz
from waitress import serve

app = Flask(__name__)

# HTML sablon fekete háttérrel és középre igazított, élő órával
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Budapest Pontos Idő</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            background-color: #000000;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #ffffff;
            font-family: 'Courier New', Courier, monospace;
        }

        .container {
            text-align: center;
        }

        #clock {
            font-size: 5rem;
            font-weight: bold;
            letter-spacing: 5px;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        }

        .location {
            font-size: 1.2rem;
            color: #888;
            margin-top: 10px;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="location">Budapest</div>
        <div id="clock">00:00:00</div>
    </div>

    <script>
        function updateClock() {
            // Budapest időzóna beállítása
            const options = {
                timeZone: 'Europe/Budapest',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            };
            
            const formatter = new Intl.DateTimeFormat('hu-HU', options);
            document.getElementById('clock').textContent = formatter.format(new Date());
        }

        // Frissítés minden másodpercben
        setInterval(updateClock, 1000);
        updateClock(); // Azonnali indítás
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_TEMPLATE

if __name__ == "__main__":
    PORT = 6767
    print(f"--- ZSIRB IDŐ SZERVER ---")
    print(f"Indítás a http://localhost:{PORT} címen...")
    print(f"Időzóna: Budapest (Europe/Budapest)")
    
    # Production szerver indítása
    serve(app, host='0.0.0.0', port=PORT, threads=2)