const SGD_FORMATTER = new Intl.NumberFormat('en-SG', {
  style: 'currency',
  currency: 'SGD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * Format a numeric amount as Singapore dollars.
 * Accepts both number and string (backend returns Decimal as string).
 * Output: "S$1,234.56"
 */
export const formatCurrency = (amount: number | string): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return 'S$0.00';
  return SGD_FORMATTER.format(num);
};

/**
 * Short formatter for chart axis ticks — omits cents for large values.
 * Output: "S$1,234" or "S$1,234.56"
 */
export const formatCurrencyCompact = (amount: number): string => {
  if (isNaN(amount)) return 'S$0';
  return new Intl.NumberFormat('en-SG', {
    style: 'currency',
    currency: 'SGD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};
