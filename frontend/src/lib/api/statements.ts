import apiClient from './client';
import { Statement, StatementUploadResponse } from '@/models';

/**
 * Upload a PDF statement for AI extraction
 * @param file - PDF file to upload
 * @returns Statement with extracted transactions and stats
 */
export const uploadStatement = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<StatementUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<StatementUploadResponse>(
    '/statements/upload',
    formData,
    {
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    }
  );

  return response.data;
};

/**
 * Get all statements for the current user
 * @param cardId - Optional filter by card ID
 * @returns List of statements
 */
export const getStatements = async (cardId?: string): Promise<Statement[]> => {
  const params = cardId ? { card_id: cardId } : {};
  const response = await apiClient.get<Statement[]>('/statements', { params });
  return response.data;
};

/**
 * Get a single statement by ID
 * @param statementId - Statement ID
 * @returns Statement details
 */
export const getStatement = async (statementId: string): Promise<Statement> => {
  const response = await apiClient.get<Statement>(`/statements/${statementId}`);
  return response.data;
};

/**
 * Delete a statement and all its transactions
 * @param statementId - Statement ID
 */
export const deleteStatement = async (statementId: string): Promise<void> => {
  await apiClient.delete(`/statements/${statementId}`);
};

/**
 * Statement status response for polling
 */
export interface StatementStatus {
  statement_id: string;
  processing_status: 'processing' | 'completed' | 'failed';
  insights_status: 'pending' | 'processing' | 'completed' | 'failed';
  insights_generated_at: string | null;
  error: string | null;
}

/**
 * Check statement processing status (for polling)
 * @param statementId - Statement ID
 * @returns Status information
 */
export const getStatementStatus = async (statementId: string): Promise<StatementStatus> => {
  const response = await apiClient.get<StatementStatus>(`/statements/${statementId}/status`);
  return response.data;
};
