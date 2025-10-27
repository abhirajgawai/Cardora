/**
 * Error handling utilities
 */

import { AxiosErrorResponse, ApiErrorDetail } from '@/types/common';

/**
 * Extract error message from API error response
 */
export function extractErrorMessage(error: unknown, defaultMessage = 'An error occurred'): string {
  const err = error as AxiosErrorResponse;

  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;

    // Check if detail is a string
    if (typeof detail === 'string') {
      return detail;
    }

    // Check if detail is an array (validation errors)
    if (Array.isArray(detail)) {
      return detail
        .map((e: ApiErrorDetail) => e.msg || e.message || JSON.stringify(e))
        .join(', ');
    }

    // Check if detail is an object
    if (typeof detail === 'object') {
      const detailObj = detail as ApiErrorDetail;
      return detailObj.msg || detailObj.message || JSON.stringify(detail);
    }
  }

  return defaultMessage;
}

/**
 * Check if error is an authentication error (401)
 */
export function isAuthError(error: unknown): boolean {
  const err = error as AxiosErrorResponse;
  return err.response?.status === 401;
}
