import { Transaction } from '@/models';
import { TimeRange } from '@/components/TimeRangeSelector';

export interface DateRange {
  startDate: Date;
  endDate: Date;
}

/**
 * Get the date range based on the selected time range option
 */
export function getDateRangeFromTimeRange(timeRange: TimeRange): DateRange {
  const now = new Date();
  const endDate = now;
  let startDate: Date;

  switch (timeRange) {
    case 'last_month':
      // Current month from 1st to today
      startDate = new Date(now.getFullYear(), now.getMonth(), 1);
      break;

    case 'last_3_months':
      // 3 months back from today
      startDate = new Date(now);
      startDate.setMonth(startDate.getMonth() - 3);
      break;

    case 'last_6_months':
      // 6 months back from today
      startDate = new Date(now);
      startDate.setMonth(startDate.getMonth() - 6);
      break;

    case 'this_year':
      // From January 1st of current year
      startDate = new Date(now.getFullYear(), 0, 1);
      break;

    case 'all_time':
      // From a very old date (effectively no filter)
      startDate = new Date(2000, 0, 1);
      break;

    default:
      startDate = new Date(now.getFullYear(), now.getMonth(), 1);
  }

  return { startDate, endDate };
}

/**
 * Filter transactions by date range
 */
export function filterTransactionsByDateRange(
  transactions: Transaction[],
  dateRange: DateRange
): Transaction[] {
  return transactions.filter((transaction) => {
    const transactionDate = new Date(transaction.transaction_date);
    return (
      transactionDate >= dateRange.startDate &&
      transactionDate <= dateRange.endDate
    );
  });
}

/**
 * Filter transactions by time range
 */
export function filterTransactionsByTimeRange(
  transactions: Transaction[],
  timeRange: TimeRange
): Transaction[] {
  const dateRange = getDateRangeFromTimeRange(timeRange);
  return filterTransactionsByDateRange(transactions, dateRange);
}

/**
 * Get a descriptive label for the time range
 */
export function getTimeRangeLabel(timeRange: TimeRange): string {
  const labels: Record<TimeRange, string> = {
    last_month: 'this month',
    last_3_months: 'the last 3 months',
    last_6_months: 'the last 6 months',
    this_year: 'this year',
    all_time: 'all time',
  };
  return labels[timeRange];
}

/**
 * Calculate percentage change between two values
 */
export function calculatePercentageChange(current: number, previous: number): number {
  if (previous === 0) return current > 0 ? 100 : 0;
  return ((current - previous) / previous) * 100;
}

/**
 * Get previous period date range for comparison
 */
export function getPreviousPeriodDateRange(timeRange: TimeRange): DateRange {
  const currentRange = getDateRangeFromTimeRange(timeRange);
  const duration = currentRange.endDate.getTime() - currentRange.startDate.getTime();

  const endDate = new Date(currentRange.startDate.getTime() - 1); // One day before current period
  const startDate = new Date(endDate.getTime() - duration);

  return { startDate, endDate };
}
