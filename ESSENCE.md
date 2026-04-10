# Spotifriends v2 🎵

## The Essence
Spotifriends is a modern, web-based remote control for Spotify, designed to bring a sleek, shared-listening experience to any device. It bridges the gap between a high-end music player and a social queueing system, allowing users to control playback, search the entire Spotify library, and manage the "vibe" through a dark-themed, immersive interface.

## Core Philosophy
- **Minimalist Aesthetics**: Inspired by Spotify's deep-black and neon-green palette, the UI uses glassmorphism and blurred album art backgrounds to create a feeling of "living" music.
- **Accessibility**: Built to be fully responsive, ensuring that whether you're on a desktop or a phone, you have total control over the music.
- **Simplified Control**: Removing the clutter of the full Spotify app to focus on what matters: **Play, Skip, Volume, and Search.**

## The Hungarian Interface (A Szövegezés)
The project is localized in Hungarian to provide a familiar and friendly environment:
- **"Belépés"** (Login): A secure gateway for users and admins.
- **"Keresés és hozzáadás..."** (Search and add): A unified bar to find any track and instantly push it to the active queue.
- **"Spotify Csatlakoztatás"** (Spotify Connection): The bridge to the user's musical world.
- **"Nincs lejátszás"** (No playback): A clean state for when the music stops.

## Technical Foundation
- **Frontend**: A lightning-fast **React 18** application powered by **Vite**, using **Tailwind CSS** for a fluid, modern layout.
- **Backend**: A robust **FastAPI** server that communicates securely with the Spotify Web API.
- **Security**: Role-based access (Admin vs. User) ensuring only authorized friends can manage the server or the playlist.
- **Connectivity**: Designed for the modern web with full support for **Cloudflare Tunnels** and custom domains like `zsirb.hu`.

---
*Created with ❤️ for music lovers who want to share the remote.*
