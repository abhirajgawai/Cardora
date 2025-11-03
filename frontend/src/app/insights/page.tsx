'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { getInsights, getInsightTransactions, dismissInsight, generateInsights, Insight, InsightTransaction } from '@/features/insights';
import Sidebar from '@/shared/components/layout/Sidebar';

interface GroupedTransactions {
  weekend: string;
  transactions: InsightTransaction[];
  total: number;
}

export default function InsightsPage() {
  const router = useRouter();
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInsight, setSelectedInsight] = useState<Insight | null>(null);
  const [transactions, setTransactions] = useState<InsightTransaction[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [transactionsSummary, setTransactionsSummary] = useState<{ total_amount: number; transaction_count: number } | null>(null);
  const [generatingInsights, setGeneratingInsights] = useState(false);
  const [visibleTransactionCount, setVisibleTransactionCount] = useState<{ [key: string]: number }>({});
  const [isModalOpen, setIsModalOpen] = useState(false);

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

  const handleOpenInsight = async (insight: Insight) => {
    setSelectedInsight(insight);
    setIsModalOpen(true);
    setTransactionsLoading(true);

    // Load transactions if insight type supports it
    if (['subscription_detection', 'transport_savings', 'recurring_habit', 'weekend_spending'].includes(insight.insight_type)) {
      try {
        const response = await getInsightTransactions(insight.id);
        setTransactions(response.transactions);
        setTransactionsSummary(response.summary);
        // Initialize with 5 visible transactions
        setVisibleTransactionCount({ [insight.id]: 5 });
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
        toast.error('Load Failed', {
          description: 'Failed to load transactions. Please try again.',
        });
      } finally {
        setTransactionsLoading(false);
      }
    } else {
      setTransactionsLoading(false);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedInsight(null);
    setTransactions([]);
    setTransactionsSummary(null);
    setVisibleTransactionCount({});
  };

  const loadMoreTransactions = (insightId: string) => {
    setVisibleTransactionCount(prev => ({
      ...prev,
      [insightId]: (prev[insightId] || 5) + 10
    }));
  };

  const showAllTransactions = (insightId: string) => {
    setVisibleTransactionCount(prev => ({
      ...prev,
      [insightId]: transactions.length
    }));
  };

  const handleDismiss = async (insightId: string) => {
    try {
      await dismissInsight(insightId);
      setInsights(prev => prev.filter(i => i.id !== insightId));
      // Close modal if this insight was open
      if (selectedInsight?.id === insightId) {
        handleCloseModal();
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

  // Get insight type icon and color
  const getInsightTypeIcon = (insightType: string, insightTitle?: string) => {
    // Special handling for positive recurring_habit insight
    if (insightType === 'recurring_habit' && insightTitle?.toLowerCase().includes('no recurring')) {
      return {
        icon: '🏆',
        color: '#10B981', // Emerald (positive green)
        bgColor: '#10B98115'
      };
    }

    const iconMap: Record<string, { icon: string; color: string; bgColor: string }> = {
      'subscription': {
        icon: '💳',
        color: '#8B5CF6', // Purple
        bgColor: '#8B5CF615'
      },
      'subscription_detection': {
        icon: '💳',
        color: '#8B5CF6', // Purple
        bgColor: '#8B5CF615'
      },
      'weekend_spending': {
        icon: '📅',
        color: '#F59E0B', // Amber
        bgColor: '#F59E0B15'
      },
      'recurring_habit': {
        icon: '🔄',
        color: '#10B981', // Emerald
        bgColor: '#10B98115'
      },
      'transport_savings': {
        icon: '🚗',
        color: '#00E0A1', // Teal
        bgColor: '#00E0A115'
      },
      'smart_spending_praise': {
        icon: '⭐',
        color: '#4B6EF5', // Indigo
        bgColor: '#4B6EF515'
      },
      'ai_personalized': {
        icon: '💡',
        color: '#4B6EF5', // Indigo
        bgColor: '#4B6EF515'
      }
    };

    return iconMap[insightType] || { icon: '💡', color: '#4B6EF5', bgColor: '#4B6EF515' };
  };

  // Get category icon
  const getCategoryIcon = (categoryName: string): string => {
    const iconMap: Record<string, string> = {
      'Groceries': '🛒',
      'Flights & Travel': '✈️',
      'Transport': '🚗',
      'Dining': '🍽️',
      'Shopping': '🛍️',
      'Bills & Utilities': '📄',
      'Entertainment': '🎮',
      'Healthcare': '⚕️',
      'Clothing & Apparel': '👕',
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
      'Others': '📦',
      'Uncategorized': '❓',
    };
    return iconMap[categoryName] || '📦';
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {insights.map((insight, index) => {
                const insightIcon = getInsightTypeIcon(insight.insight_type, insight.title);
                const hasTransactions = ['subscription_detection', 'transport_savings', 'recurring_habit', 'weekend_spending'].includes(insight.insight_type);
                const hasSavings = insight.potential_savings && insight.potential_savings > 0 &&
                                   ['subscription_detection', 'transport_savings', 'recurring_habit'].includes(insight.insight_type);

                return (
                  <div
                    key={insight.id}
                    onClick={() => handleOpenInsight(insight)}
                    className="fintech-card p-6 text-left hover:shadow-xl hover:scale-[1.02] transition-all duration-200 animate-slide-in cursor-pointer"
                    style={{ animationDelay: `${index * 0.1}s` }}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleOpenInsight(insight);
                      }
                    }}
                  >
                    {/* Icon & Dismiss Button */}
                    <div className="flex items-start justify-between mb-4">
                      <div
                        className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl shadow-sm"
                        style={{ backgroundColor: insightIcon.bgColor }}
                      >
                        {insightIcon.icon}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDismiss(insight.id);
                        }}
                        className="p-1.5 rounded-lg bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                        title="Dismiss"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-bold text-foreground mb-3 line-clamp-2">
                      {insight.title}
                    </h3>

                    {/* Impact Badge */}
                    <div className="flex items-center gap-2 mb-4">
                      <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${getImpactBadgeColor(insight.impact_score)}`}>
                        {getImpactLabel(insight.impact_score)}
                      </span>
                    </div>

                    {/* Savings Display */}
                    {hasSavings ? (
                      <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20">
                        <p className="text-xs text-muted-foreground uppercase tracking-wide font-bold mb-1">
                          Save Monthly
                        </p>
                        <p className="text-2xl font-bold text-green-600">
                          {formatCurrency(insight.potential_savings ?? 0)}
                        </p>
                      </div>
                    ) : (
                      <div className="text-sm text-muted-foreground line-clamp-2">
                        {insight.description}
                      </div>
                    )}

                    {/* View Details Indicator */}
                    <div className="mt-4 pt-4 border-t border-border flex items-center justify-between text-sm">
                      <span className="text-primary font-semibold">View Details</span>
                      <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Modal for Insight Details */}
          {isModalOpen && selectedInsight && (
            <div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in"
              onClick={handleCloseModal}
            >
              <div
                className="bg-card rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden animate-scale-in"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div className="p-6 border-b border-border">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-4 flex-1">
                      <div
                        className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl shadow-sm flex-shrink-0"
                        style={{ backgroundColor: getInsightTypeIcon(selectedInsight.insight_type, selectedInsight.title).bgColor }}
                      >
                        {getInsightTypeIcon(selectedInsight.insight_type, selectedInsight.title).icon}
                      </div>
                      <div className="flex-1">
                        <h2 className="text-2xl font-bold text-foreground mb-2">
                          {selectedInsight.title}
                        </h2>
                        <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${getImpactBadgeColor(selectedInsight.impact_score)}`}>
                          {getImpactLabel(selectedInsight.impact_score)}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={handleCloseModal}
                      className="p-2 rounded-lg bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors flex-shrink-0"
                      title="Close"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Modal Body */}
                <div className="overflow-y-auto max-h-[calc(90vh-140px)]">
                  <div className="p-6 space-y-6">
                    {/* Description */}
                    <div>
                      <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wide mb-3">
                        Details
                      </h3>
                      <p className="text-foreground leading-relaxed whitespace-pre-line">
                        {selectedInsight.description}
                      </p>
                    </div>

                    {/* Savings Display */}
                    {selectedInsight.potential_savings && selectedInsight.potential_savings > 0 &&
                     ['subscription_detection', 'transport_savings', 'recurring_habit'].includes(selectedInsight.insight_type) && (
                      <div className="p-6 rounded-xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20">
                        <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wide mb-2">
                          Potential Monthly Savings
                        </h3>
                        <p className="text-4xl font-bold text-green-600">
                          {formatCurrency(selectedInsight.potential_savings)}
                        </p>
                        <p className="text-sm text-muted-foreground mt-2">
                          That's {formatCurrency(selectedInsight.potential_savings * 12)} per year!
                        </p>
                      </div>
                    )}

                    {/* Linked Transactions */}
                    {['subscription_detection', 'transport_savings', 'recurring_habit', 'weekend_spending'].includes(selectedInsight.insight_type) && (
                      <div>
                        <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wide mb-4">
                          Linked Transactions
                        </h3>

                        {transactionsLoading ? (
                          <div className="text-center py-8">
                            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                            <p className="text-muted-foreground">Loading transactions...</p>
                          </div>
                        ) : transactions.length > 0 ? (
                          <>
                            {/* Transaction Summary */}
                            {transactionsSummary && (
                              <div className="mb-4 p-4 bg-muted/50 rounded-lg flex items-center justify-between">
                                <div>
                                  <p className="text-sm text-muted-foreground">Total Amount</p>
                                  <p className="text-2xl font-bold text-foreground">
                                    {formatCurrency(transactionsSummary.total_amount)}
                                  </p>
                                </div>
                                <div className="text-right">
                                  <p className="text-sm text-muted-foreground">Transactions</p>
                                  <p className="text-2xl font-bold text-foreground">
                                    {transactionsSummary.transaction_count}
                                  </p>
                                </div>
                              </div>
                            )}

                            {/* Transactions List */}
                            <div className="space-y-3">
                              {(() => {
                                const visibleCount = visibleTransactionCount[selectedInsight.id] || 5;
                                const visibleTxns = transactions.slice(0, visibleCount);
                                const topExpenses = getTopExpenses(transactions);

                                return visibleTxns.map((txn, idx) => (
                                  <div
                                    key={txn.id}
                                    className="p-5 bg-background rounded-xl border border-border hover:border-primary/50 hover:shadow-lg transition-all duration-200 animate-slide-in"
                                    style={{ animationDelay: `${idx * 0.05}s` }}
                                  >
                                    <div className="flex items-center gap-4">
                                      {/* Category Icon */}
                                      <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center text-2xl flex-shrink-0">
                                        {getCategoryIcon(txn.category_name)}
                                      </div>

                                      {/* Transaction Details */}
                                      <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                                          <h6 className="font-bold text-foreground text-base">{txn.merchant_name}</h6>
                                          {topExpenses.has(txn.id) && (
                                            <span className="px-2 py-1 bg-amber-500/10 text-amber-600 text-xs font-bold rounded-lg flex items-center gap-1">
                                              <span>🔥</span>
                                              <span>Top Expense</span>
                                            </span>
                                          )}
                                        </div>
                                        <div className="flex items-center gap-3 text-sm text-muted-foreground mb-1 flex-wrap">
                                          <span className="flex items-center gap-1.5">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                            {formatDate(txn.transaction_date)}
                                          </span>
                                          <span>•</span>
                                          <span className="font-semibold">{txn.category_name}</span>
                                        </div>
                                        {txn.description && (
                                          <p className="text-xs text-muted-foreground">{txn.description}</p>
                                        )}
                                      </div>

                                      {/* Amount */}
                                      <div className="text-right flex-shrink-0">
                                        <p className="text-xl font-bold text-foreground">
                                          {formatCurrency(txn.amount)}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                ));
                              })()}
                            </div>

                            {/* Show More / Show All Buttons */}
                            {transactions.length > (visibleTransactionCount[selectedInsight.id] || 5) && (
                              <div className="mt-4 flex items-center justify-center gap-3">
                                <button
                                  onClick={() => loadMoreTransactions(selectedInsight.id)}
                                  className="px-6 py-2.5 bg-muted hover:bg-muted/80 text-foreground font-semibold rounded-lg transition-colors flex items-center gap-2"
                                >
                                  <span>Show More</span>
                                  <span className="text-xs text-muted-foreground">
                                    (+10 more)
                                  </span>
                                </button>
                                <button
                                  onClick={() => showAllTransactions(selectedInsight.id)}
                                  className="px-6 py-2.5 bg-primary hover:bg-primary/90 text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
                                >
                                  <span>Show All</span>
                                  <span className="text-xs opacity-80">
                                    ({transactions.length} total)
                                  </span>
                                </button>
                              </div>
                            )}
                          </>
                        ) : (
                          <p className="text-center text-muted-foreground py-8">
                            No transactions available for this insight.
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Modal Footer */}
                <div className="p-6 border-t border-border bg-muted/20">
                  <div className="flex items-center justify-between gap-4">
                    <button
                      onClick={() => {
                        handleDismiss(selectedInsight.id);
                      }}
                      className="px-6 py-2.5 bg-muted hover:bg-muted/80 text-foreground font-semibold rounded-xl transition-colors"
                    >
                      Dismiss Insight
                    </button>
                    <button
                      onClick={handleCloseModal}
                      className="px-6 py-2.5 gradient-indigo-purple text-white font-semibold rounded-xl btn-hover-accent shadow-lg"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
