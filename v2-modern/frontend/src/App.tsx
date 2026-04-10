import React, { useState, useEffect, useCallback } from 'react';
import { 
  Play, Pause, SkipBack, SkipForward, Volume2, Search, Plus, LogOut, ExternalLink, User as UserIcon, Trash2
} from 'lucide-react';
import { authApi, playbackApi, searchApi } from './services/api';

interface PlaybackStatus {
  active: boolean;
  authenticated: boolean;
  is_logged_in: boolean;
  username?: string;
  track_name?: string;
  artist_name?: string;
  album_art?: string;
  is_playing?: boolean;
  volume?: number;
  progress_ms?: number;
  duration_ms?: number;
}

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [status, setStatus] = useState<PlaybackStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isSeeking, setIsSeeking] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const error = params.get('error');
    if (error) {
      setAuthError(error);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Check initial login status
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const { data } = await playbackApi.getStatus();
      setStatus(data);
      setIsLoggedIn(data.is_logged_in);
      if (!isSeeking && data.progress_ms !== undefined) {
        setCurrentProgress(data.progress_ms);
      }
    } catch (err) {
      console.error('Status fetch error', err);
    }
  };

  useEffect(() => {
    if (!isLoggedIn) return;
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [isLoggedIn, isSeeking]);

  useEffect(() => {
    if (status?.is_playing && !isSeeking) {
      const interval = setInterval(() => {
        setCurrentProgress(prev => {
          if (status.duration_ms && prev < status.duration_ms) {
            return prev + 100;
          }
          return prev;
        });
      }, 100);
      return () => clearInterval(interval);
    }
  }, [status?.is_playing, isSeeking, status?.duration_ms]);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (authMode === 'login') {
        await authApi.login(credentials);
      } else {
        await authApi.register(credentials);
        alert('Sikeres regisztráció! Most jelentkezz be.');
        setAuthMode('login');
        return;
      }
      setIsLoggedIn(true);
      fetchStatus();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Hiba történt!');
    }
  };

  const handleLogout = async () => {
    await authApi.logout();
    setIsLoggedIn(false);
    setStatus(null);
  };

  const handleDeleteAccount = async () => {
    if (window.confirm('Biztosan törlöd a fiókodat? Minden Spotify kapcsolatod elveszik!')) {
      await authApi.deleteAccount();
      handleLogout();
    }
  };

  const connectSpotify = async () => {
    const { data } = await authApi.getSpotifyLoginUrl();
    window.location.href = data.url;
  };

  const handleControl = async (action: string) => {
    await playbackApi.control(action);
  };

  const handleSeekEnd = async (e: React.ChangeEvent<HTMLInputElement>) => {
    await playbackApi.seek(parseInt(e.target.value));
    setIsSeeking(false);
  };

  const handleSpotifyLogout = async () => {
    await authApi.logoutSpotify();
    fetchStatus();
  };

  const handleSearch = useCallback(async (q: string) => {
    setSearchQuery(q);
    if (q.length < 3) {
      setSearchResults([]);
      return;
    }
    try {
      const { data } = await searchApi.search(q);
      setSearchResults(data.results);
    } catch (err) {
      console.error('Search error', err);
    }
  }, []);

  const addToQueue = async (uri: string) => {
    await searchApi.addToQueue(uri);
    setSearchQuery('');
    setSearchResults([]);
  };

  const formatTime = (ms: number) => {
    const min = Math.floor(ms / 60000);
    const sec = Math.floor((ms % 60000) / 1000);
    return `${min}:${sec < 10 ? '0' : ''}${sec}`;
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center text-white font-sans p-4">
        <div className="bg-[#181818] p-8 rounded-2xl w-full max-w-sm border border-white/10 shadow-2xl">
          <h1 className="text-3xl font-bold mb-6 text-center">
            {authMode === 'login' ? 'Belépés' : 'Regisztráció'}
          </h1>
          <form onSubmit={handleAuth} className="space-y-4">
            <input 
              type="text" 
              placeholder="Felhasználónév"
              className="w-full bg-[#282828] p-3 rounded-lg outline-none focus:ring-2 focus:ring-[#1DB954]"
              value={credentials.username}
              onChange={e => setCredentials({...credentials, username: e.target.value})}
            />
            <input 
              type="password" 
              placeholder="Jelszó"
              className="w-full bg-[#282828] p-3 rounded-lg outline-none focus:ring-2 focus:ring-[#1DB954]"
              value={credentials.password}
              onChange={e => setCredentials({...credentials, password: e.target.value})}
            />
            <button className="w-full bg-[#1DB954] p-3 rounded-full font-bold hover:scale-105 transition-transform">
              {authMode === 'login' ? 'Belépés' : 'Regisztráció'}
            </button>
          </form>
          <button 
            onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
            className="w-full mt-4 text-sm text-gray-500 hover:text-white"
          >
            {authMode === 'login' ? 'Nincs még fiókod? Regisztrálj!' : 'Már van fiókod? Lépj be!'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#121212] text-white font-sans p-4 md:p-8 flex flex-col items-center relative">
      <div 
        className="fixed inset-0 z-0 opacity-20 blur-[100px] transition-all duration-1000"
        style={{ backgroundImage: status?.album_art ? `url(${status.album_art})` : 'none', backgroundSize: 'cover', backgroundPosition: 'center' }}
      />

      <div className="z-10 w-full max-w-md flex flex-col items-center space-y-8 pb-12">
        <div className="flex justify-between w-full items-center">
          <div className="flex flex-col">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Spotifriends v2</span>
            <span className="text-[10px] text-[#1DB954] flex items-center gap-1 font-bold">
              <UserIcon size={10} /> {status?.username}
            </span>
          </div>
          <div className="flex items-center gap-4">
            {status?.authenticated && (
              <button 
                onClick={handleSpotifyLogout} 
                className="text-gray-500 hover:text-[#1DB954] transition-colors text-xs font-bold uppercase tracking-tight flex items-center gap-1"
              >
                Váltás <ExternalLink size={14} />
              </button>
            )}
            <button onClick={handleDeleteAccount} className="text-gray-500 hover:text-red-500 transition-colors" title="Fiók törlése">
              <Trash2 size={20} />
            </button>
            <button onClick={handleLogout} className="text-gray-500 hover:text-white transition-colors" title="Kijelentkezés">
              <LogOut size={20} />
            </button>
          </div>
        </div>

        {!status?.authenticated ? (
          <div className="text-center space-y-6 pt-12">
            <h1 className="text-3xl font-bold">Spotify Csatlakoztatás</h1>
            <p className="text-gray-400">Csatlakoztasd a fiókodat a vezérléshez.</p>
            {authError && <div className="bg-red-500/20 border border-red-500/50 p-4 rounded-xl text-red-200 text-sm">Hiba: {authError}</div>}
            <button onClick={connectSpotify} className="bg-[#1DB954] px-8 py-4 rounded-full font-bold text-lg hover:scale-105 transition-transform inline-flex items-center gap-2">
              Connect Spotify <ExternalLink size={20} />
            </button>
            <div className="pt-8 text-xs text-gray-500 max-w-xs mx-auto space-y-2">
              <p>📍 <strong>Zárt Béta Információ:</strong></p>
              <p>Az alkalmazás maximum 25 felhasználót engedélyez.</p>
              <p>Ha az "access_denied" hibát látod, a fiókod nincs a fehérlistán!</p>
            </div>
          </div>
        ) : (
          <>
            <div className="w-full bg-white/5 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white/5">
              <div className="aspect-square w-full rounded-xl overflow-hidden shadow-2xl mb-6 bg-[#282828]">
                {status?.album_art ? <img src={status.album_art} alt="Album Art" className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-600">Nincs lejátszás</div>}
              </div>
              <div className="text-center mb-6">
                <h1 className="text-xl font-bold truncate">{status?.track_name || 'Ismeretlen szám'}</h1>
                <p className="text-gray-400 truncate">{status?.artist_name || 'Ismeretlen előadó'}</p>
              </div>
              <div className="space-y-2">
                <input type="range" min="0" max={status?.duration_ms || 100} value={currentProgress} onChange={e => setCurrentProgress(parseInt(e.target.value))} onMouseUp={handleSeekEnd} onTouchEnd={handleSeekEnd} className="w-full h-1 bg-white/20 rounded-lg appearance-none cursor-pointer accent-[#1DB954]" />
                <div className="flex justify-between text-[10px] font-bold text-gray-500"><span>{formatTime(currentProgress)}</span><span>{status?.duration_ms ? formatTime(status.duration_ms) : '0:00'}</span></div>
              </div>
              <div className="flex items-center justify-around mt-6">
                <button onClick={() => handleControl('previous')} className="hover:text-[#1DB954] transition-colors"><SkipBack size={32} /></button>
                <button onClick={() => handleControl('play_pause')} className="bg-white text-black p-4 rounded-full hover:scale-110 transition-transform">{status?.is_playing ? <Pause size={32} fill="black" /> : <Play size={32} fill="black" />}</button>
                <button onClick={() => handleControl('next')} className="hover:text-[#1DB954] transition-colors"><SkipForward size={32} /></button>
              </div>
              <div className="flex items-center gap-4 mt-8 px-4 text-gray-400">
                <Volume2 size={20} />
                <input type="range" min="0" max="100" defaultValue={status?.volume || 50} onMouseUp={(e) => playbackApi.setVolume(parseInt((e.target as HTMLInputElement).value))} className="w-full h-1 bg-white/20 rounded-lg appearance-none cursor-pointer accent-white" />
              </div>
            </div>
            <div className="w-full relative">
              <div className="relative"><Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} /><input type="text" placeholder="Keresés és hozzáadás..." className="w-full bg-white/5 border border-white/5 p-4 pl-12 rounded-2xl outline-none focus:ring-2 focus:ring-[#1DB954] transition-all" value={searchQuery} onChange={e => handleSearch(e.target.value)} /></div>
              {searchResults.length > 0 && (
                <div className="w-full mt-4 bg-[#282828] rounded-2xl shadow-2xl z-20 border border-white/10">
                  {searchResults.map((track) => (
                    <div key={track.uri} className="p-4 flex items-center gap-4 hover:bg-white/5 transition-colors cursor-pointer group border-b border-white/5 last:border-0" onClick={() => addToQueue(track.uri)}>
                      <img src={track.img} alt={track.name} className="w-14 h-14 rounded-lg shadow-lg" /><div className="flex-1 min-width-0"><div className="font-bold truncate text-base">{track.name}</div><div className="text-gray-400 truncate text-sm">{track.artist}</div></div><Plus className="text-gray-500 group-hover:text-[#1DB954]" size={24} />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default App;
