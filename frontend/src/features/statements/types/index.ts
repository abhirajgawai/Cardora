/**
 * Statements feature types
 */

import { CreditCard } from '@/features/cards/types';
import { Transaction } from '@/features/transactions/types';

export interface Statement {
  id: string;
  user_id: string;
  card_id: string;
  file_name: string;
  statement_month: number;
  statement_year: number;
  total_transactions: number;
  total_amount: number | string; // Backend returns Decimal as string
  processing_status: 'processing' | 'completed' | 'failed';
  ai_confidence_score: number | string | null; // Backend returns Decimal as string
  processed_at: string | null;
  created_at: string;
  updated_at: string;
  card?: CreditCard;
}

export interface StatementUploadResponse {
  statement: Statement;
  extracted_transactions: Transaction[];
  message: string;
  stats: {
    total_transactions: number;
    total_amount: number;
    avg_confidence: number;
    processing_time_seconds: number;
    categories_assigned?: Record<string, number>;
  };
}

export interface StatementListResponse {
  statements: Statement[];
  total: number;
}

export interface StatementStatus {
  statement_id: string;
  processing_status: 'processing' | 'completed' | 'failed';
  insights_status: 'pending' | 'processing' | 'completed' | 'failed';
  insights_generated_at: string | null;
  error: string | null;
}
