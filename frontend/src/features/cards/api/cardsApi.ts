import apiClient from '@/shared/lib/api/client';
import {
  CreditCard,
  CreateCardData,
  UpdateCardData,
} from '../types';

// Get all credit cards for the current user
export const getCards = async (): Promise<CreditCard[]> => {
  const response = await apiClient.get('/credit-cards');
  return response.data;
};

// Get a single credit card by ID
export const getCard = async (cardId: string): Promise<CreditCard> => {
  const response = await apiClient.get(`/credit-cards/${cardId}`);
  return response.data;
};

// Create a new credit card
export const createCard = async (data: CreateCardData): Promise<CreditCard> => {
  const response = await apiClient.post('/credit-cards', data);
  return response.data;
};

// Update a credit card
export const updateCard = async (cardId: string, data: UpdateCardData): Promise<CreditCard> => {
  const response = await apiClient.patch(`/credit-cards/${cardId}`, data);
  return response.data;
};

// Delete a credit card
export const deleteCard = async (cardId: string): Promise<void> => {
  await apiClient.delete(`/credit-cards/${cardId}`);
};
