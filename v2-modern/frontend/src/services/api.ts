import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.zsirb.hu/api',
  withCredentials: true,
});

export const authApi = {
  login: (credentials: { username: string; password: str }) => 
    api.post('/auth/login', credentials),
  register: (credentials: { username: string; password: str }) => 
    api.post('/auth/register', credentials),
  logout: () => api.get('/auth/logout'),
  deleteAccount: () => api.delete('/auth/account'),
  getSpotifyLoginUrl: () => 
    api.get('/auth/spotify/login'),
  logoutSpotify: () => api.get('/auth/spotify/logout'),
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
