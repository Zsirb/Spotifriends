import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true,
});

export const authApi = {
  login: (credentials: { username: string; password: str }) => 
    api.post('/auth/login', credentials),
  getSpotifyLoginUrl: () => 
    api.get('/auth/spotify/login'),
};

export const playbackApi = {
  getStatus: () => api.get('/playback/status'),
  control: (action: string) => api.get(`/playback/control/${action}`),
  seek: (posMs: number) => api.get(`/playback/seek/${posMs}`),
  setVolume: (percent: number) => api.get(`/playback/volume/${percent}`),
};

export const searchApi = {
  search: (query: string) => api.get(`/search/`, { params: { q: query } }),
  addToQueue: (uri: string) => api.post(`/search/queue/${uri}`),
};

export default api;
