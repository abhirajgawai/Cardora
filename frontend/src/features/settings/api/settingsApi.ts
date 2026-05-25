import apiClient from '@/shared/lib/api/client';
import { User } from '@/features/auth/types';

export interface UpdateProfileData {
  full_name?: string;
  timezone?: string;
}

export interface UpdatePasswordData {
  current_password: string;
  new_password: string;
}

/** Fetch the current user's profile. */
export const getProfile = async (): Promise<User> => {
  const response = await apiClient.get('/users/me');
  return response.data;
};

/** Update display name or timezone. */
export const updateProfile = async (data: UpdateProfileData): Promise<User> => {
  const response = await apiClient.patch('/users/me', data);
  return response.data;
};

/** Change the current user's password. */
export const updatePassword = async (data: UpdatePasswordData): Promise<void> => {
  await apiClient.post('/users/me/password', data);
};

/** Permanently delete the current user's account and all associated data. */
export const deleteAccount = async (): Promise<void> => {
  await apiClient.delete('/users/me');
};
