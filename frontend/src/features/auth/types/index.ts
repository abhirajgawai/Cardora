/**
 * Auth feature types
 */

export interface User {
  id: string;
  email: string;
  full_name: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string; // FastAPI OAuth2 expects 'username' field
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}
