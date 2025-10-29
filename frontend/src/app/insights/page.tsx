'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { getInsights, getInsightTransactions, dismissInsight, generateInsights, Insight, InsightTransaction } from '@/lib/api/insights';
import Sidebar from '@/components/layout/Sidebar';

interface GroupedTransactions {
  weekend: string;
  transactions: InsightTransaction[];
  total: number;
}

export default function InsightsPage() {
  const router = useRouter();
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedInsightId, setExpandedInsightId] = useState<string | null>(null);
  const [transactions, setTransactions] = useState<InsightTransaction[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [transactionsSummary, setTransactionsSummary] = useState<{ total_amount: number; transaction_count: number } | null>(null);
  const [generatingInsights, setGeneratingInsights] = useState(false);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const response = await getInsights(false);
      setInsights(response.insights);
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInsights = async () => {
    try {
      setGeneratingInsights(true);
      const response = await generateInsights();
      await fetchInsights();

      // Show success toast
      if (response.generated > 0) {
        toast.success('Insights Generated', {
          description: `Successfully generated ${response.generated} new insight(s)`,
        });
      } else {
        toast.info('No New Insights', {
          description: 'No new insights generated based on your spending patterns.',
        });
      }
    } catch (error) {
      console.error('Failed to generate insights:', error);
      toast.error('Generation Failed', {
        description: 'Failed to generate insights. Please try again.',
      });
    } finally {
      setGeneratingInsights(false);
    }
  };

  const handleExpandInsight = async (insightId: string) => {
    // If clicking the same insight, collapse it
    if (expandedInsightId === insightId) {
      setExpandedInsightId(null);
      setTransactions([]);
      setTransactionsSummary(null);
      return;
    }

    // Expand and load transactions
    setExpandedInsightId(insightId);
    setTransactionsLoading(true);

    try {
      const response = await getInsightTransactions(insightId);
      setTransactions(response.transactions);
      setTransactionsSummary(response.summary);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      toast.error('Load Failed', {
        description: 'Failed to load transactions. Please try again.',
      });
    } finally {
      setTransactionsLoading(false);
    }
  };

  const handleDismiss = async (insightId: string) => {
    try {
      await dismissInsight(insightId);
      setInsights(prev => prev.filter(i => i.id !== insightId));
      if (expandedInsightId === insightId) {
        setExpandedInsightId(null);
        setTransactions([]);
        setTransactionsSummary(null);
      }
      toast.success('Insight Dismissed', {
        description: 'This insight has been removed from your list.',
      });
    } catch (error) {
      console.error('Failed to dismiss insight:', error);
      toast.error('Dismiss Failed', {
        description: 'Failed to dismiss insight. Please try again.',
      });
    }
  };

  const getImpactColor = (score: number) => {
    if (score >= 8) return 'text-red-500';
    if (score >= 5) return 'text-amber-500';
    return 'text-blue-500';
  };

  const getImpactBadgeColor = (score: number) => {
    if (score >= 8) return 'bg-red-500/10 text-red-500 border-red-500/20';
    if (score >= 5) return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
    return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
  };

  const getImpactLabel = (score: number) => {
    if (score >= 8) return 'High Impact';
    if (score >= 5) return 'Medium Impact';
    return 'Low Impact';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  // Group transactions by weekend for weekend_spending insights
  const groupTransactionsByWeekend = (txns: InsightTransaction[]): GroupedTransactions[] => {
    const groups: { [key: string]: InsightTransaction[] } = {};

    txns.forEach(txn => {
      const date = new Date(txn.transaction_date);
      const dayOfWeek = date.getDay();

      // Only group if it's a weekend transaction
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        // Find the Saturday of this weekend
        const saturday = new Date(date);
        if (dayOfWeek === 0) {
          // If Sunday, go back one day to Saturday
          saturday.setDate(saturday.getDate() - 1);
        }

        const weekendKey = saturday.toISOString().split('T')[0];

        if (!groups[weekendKey]) {
          groups[weekendKey] = [];
        }
        groups[weekendKey].push(txn);
      }
    });

    // Convert to array and calculate totals
    return Object.entries(groups).map(([weekend, txns]) => ({
      weekend,
      transactions: txns.sort((a, b) =>
        new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime()
      ),
      total: txns.reduce((sum, txn) => sum + txn.amount, 0)
    })).sort((a, b) => new Date(b.weekend).getTime() - new Date(a.weekend).getTime());
  };

  // Find top 3 expenses
  const getTopExpenses = (txns: InsightTransaction[]): Set<string> => {
    const sorted = [...txns].sort((a, b) => b.amount - a.amount);
    return new Set(sorted.slice(0, 3).map(t => t.id));
  };

  // Calculate weekend vs weekday stats for weekend_spending insights
  const calculateWeekendStats = (insight: Insight, txns: InsightTransaction[]) => {
    const weekendTxns = txns.filter(t => {
      const day = new Date(t.transaction_date).getDay();
      return day === 0 || day === 6;
    });

    const weekendTotal = weekendTxns.reduce((sum, t) => sum + t.amount, 0);
    const weekendCount = weekendTxns.length;

    // Parse weekday stats from description
    const description = insight.description;
    const weekdayMatch = description.match(/\$([0-9,]+\.[0-9]+) across (\d+) weekday/);

    if (weekdayMatch) {
      const weekdayTotal = parseFloat(weekdayMatch[1].replace(/,/g, ''));
      const weekdayCount = parseInt(weekdayMatch[2]);

      return {
        weekend: { total: weekendTotal, count: weekendCount },
        weekday: { total: weekdayTotal, count: weekdayCount }
      };
    }

    return null;
  };

  // Generate smart recommendations based on insight data
  const generateRecommendations = (insight: Insight, txns: InsightTransaction[]): string[] => {
    const recommendations: string[] = [];

    if (insight.insight_type === 'weekend_spending') {
      // Find top spending category
      const categoryTotals: { [key: string]: number } = {};
      txns.forEach(t => {
        categoryTotals[t.category_name] = (categoryTotals[t.category_name] || 0) + t.amount;
      });

      const topCategory = Object.entries(categoryTotals).sort((a, b) => b[1] - a[1])[0];

      if (topCategory) {
        recommendations.push(`Your biggest weekend expense is ${topCategory[0]} (${formatCurrency(topCategory[1])})`);
      }

      if (insight.potential_savings) {
        const targetReduction = Math.round((insight.potential_savings / transactionsSummary!.total_amount) * 100);
        recommendations.push(`Consider reducing weekend spending by ${targetReduction}% to save ${formatCurrency(insight.potential_savings)}/month`);
      }

      recommendations.push('Try planning weekend activities in advance to avoid impulse purchases');
    }

    return recommendations;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen fintech-bg">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 ml-64">
        {/* Header - Clean & Consistent with Dashboard */}
        <header className="bg-card border-b border-border px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="p-2 rounded-lg bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-all group"
                  title="Back to Dashboard"
                >
                  <svg className="w-5 h-5 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <h1 className="text-3xl font-bold text-card-foreground">AI Insights</h1>
              </div>
              <p className="text-muted-foreground ml-14">
                Personalized recommendations based on your spending patterns
              </p>
            </div>

            {/* Action Button */}
            <button
              onClick={handleGenerateInsights}
              disabled={generatingInsights}
              className="flex items-center space-x-2 px-6 py-2.5 gradient-indigo-purple text-white font-semibold rounded-xl btn-hover-accent shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingInsights ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span>Generate Insights</span>
                </>
              )}
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="px-8 py-5">
          {insights.length === 0 ? (
            <div className="fintech-card p-12 text-center">
              <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">No Insights Yet</h2>
              <p className="text-muted-foreground mb-6">
                Upload statements and generate insights to get personalized recommendations.
              </p>
              <button
                onClick={() => router.push('/dashboard')}
                className="px-6 py-2.5 gradient-indigo-purple text-white font-semibold rounded-xl btn-hover-accent shadow-lg"
              >
                Go to Dashboard
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {insights.map((insight, index) => {
                const isExpanded = expandedInsightId === insight.id;
                const topExpenses = isExpanded ? getTopExpenses(transactions) : new Set();
                const weekendGroups = isExpanded && insight.insight_type === 'weekend_spending'
                  ? groupTransactionsByWeekend(transactions)
                  : [];
                const weekendStats = isExpanded && insight.insight_type === 'weekend_spending'
                  ? calculateWeekendStats(insight, transactions)
                  : null;
                const recommendations = isExpanded && transactionsSummary
                  ? generateRecommendations(insight, transactions)
                  : [];

                return (
                  <div key={insight.id} className="fintech-card overflow-hidden animate-slide-in" style={{ animationDelay: `${index * 0.1}s` }}>
                    {/* Insight Header */}
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-xl font-bold text-foreground">{insight.title}</h3>
                            <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${getImpactBadgeColor(insight.impact_score)}`}>
                              {getImpactLabel(insight.impact_score)}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            {formatDate(insight.created_at)}
                          </p>
                          <p className="text-foreground leading-relaxed">{insight.description}</p>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => handleDismiss(insight.id)}
                            className="p-2 rounded-lg bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
                            title="Dismiss"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>

                      {/* Potential Savings */}
                      {insight.potential_savings && insight.potential_savings > 0 && (
                        <div className="mt-4 p-4 rounded-lg bg-green-500/5 border border-green-500/20">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
                                Potential Monthly Savings
                              </p>
                              <p className="text-2xl font-bold text-green-600 mt-1">
                                {formatCurrency(insight.potential_savings)}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
                                Impact Score
                              </p>
                              <p className="text-2xl font-bold text-foreground mt-1">
                                {insight.impact_score}/10
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Expand/Collapse Button */}
                      <button
                        onClick={() => handleExpandInsight(insight.id)}
                        disabled={transactionsLoading}
                        className="mt-4 w-full px-4 py-3 bg-primary hover:bg-primary/90 text-white font-semibold rounded-lg transition-all flex items-center justify-center space-x-2 shadow-md hover:shadow-lg disabled:opacity-50"
                      >
                        {transactionsLoading ? (
                          <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            <span>Loading Transactions...</span>
                          </>
                        ) : (
                          <>
                            <span>{isExpanded ? 'Hide Transactions' : 'View Linked Transactions'}</span>
                            <svg className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Expanded Transactions View */}
                    {isExpanded && transactions.length > 0 && (
                      <div className="border-t border-border bg-muted/30 animate-slide-down">
                        <div className="p-6">
                          {/* Summary Stats */}
                          <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="p-4 bg-background rounded-lg border border-border">
                              <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold mb-1">
                                Total Transactions
                              </p>
                              <p className="text-2xl font-bold text-foreground">
                                {transactionsSummary?.transaction_count || 0}
                              </p>
                            </div>
                            <div className="p-4 bg-background rounded-lg border border-border">
                              <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold mb-1">
                                Total Amount
                              </p>
                              <p className="text-2xl font-bold text-foreground">
                                {formatCurrency(transactionsSummary?.total_amount || 0)}
                              </p>
                            </div>
                          </div>

                          {/* Weekend vs Weekday Comparison Chart */}
                          {weekendStats && (
                            <div className="mb-6 p-5 bg-background rounded-lg border border-border">
                              <h5 className="text-sm font-bold text-foreground mb-4">Weekend vs Weekday Comparison</h5>
                              <div className="space-y-4">
                                {/* Weekend Bar */}
                                <div>
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium text-foreground">
                                      Weekend ({weekendStats.weekend.count} txns)
                                    </span>
                                    <span className="text-sm font-bold text-red-500">
                                      {formatCurrency(weekendStats.weekend.total)}
                                    </span>
                                  </div>
                                  <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full transition-all duration-700"
                                      style={{
                                        width: `${(weekendStats.weekend.total / (weekendStats.weekend.total + weekendStats.weekday.total)) * 100}%`
                                      }}
                                    />
                                  </div>
                                </div>

                                {/* Weekday Bar */}
                                <div>
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium text-foreground">
                                      Weekday ({weekendStats.weekday.count} txns)
                                    </span>
                                    <span className="text-sm font-bold text-green-500">
                                      {formatCurrency(weekendStats.weekday.total)}
                                    </span>
                                  </div>
                                  <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-700"
                                      style={{
                                        width: `${(weekendStats.weekday.total / (weekendStats.weekend.total + weekendStats.weekday.total)) * 100}%`
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Smart Recommendations */}
                          {recommendations.length > 0 && (
                            <div className="mb-6 p-5 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                              <div className="flex items-start space-x-3">
                                <svg className="w-6 h-6 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <div className="flex-1">
                                  <h5 className="text-sm font-bold text-blue-600 mb-2">💡 Smart Tips</h5>
                                  <ul className="space-y-1.5">
                                    {recommendations.map((rec, idx) => (
                                      <li key={idx} className="text-sm text-foreground flex items-start">
                                        <span className="mr-2">•</span>
                                        <span>{rec}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Transactions List */}
                          <div>
                            <h4 className="font-semibold text-foreground mb-3">Linked Transactions</h4>

                            {/* Grouped by Weekend */}
                            {weekendGroups.length > 0 ? (
                              <div className="space-y-4">
                                {weekendGroups.map((group, groupIdx) => (
                                  <div key={group.weekend} className="animate-fade-in" style={{ animationDelay: `${groupIdx * 0.1}s` }}>
                                    <div className="mb-3 p-3 bg-red-500/5 border border-red-500/20 rounded-lg">
                                      <div className="flex items-center justify-between">
                                        <h5 className="text-sm font-bold text-red-600">
                                          Weekend of {formatDate(group.weekend)}
                                        </h5>
                                        <span className="text-sm font-semibold text-red-600">
                                          {group.transactions.length} transactions • {formatCurrency(group.total)}
                                        </span>
                                      </div>
                                    </div>

                                    <div className="space-y-2 ml-4">
                                      {group.transactions.map((txn, txnIdx) => (
                                        <div
                                          key={txn.id}
                                          className="p-4 bg-background rounded-lg border border-border hover:border-red-500/50 hover:shadow-md transition-all duration-200 hover:scale-[1.01] animate-slide-in"
                                          style={{ animationDelay: `${(groupIdx * 0.1) + (txnIdx * 0.05)}s` }}
                                        >
                                          <div className="flex items-center justify-between">
                                            <div className="flex-1">
                                              <div className="flex items-center space-x-2 mb-1">
                                                <h6 className="font-semibold text-foreground">{txn.merchant_name}</h6>
                                                {topExpenses.has(txn.id) && (
                                                  <span className="px-2 py-1 bg-red-500/10 text-red-600 text-xs font-bold rounded flex items-center space-x-1">
                                                    <span>🔥</span>
                                                    <span>Top Expense</span>
                                                  </span>
                                                )}
                                              </div>
                                              <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                                                <span>{formatDate(txn.transaction_date)}</span>
                                                <span>•</span>
                                                <span className="font-medium">{txn.category_name}</span>
                                              </div>
                                              {txn.description && (
                                                <p className="text-xs text-muted-foreground mt-1">{txn.description}</p>
                                              )}
                                            </div>
                                            <div className="text-right ml-4">
                                              <p className="text-lg font-bold text-foreground">
                                                {formatCurrency(txn.amount)}
                                              </p>
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              // Regular List (for non-weekend insights)
                              <div className="space-y-2">
                                {transactions.map((txn, idx) => (
                                  <div
                                    key={txn.id}
                                    className="p-4 bg-background rounded-lg border border-border hover:border-primary/50 hover:shadow-md transition-all duration-200 hover:scale-[1.01] animate-slide-in"
                                    style={{ animationDelay: `${idx * 0.05}s` }}
                                  >
                                    <div className="flex items-center justify-between">
                                      <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-1">
                                          <h6 className="font-semibold text-foreground">{txn.merchant_name}</h6>
                                          {topExpenses.has(txn.id) && (
                                            <span className="px-2 py-1 bg-amber-500/10 text-amber-600 text-xs font-bold rounded flex items-center space-x-1">
                                              <span>🔥</span>
                                              <span>Top Expense</span>
                                            </span>
                                          )}
                                        </div>
                                        <div className="flex items-center space-x-3 text-sm text-muted-foreground">
                                          <span>{formatDate(txn.transaction_date)}</span>
                                          <span>•</span>
                                          <span className="font-medium">{txn.category_name}</span>
                                        </div>
                                        {txn.description && (
                                          <p className="text-xs text-muted-foreground mt-1">{txn.description}</p>
                                        )}
                                      </div>
                                      <div className="text-right ml-4">
                                        <p className="text-lg font-bold text-foreground">
                                          {formatCurrency(txn.amount)}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
