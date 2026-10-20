import axios from 'axios';

const KEY = 'papelera-la-plata:auth';
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/',
    headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
    const tokens = JSON.parse(sessionStorage.getItem(KEY) || '{}');
    if (tokens.access)
        config.headers.Authorization = `Bearer ${tokens.access}`;
    return config;
});

let refreshRequest;
api.interceptors.response.use((response) => response, async (error) => {
    const request = error.config;
    const tokens = JSON.parse(sessionStorage.getItem(KEY) || '{}');
    if (error.response?.status !== 401 || request?._retry || !tokens.refresh || request?.url?.includes('/token/'))
        return Promise.reject(error);
    request._retry = true;
    try {
        refreshRequest ||= axios.post(`${api.defaults.baseURL}token/refresh/`, { refresh: tokens.refresh });
        const { data } = await refreshRequest;
        const nextTokens = { ...tokens, access: data.access, refresh: data.refresh || tokens.refresh };
        sessionStorage.setItem(KEY, JSON.stringify(nextTokens));
        refreshRequest = null;
        request.headers.Authorization = `Bearer ${nextTokens.access}`;
        return api(request);
    }
    catch (refreshError) {
        refreshRequest = null;
        sessionStorage.removeItem(KEY);
        window.dispatchEvent(new Event('auth:expired'));
        return Promise.reject(refreshError);
    }
});

export default api;