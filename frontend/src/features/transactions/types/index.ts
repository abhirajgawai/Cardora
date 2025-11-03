/**
 * Transactions feature types
 */

import { CreditCard } from '@/features/cards/types';
import { PaginationParams } from '@/shared/types/common';

export interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  is_custom: boolean;
  created_at: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  card_id: string;
  statement_id: string | null;
  merchant_name: string;
  amount: number | string; // Backend returns Decimal as string
  transaction_date: string;
  description: string | null;
  statement_month: number;
  statement_year: number;
  is_recurring: boolean;
  confidence_score: number | string | null; // Backend returns Decimal as string
  category: Category | null;
  card?: CreditCard; // Optional nested card object (from API joins)
  created_at: string;
  updated_at: string;
}

export interface TransactionFilters extends PaginationParams {
  card_id?: string;
  category?: string;
  month?: number;
  year?: number;
}

export interface CreateTransactionData {
  card_id: string;
  transaction_date: string;
  description: string;
  amount: number;
  category?: string;
  merchant_name?: string;
}

export interface UpdateTransactionData {
  transaction_date?: string;
  description?: string;
  amount?: number;
  category?: string;
  merchant_name?: string;
}

export interface TransactionListResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  page_size: number;
}
