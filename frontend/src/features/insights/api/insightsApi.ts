import apiClient from '@/shared/lib/api/client';
import {
  Insight,
  GetInsightsResponse,
  GenerateInsightsResponse,
  DismissInsightResponse,
  GetInsightTransactionsResponse
} from '../types';

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
