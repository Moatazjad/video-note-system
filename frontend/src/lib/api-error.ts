import { AxiosError } from 'axios';

/**
 * Extract user-friendly error message from API errors.
 * Type-safe error handling without 'any'.
 */
export function extractApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    return error.response?.data?.detail ?? 'API request failed';
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
}