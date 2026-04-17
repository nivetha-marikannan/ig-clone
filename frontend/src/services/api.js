import axios from 'axios';
import { getToken, setToken, removeToken, getRefreshToken } from '../utils/storage';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  isRefreshing = false;
  failedQueue = [];
};

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        removeToken();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      return api
        .post('/user/token/refresh/', { refresh: refreshToken })
        .then((response) => {
          const { access } = response.data;
          setToken({ access, refresh: refreshToken });
          api.defaults.headers.common.Authorization = `Bearer ${access}`;
          originalRequest.headers.Authorization = `Bearer ${access}`;
          processQueue(null, access);
          return api(originalRequest);
        })
        .catch((err) => {
          removeToken();
          window.location.href = '/login';
          processQueue(err, null);
          return Promise.reject(err);
        });
    }
    return Promise.reject(error);
  }
);

export default api;
