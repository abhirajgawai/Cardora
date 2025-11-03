'use client';

import { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { StatementUploadResponse } from '@/models';
import { formatCardDisplayName } from '@/lib/utils/cardFormatter';

interface UploadResultsProps {
  result: StatementUploadResponse;
  onUploadAnother: () => void;
}

// Category icon mapping - same as Dashboard/Analytics
const getCategoryIcon = (categoryName: string): string => {
  const iconMap: Record<string, string> = {
    'Groceries': '🛒',
    'Flights & Travel': '✈️',
    'Flights & Travel Bookings': '✈️',
    'Transport': '🚗',
    'Dining': '🍽️',
    'Shopping': '🛍️',
    'Bills & Utilities': '📄',
    'Entertainment': '🎮',
    'Healthcare': '⚕️',
    'Clothing & Apparel': '👕',
    'Clothing & Accessories': '👕',
    'Fitness & Wellness': '💪',
    'Online Shopping': '🖥️',
    'Home & Garden': '🏡',
    'Education': '📚',
    'Pets': '🐾',
    'Travel': '🧳',
    'Gas': '⛽',
    'Restaurants': '🍔',
    'Coffee': '☕',
    'Subscriptions': '📱',
    'Insurance': '🛡️',
    'Hotels & Accommodation': '🏨',
    'Beauty & Personal Care': '💄',
    'Electronics': '💻',
    'Gas & Fuel': '⛽',
    'Others': '📦',
    'Uncategorized': '❓',
  };
  return iconMap[categoryName] || '📦';
};

const COLORS = [
  '#4B6EF5', // Primary
  '#00E0A1', // Accent
  '#F59E0B', // Amber
  '#10B981', // Emerald
  '#8B5CF6', // Purple
  '#60A5FA', // Sky Blue
  '#FB923C', // Coral
];

export default function UploadResults({ result, onUploadAnother }: UploadResultsProps) {
  const router = useRouter();
  const { statement, extracted_transactions, stats } = result;

  // Get the card info from the first transaction if available
  const cardInfo = extracted_transactions[0]?.card;
  const cardDisplayName = cardInfo
    ? formatCardDisplayName(cardInfo.card_name, cardInfo.bank_name, cardInfo.card_type, cardInfo.last_four_digits)
    : 'Credit Card';

  // Get top 7 transactions
  const recentTransactions = useMemo(() => {
    return extracted_transactions
      .sort((a, b) => new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime())
      .slice(0, 7);
  }, [extracted_transactions]);

  // Process category data with icons and colors
  const categoryData = useMemo(() => {
    const categoryEntries = stats.categories_assigned
      ? Object.entries(stats.categories_assigned).sort((a, b) => b[1] - a[1])
      : [];

    return categoryEntries.slice(0, 5).map(([name, count], index) => {
      const percentage = Math.round((count / stats.total_transactions) * 100);
      // Calculate total amount for this category
      const categoryTotal = extracted_transactions
        .filter(t => t.category?.name === name)
        .reduce((sum, t) => sum + Number(t.amount), 0);

      return {
        name,
        count,
        amount: Math.round(categoryTotal * 100) / 100,
        percentage,
        icon: getCategoryIcon(name),
        color: COLORS[index % COLORS.length],
      };
    });
  }, [stats, extracted_transactions]);

  // Generate quick insights
  const insights = useMemo(() => {
    const topCategory = categoryData[0];
    const uniqueMerchants = new Set(extracted_transactions.map(t => t.merchant_name || t.description)).size;
    const avgTransaction = stats.total_amount / stats.total_transactions;

    return [
      topCategory ? `You spent most on ${topCategory.name} ($${topCategory.amount.toFixed(2)} across ${topCategory.count} ${topCategory.count === 1 ? 'transaction' : 'transactions'})` : null,
      `${uniqueMerchants} unique merchant${uniqueMerchants !== 1 ? 's' : ''} detected`,
      `Average transaction: $${avgTransaction.toFixed(2)}`,
      stats.avg_confidence >= 0.95 ? 'Excellent extraction confidence' : null,
    ].filter(Boolean);
  }, [categoryData, extracted_transactions, stats]);

  return (
    <div className="animate-fade-in space-y-6">
      {/* Hero Section - Success Celebration */}
      <div className="fintech-card overflow-hidden">
        <div className="px-8 py-6 bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl gradient-indigo-purple flex items-center justify-center flex-shrink-0">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-foreground mb-2">Statement Uploaded Successfully!</h2>
              <div className="flex items-center gap-2 text-muted-foreground">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                <span className="font-medium">{cardDisplayName}</span>
                <span>•</span>
                <span>{new Date(statement.statement_year, statement.statement_month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} Statement</span>
              </div>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-card rounded-xl p-4 border border-border card-accent-indigo">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Transactions</p>
              <p className="text-2xl font-bold text-foreground">{stats.total_transactions}</p>
            </div>

            <div className="bg-card rounded-xl p-4 border border-border card-accent-teal">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                  <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Total Spent</p>
              <p className="text-2xl font-bold text-foreground">${stats.total_amount.toFixed(2)}</p>
            </div>

            <div className="bg-card rounded-xl p-4 border border-border card-accent-amber">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg gradient-indigo-purple flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Confidence</p>
              <p className="text-2xl font-bold text-accent">{Math.round(stats.avg_confidence * 100)}%</p>
            </div>

            <div className="bg-card rounded-xl p-4 border border-border card-accent-emerald">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg bg-secondary/10 flex items-center justify-center">
                  <svg className="w-4 h-4 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Categories</p>
              <p className="text-2xl font-bold text-foreground">{Object.keys(stats.categories_assigned || {}).length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid - Transaction Preview + Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Transaction Preview */}
        <div className="fintech-card">
          <div className="px-5 py-4 border-b border-border">
            <h3 className="text-base font-bold text-foreground">Recent Transactions</h3>
            <p className="text-xs text-muted-foreground mt-0.5">From this statement</p>
          </div>
          <div className="p-5">
            {recentTransactions.length > 0 ? (
              <div className="space-y-3">
                {recentTransactions.map((transaction, index) => (
                  <div
                    key={transaction.id || index}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/30 transition-all duration-200 border border-transparent hover:border-border"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-12 h-12 rounded-xl flex items-center justify-center text-3xl"
                        style={{ backgroundColor: `${COLORS[index % COLORS.length]}15` }}
                      >
                        {getCategoryIcon(transaction.category?.name || 'Uncategorized')}
                      </div>
                      <div className="text-left">
                        <div className="font-semibold text-sm text-foreground truncate max-w-[180px]">
                          {transaction.merchant_name || transaction.description}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(transaction.transaction_date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric'
                          })}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-sm text-foreground">
                        ${Number(transaction.amount).toFixed(2)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {transaction.category?.name || 'Other'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-10 text-center text-muted-foreground text-sm">
                <p>No transactions found</p>
              </div>
            )}
            {extracted_transactions.length > 7 && (
              <button
                onClick={() => router.push('/transactions')}
                className="w-full mt-4 text-sm font-medium text-primary hover:text-primary/80 transition-colors flex items-center justify-center gap-1"
              >
                <span>View All {extracted_transactions.length} Transactions</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Category Breakdown - Beautiful Horizontal Bars */}
        <div className="fintech-card p-5">
          <div className="mb-5">
            <h3 className="text-base font-bold text-foreground mb-0.5">Spending by Category</h3>
            <p className="text-xs text-muted-foreground">Top {categoryData.length} categories from this statement</p>
          </div>
          {categoryData.length > 0 ? (
            <div className="space-y-3">
              {categoryData.map((category) => (
                <div
                  key={category.name}
                  className="group hover:bg-muted/30 p-3 rounded-lg transition-all duration-200 border border-transparent hover:border-border"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-12 h-12 rounded-xl flex items-center justify-center text-3xl"
                        style={{ backgroundColor: `${category.color}15` }}
                      >
                        {category.icon}
                      </div>
                      <div className="text-left">
                        <div className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors">
                          {category.name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {category.count} transaction{category.count !== 1 ? 's' : ''}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-sm text-foreground">
                        ${category.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {category.percentage}%
                      </div>
                    </div>
                  </div>
                  <div className="w-full h-3 bg-muted/50 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500 ease-out"
                      style={{
                        width: `${category.percentage}%`,
                        backgroundColor: category.color,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-10 text-center text-muted-foreground text-sm">
              <p>No category data</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Insights */}
      {insights.length > 0 && (
        <div className="fintech-card p-6 bg-gradient-to-r from-blue-50/50 to-teal-50/50 dark:from-blue-900/10 dark:to-teal-900/10">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-foreground mb-2">Statement Highlights</h3>
              <ul className="space-y-1 text-sm text-muted-foreground">
                {insights.map((insight, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">•</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4">
        <button
          onClick={() => router.push('/transactions')}
          className="flex-1 px-6 py-3 gradient-indigo-purple text-white font-semibold rounded-xl hover:opacity-90 transition-opacity shadow-lg flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span>View All Transactions ({stats.total_transactions})</span>
        </button>
        <button
          onClick={onUploadAnother}
          className="sm:w-48 px-6 py-3 bg-muted text-foreground font-medium rounded-xl hover:bg-muted/80 transition-colors"
        >
          Upload Another
        </button>
        <button
          onClick={() => router.push('/dashboard')}
          className="sm:w-48 px-6 py-3 border border-border text-foreground font-medium rounded-xl hover:bg-muted/50 transition-colors"
        >
          Dashboard
        </button>
      </div>
    </div>
  );
}
