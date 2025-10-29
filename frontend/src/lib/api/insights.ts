import apiClient from './client';

/**
 * Insight Types - Matches Backend API Structure
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

/**
 * Response from GET /insights
 */
export interface GetInsightsResponse {
  insights: Insight[];
  count: number;
}

/**
 * Response from POST /insights/generate
 */
export interface GenerateInsightsResponse {
  generated: number;
  insights: Insight[];
  message: string;
}

/**
 * Response from PATCH /insights/{id}/dismiss
 */
export interface DismissInsightResponse {
  message: string;
  id: string;
}

/**
 * Transaction linked to an insight
 */
export interface InsightTransaction {
  id: string;
  transaction_date: string;
  merchant_name: string;
  amount: number;
  category_name: string;
  description: string | null;
}

/**
 * Response from GET /insights/{id}/transactions
 */
export interface GetInsightTransactionsResponse {
  insight: Insight;
  transactions: InsightTransaction[];
  summary: {
    total_amount: number;
    transaction_count: number;
  };
}

/**
 * Get all insights for the current user
 * @param includeDismissed - Include dismissed insights (default: false)
 * @returns List of insights with count
 */
export const getInsights = async (includeDismissed: boolean = false): Promise<GetInsightsResponse> => {
  const response = await apiClient.get<GetInsightsResponse>('/insights', {
    params: { include_dismissed: includeDismissed }
  });
  return response.data;
};

/**
 * Generate new insights for the current user
 * Analyzes last 3 months of transactions and generates rule-based insights
 * @returns Newly generated insights
 */
export const generateInsights = async (): Promise<GenerateInsightsResponse> => {
  const response = await apiClient.post<GenerateInsightsResponse>('/insights/generate');
  return response.data;
};

/**
 * Dismiss an insight
 * @param insightId - Insight ID
 * @returns Success message
 */
export const dismissInsight = async (insightId: string): Promise<DismissInsightResponse> => {
  const response = await apiClient.patch<DismissInsightResponse>(`/insights/${insightId}/dismiss`);
  return response.data;
};

/**
 * Get transactions linked to a specific insight
 * @param insightId - Insight ID
 * @returns Insight details with all linked transactions
 */
export const getInsightTransactions = async (insightId: string): Promise<GetInsightTransactionsResponse> => {
  const response = await apiClient.get<GetInsightTransactionsResponse>(`/insights/${insightId}/transactions`);
  return response.data;
};
