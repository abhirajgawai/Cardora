/**
 * Insights feature types
 */

export interface Insight {
  id: string;
  insight_type: string;
  title: string;
  description: string;
  impact_score: number; // 1-10
  potential_savings: number | null;
  created_at: string;
  dismissed_at: string | null;
}

export interface GetInsightsResponse {
  insights: Insight[];
  count: number;
}

export interface GenerateInsightsResponse {
  generated: number;
  insights: Insight[];
  message: string;
}

export interface DismissInsightResponse {
  message: string;
  id: string;
}

export interface InsightTransaction {
  id: string;
  transaction_date: string;
  merchant_name: string;
  amount: number;
  category_name: string;
  description: string | null;
}

export interface GetInsightTransactionsResponse {
  insight: Insight;
  transactions: InsightTransaction[];
  summary: {
    total_amount: number;
    transaction_count: number;
  };
}
