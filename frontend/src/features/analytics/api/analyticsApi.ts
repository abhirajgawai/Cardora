import { getTransactions } from '@/features/transactions';
import { getCards } from '@/features/cards';
import { getStatements } from '@/features/statements';
import { Transaction } from '@/features/transactions/types';
import { CreditCard } from '@/features/cards/types';
import { Statement } from '@/features/statements/types';

export interface AnalyticsData {
  transactions: Transaction[];
  cards: CreditCard[];
  statements: Statement[];
}

/**
 * Fetch all data needed to render the analytics page.
 * Runs the three independent requests in parallel.
 */
export const getAnalyticsData = async (): Promise<AnalyticsData> => {
  const [transactions, cards, statements] = await Promise.all([
    getTransactions({ limit: 10000 }),
    getCards(),
    getStatements().catch(() => [] as Statement[]),
  ]);

  return {
    transactions: Array.isArray(transactions) ? transactions : [],
    cards: Array.isArray(cards) ? cards : [],
    statements: Array.isArray(statements) ? statements : [],
  };
};
