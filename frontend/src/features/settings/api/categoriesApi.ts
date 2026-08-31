import apiClient from '@/shared/lib/api/client';

export interface Category {
  id: string;
  name: string;
  icon: string | null;
  color: string | null;
  is_custom: boolean;
  created_at: string;
}

export interface CreateCategoryData {
  name: string;
  icon?: string | null;
  color?: string | null;
}

export interface UpdateCategoryData {
  name?: string;
  icon?: string | null;
  color?: string | null;
}

/** Fetch all categories available to the current user (system + custom). */
export const getCategories = async (): Promise<Category[]> => {
  const response = await apiClient.get('/categories');
  return response.data;
};

/** Create a custom category. */
export const createCategory = async (data: CreateCategoryData): Promise<Category> => {
  const response = await apiClient.post('/categories', data);
  return response.data;
};

/** Update a custom category owned by the current user. */
export const updateCategory = async (
  categoryId: string,
  data: UpdateCategoryData
): Promise<Category> => {
  const response = await apiClient.patch(`/categories/${categoryId}`, data);
  return response.data;
};

/** Delete a custom category owned by the current user. */
export const deleteCategory = async (categoryId: string): Promise<void> => {
  await apiClient.delete(`/categories/${categoryId}`);
};
