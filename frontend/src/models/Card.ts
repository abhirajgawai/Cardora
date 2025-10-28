/**
 * Credit Card domain model
 */

export interface CreditCard {
  id: string;
  user_id: string;
  bank_name: string;
  card_name: string | null;
  last_four_digits: string;
  card_type: string | null;
  credit_limit: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCardData {
  card_name: string;
  last_four_digits: string;
  card_type: string;
  bank_name: string;
  credit_limit?: number;
  statement_date?: number;
  due_date?: number;
}

export interface UpdateCardData {
  card_name?: string;
  last_four_digits?: string;
  card_type?: string;
  bank_name?: string;
  credit_limit?: number;
  current_balance?: number;
  statement_date?: number;
  due_date?: number;
  is_active?: boolean;
}
