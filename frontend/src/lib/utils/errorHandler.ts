/**
 * Error handling utilities
 */

import { AxiosErrorResponse, ApiErrorDetail } from '@/types/common';

/**
 * Extract error message from API error response
 */
export function extractErrorMessage(error: unknown, defaultMessage = 'An error occurred'): string {
  const err = error as AxiosErrorResponse;

  // Handle specific HTTP status codes
  if (err.response?.status === 401) {
    return 'Authentication required. Please log in.';
  }

  if (err.response?.status === 403) {
    return 'You do not have permission to access this resource.';
  }

  if (err.response?.status === 404) {
    return 'The requested resource was not found.';
  }

  if (err.response?.status === 500) {
    return 'Server error. Please try again later.';
  }

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

  // Handle network errors
  if (err.message === 'Network Error' || !err.response) {
    return 'Network error. Please check your connection.';
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
