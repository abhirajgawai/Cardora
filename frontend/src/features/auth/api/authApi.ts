import apiClient from '@/shared/lib/api/client';
import {
  User,
  LoginCredentials,
  RegisterData,
  AuthTokens,
} from '../types';

// Login user
export const login = async (credentials: LoginCredentials): Promise<AuthTokens> => {
  // Send JSON with email and password fields
  const response = await apiClient.post('/auth/login', {
    email: credentials.username, // Map username to email
    password: credentials.password,
  });

  // Store token in localStorage
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
  }

  return response.data;
};

// Register new user
export const register = async (data: RegisterData): Promise<User> => {
  const response = await apiClient.post('/auth/register', data);
  return response.data;
};

// Get current user
export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get('/users/me');
  return response.data;
};

// Logout user
export const logout = () => {
  localStorage.removeItem('access_token');
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
};
