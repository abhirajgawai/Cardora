import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // If the request data is FormData, delete Content-Type so axios sets it automatically with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized (token expired or invalid)
    // Skip for the login endpoint itself — wrong password is a legitimate 401
    // that the login form handles via its own catch block.
    const isAuthEndpoint = error.config?.url?.startsWith('/auth/');
    if (error.response?.status === 401 && !isAuthEndpoint) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');

        const currentPath = window.location.pathname;
        if (currentPath !== '/login' && currentPath !== '/register') {
          localStorage.setItem('redirectAfterLogin', currentPath);
        }

        window.location.href = '/login?expired=true';
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
