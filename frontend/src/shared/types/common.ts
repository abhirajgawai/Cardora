/**
 * Common type definitions used across the application
 */

/**
 * API Error Response structure
 */
export interface ApiErrorDetail {
  msg?: string;
  message?: string;
  type?: string;
  loc?: string[];
}

export interface ApiErrorResponse {
  detail: string | ApiErrorDetail[] | ApiErrorDetail;
}

/**
 * Axios Error type with proper typing
 */
export interface AxiosErrorResponse {
  response?: {
    status: number;
    data?: ApiErrorResponse;
  };
  message: string;
}

/**
 * Chart data types for visualizations
 */
export interface ChartDataPoint {
  month: string;
  spending: number;
}

export interface CategoryChartData {
  name: string;
  value: number;
}

/**
 * Dashboard statistics
 */
export interface DashboardStats {
  totalSpending: number;
  transactionCount: number;
  cardCount: number;
  avgConfidence: number;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
}

/**
 * Generic API List Response
 */
export interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
