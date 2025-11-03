import apiClient from '@/shared/lib/api/client';
import {
  Transaction,
  TransactionFilters,
  TransactionListResponse,
  CreateTransactionData,
  UpdateTransactionData,
} from '../types';

// Get all transactions with optional filters
export const getTransactions = async (filters?: TransactionFilters): Promise<Transaction[]> => {
  const params = new URLSearchParams();

  if (filters?.page !== undefined) params.append('page', filters.page.toString());
  if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
  if (filters?.card_id) params.append('card_id', filters.card_id.toString());
  if (filters?.category) params.append('category', filters.category);
  if (filters?.month !== undefined) params.append('month', filters.month.toString());
  if (filters?.year !== undefined) params.append('year', filters.year.toString());

  const response = await apiClient.get<TransactionListResponse>(`/transactions?${params.toString()}`);
  return response.data.transactions;
};

// Get a single transaction by ID
export const getTransaction = async (transactionId: string): Promise<Transaction> => {
  const response = await apiClient.get(`/transactions/${transactionId}`);
  return response.data;
};

// Create a new transaction manually
export const createTransaction = async (data: CreateTransactionData): Promise<Transaction> => {
  const response = await apiClient.post('/transactions', data);
  return response.data;
};

// Update a transaction
export const updateTransaction = async (
  transactionId: string,
  data: UpdateTransactionData
): Promise<Transaction> => {
  const response = await apiClient.put(`/transactions/${transactionId}`, data);
  return response.data;
};

// Delete a transaction
export const deleteTransaction = async (transactionId: string): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/transactions/${transactionId}`);
  return response.data;
};
