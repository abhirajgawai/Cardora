'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { getTransactions } from '@/lib/api/transactions';
import { getCards } from '@/lib/api/cards';
import { getInsights, Insight } from '@/lib/api/insights';
import { getStatements } from '@/lib/api/statements';
import { Transaction, CreditCard, Statement } from '@/models';
import { extractErrorMessage, isAuthError } from '@/lib/utils/errorHandler';
import { formatCardDisplayName } from '@/lib/utils/cardFormatter';
import Sidebar from '@/components/layout/Sidebar';
import Footer from '@/components/layout/Footer';
import TimeRangeSelector, { TimeRange } from '@/components/common/TimeRangeSelector';
import MonthYearPicker, { MonthYearValue } from '@/components/common/MonthYearPicker';
import { SearchableSelect } from '@/components/ui/SearchableSelect';
import InsightsList from '@/components/insights/InsightsList';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  filterTransactionsByTimeRange,
  getTimeRangeLabel,
  calculatePercentageChange,
  getPreviousPeriodDateRange,
  filterTransactionsByDateRange,
} from '@/lib/utils/dateFilters';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Cardora V2 Refined Fintech Color Palette
const FINTECH_COLORS = {
  primary: '#4B6EF5',      // Modern Indigo Blue
  indigo: '#4B6EF5',       // Alias for primary (for chart compatibility)
  accent: '#00E0A1',       // Teal Mint
  teal: '#00E0A1',         // Alias for accent (for chart compatibility)
  navy: '#1E1B4B',         // Deep Navy-Purple
  slate: '#64748B',        // Softer gray-blue
  lightGray: '#E2E8F0',    // Subtle borders
};

const CHART_COLORS = [
  FINTECH_COLORS.primary,   // Modern Indigo - Primary
  FINTECH_COLORS.accent,    // Teal Mint - Accent
  '#F59E0B',                // Amber - Warning
  '#10B981',                // Emerald - Success
  '#8B5CF6',                // Purple - Secondary
  '#60A5FA',                // Sky Blue - Supplementary
  FINTECH_COLORS.slate,     // Slate
  '#FB923C',                // Coral
  FINTECH_COLORS.navy,      // Navy
  FINTECH_COLORS.lightGray, // Light Gray
];

export default function AnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [allTransactions, setAllTransactions] = useState<Transaction[]>([]);
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Time range filter - will be overridden by most recent statement on initial load
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>('all_time');

  // Specific month filter - will be set to most recent statement on initial load
  const [specificMonth, setSpecificMonth] = useState<MonthYearValue | null>(null);

  // Category drill-down modal state
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [categoryModalOpen, setCategoryModalOpen] = useState(false);

  // Category expand/collapse state
  const [showAllCategories, setShowAllCategories] = useState(false);
  const TOP_CATEGORIES_COUNT = 6;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [transactionsData, cardsData, insightsData, statementsData] = await Promise.all([
          getTransactions({ limit: 10000 }),
          getCards(),
          getInsights(false).catch(() => ({ insights: [], count: 0 })),
          getStatements().catch(() => []),
        ]);

        setAllTransactions(Array.isArray(transactionsData) ? transactionsData : []);
        setCards(Array.isArray(cardsData) ? cardsData : []);
        setInsights(insightsData?.insights || []);

        // Set default filter to most recent statement on initial load
        if (isInitialLoad && Array.isArray(statementsData) && statementsData.length > 0) {
          const mostRecentStatement = statementsData[0];
          setSpecificMonth({
            month: mostRecentStatement.statement_month,
            year: mostRecentStatement.statement_year
          });
          console.log(`[Analytics] Defaulting to most recent statement: ${mostRecentStatement.statement_month}/${mostRecentStatement.statement_year}`);
        }

        // Mark initial load as complete
        setIsInitialLoad(false);
      } catch (error) {
        console.error('Analytics error:', extractErrorMessage(error));
        if (isAuthError(error)) {
          localStorage.removeItem('access_token');
          router.push('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router, isInitialLoad]);

  // Function to refresh insights after user actions
  const refreshInsights = async () => {
    try {
      const insightsData = await getInsights(false);
      setInsights(insightsData?.insights || []);
    } catch (error) {
      console.error('Failed to refresh insights:', error);
    }
  };

  // Handle insight dismissal
  const handleDismissInsight = async (id: string) => {
    try {
      // Optimistically remove from UI
      setInsights(insights.filter(i => i.id !== id));
      // You can call dismissInsight API here if you have one
      // await dismissInsight(id);
    } catch (error) {
      console.error('Failed to dismiss insight:', error);
      // Refresh on error to restore state
      refreshInsights();
    }
  };

  // Handle time range change
  const handleTimeRangeChange = (newRange: TimeRange) => {
    setSelectedTimeRange(newRange);
    // Clear specific month when time range is changed
    if (newRange !== 'all_time') {
      setSpecificMonth(null);
    }
  };

  // Filter transactions by specific month or time range
  const transactions = useMemo(() => {
    // If specific month is selected, use that instead of time range
    if (specificMonth) {
      return allTransactions.filter(
        (t) => t.statement_month === specificMonth.month && t.statement_year === specificMonth.year
      );
    }
    // Otherwise use time range filter
    return filterTransactionsByTimeRange(allTransactions, selectedTimeRange);
  }, [allTransactions, selectedTimeRange, specificMonth]);

  // Filter transactions by selected card
  const filteredTransactions = useMemo(() => {
    if (!selectedCardId) return transactions;
    return transactions.filter(t => t.card_id === selectedCardId);
  }, [transactions, selectedCardId]);

  // Calculate analytics
  const analytics = useMemo(() => {
    const total = filteredTransactions.reduce((sum, t) => sum + Number(t.amount), 0);
    const count = filteredTransactions.length;
    const avgPerTransaction = count > 0 ? total / count : 0;

    // Monthly average
    const monthsSet = new Set(filteredTransactions.map(t =>
      `${t.statement_year}-${String(t.statement_month).padStart(2, '0')}`
    ));
    const avgPerMonth = monthsSet.size > 0 ? total / monthsSet.size : 0;

    // Most used card
    const cardCounts = new Map<string, number>();
    transactions.forEach(t => {
      if (t.card_id) {
        cardCounts.set(t.card_id, (cardCounts.get(t.card_id) || 0) + 1);
      }
    });
    const mostUsedCardId = Array.from(cardCounts.entries())
      .sort((a, b) => b[1] - a[1])[0]?.[0];
    const mostUsedCard = cards.find(c => c.id === mostUsedCardId);

    return { total, count, avgPerTransaction, avgPerMonth, mostUsedCard };
  }, [filteredTransactions, transactions, cards]);

  // Card comparison data
  const cardComparisonData = useMemo(() => {
    const cardMap = new Map<string, { name: string; total: number; count: number }>();

    transactions.forEach(t => {
      if (t.card_id) {
        const card = cards.find(c => c.id === t.card_id);
        if (card) {
          const formattedName = formatCardDisplayName(card.card_name, card.bank_name, card.card_type, card.last_four_digits);
          const existing = cardMap.get(t.card_id) || { name: formattedName, total: 0, count: 0 };
          existing.total += Number(t.amount);
          existing.count += 1;
          cardMap.set(t.card_id, existing);
        }
      }
    });

    return Array.from(cardMap.values())
      .sort((a, b) => b.total - a.total);
  }, [transactions, cards]);

  // Monthly trends
  const monthlyTrendsData = useMemo(() => {
    const monthMap = new Map<string, number>();

    filteredTransactions.forEach(t => {
      // Use statement_month and statement_year instead of transaction_date
      const month = `${t.statement_year}-${String(t.statement_month).padStart(2, '0')}`;
      monthMap.set(month, (monthMap.get(month) || 0) + Number(t.amount));
    });

    return Array.from(monthMap.entries())
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([month, total]) => ({
        month: new Date(month + '-01').toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
        total: Math.round(total * 100) / 100,
      }));
  }, [filteredTransactions]);

  // Category icon mapping
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

  // Full category breakdown with transaction counts
  const categoryData = useMemo(() => {
    const catMap = new Map<string, { value: number; count: number }>();

    filteredTransactions.forEach(t => {
      const category = t.category?.name || 'Uncategorized';
      const existing = catMap.get(category) || { value: 0, count: 0 };
      existing.value += Number(t.amount);
      existing.count += 1;
      catMap.set(category, existing);
    });

    const total = Array.from(catMap.values()).reduce((sum, val) => sum + val.value, 0);

    return Array.from(catMap.entries())
      .sort((a, b) => b[1].value - a[1].value)
      .map(([name, data], index) => ({
        name,
        value: Math.round(data.value * 100) / 100,
        count: data.count,
        percentage: total > 0 ? Math.round((data.value / total) * 100) : 0,
        icon: getCategoryIcon(name),
        color: CHART_COLORS[index % CHART_COLORS.length],
      }));
  }, [filteredTransactions]);

  // Top merchants
  const topMerchants = useMemo(() => {
    const merchantMap = new Map<string, { total: number; count: number; categories: Map<string, number> }>();

    filteredTransactions.forEach(t => {
      const merchant = t.merchant_name || t.description || 'Unknown';
      const category = t.category?.name || 'Uncategorized';
      const existing = merchantMap.get(merchant) || { total: 0, count: 0, categories: new Map() };
      existing.total += Number(t.amount);
      existing.count += 1;
      existing.categories.set(category, (existing.categories.get(category) || 0) + 1);
      merchantMap.set(merchant, existing);
    });

    return Array.from(merchantMap.entries())
      .sort((a, b) => b[1].total - a[1].total)
      .slice(0, 10)
      .map(([name, data]) => {
        // Find most common category for this merchant
        const mostCommonCategory = Array.from(data.categories.entries())
          .sort((a, b) => b[1] - a[1])[0]?.[0] || 'Uncategorized';

        return {
          name,
          total: Math.round(data.total * 100) / 100,
          count: data.count,
          avgTransaction: Math.round((data.total / data.count) * 100) / 100,
          category: mostCommonCategory,
          categoryIcon: getCategoryIcon(mostCommonCategory),
        };
      });
  }, [filteredTransactions]);

  // Day of week analysis
  const dayOfWeekData = useMemo(() => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const dayMap = new Map(days.map(d => [d, 0]));

    filteredTransactions.forEach(t => {
      const day = days[new Date(t.transaction_date).getDay()];
      dayMap.set(day, (dayMap.get(day) || 0) + Number(t.amount));
    });

    return days.map(day => ({
      day,
      total: Math.round((dayMap.get(day) || 0) * 100) / 100,
    }));
  }, [filteredTransactions]);

  // Weekday vs Weekend analysis
  const weekdayWeekendData = useMemo(() => {
    let weekdayTotal = 0;
    let weekendTotal = 0;
    let weekdayCount = 0;
    let weekendCount = 0;
    const dayTotals = new Map<string, number>();
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    filteredTransactions.forEach(t => {
      const date = new Date(t.transaction_date);
      const dayOfWeek = date.getDay();
      const amount = Number(t.amount);
      const dayName = days[dayOfWeek];

      // Track by day name for finding peak day
      dayTotals.set(dayName, (dayTotals.get(dayName) || 0) + amount);

      // Weekend is Saturday (6) and Sunday (0)
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        weekendTotal += amount;
        weekendCount += 1;
      } else {
        weekdayTotal += amount;
        weekdayCount += 1;
      }
    });

    // Find most expensive day
    const peakDay = Array.from(dayTotals.entries())
      .sort((a, b) => b[1] - a[1])[0];

    return {
      weekday: {
        total: Math.round(weekdayTotal * 100) / 100,
        count: weekdayCount,
        avgPerDay: weekdayCount > 0 ? Math.round((weekdayTotal / weekdayCount) * 100) / 100 : 0,
      },
      weekend: {
        total: Math.round(weekendTotal * 100) / 100,
        count: weekendCount,
        avgPerDay: weekendCount > 0 ? Math.round((weekendTotal / weekendCount) * 100) / 100 : 0,
      },
      peakDay: peakDay ? { day: peakDay[0], amount: Math.round(peakDay[1] * 100) / 100 } : null,
      totalTransactions: weekdayCount + weekendCount,
    };
  }, [filteredTransactions]);

  // Transactions for selected category (for modal)
  const categoryTransactions = useMemo(() => {
    if (!selectedCategory) return [];
    return filteredTransactions
      .filter(t => (t.category?.name || 'Uncategorized') === selectedCategory)
      .sort((a, b) => new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime());
  }, [filteredTransactions, selectedCategory]);

  // Handler for clicking on a pie chart segment
  const handleCategoryClick = (categoryName: string) => {
    setSelectedCategory(categoryName);
    setCategoryModalOpen(true);
  };

  // Get card name by ID (helper function for modal)
  const getCardName = (cardId: string): string => {
    const card = cards.find((c) => c.id === cardId);
    if (!card) return 'Unknown Card';
    return formatCardDisplayName(card.card_name, card.bank_name, card.card_type, card.last_four_digits);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen fintech-bg">
      <Sidebar />

      <div className="flex-1 ml-64">
        {/* Header */}
        <header className="bg-card border-b border-border px-8 py-5">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-foreground mb-0.5">
                Analytics Dashboard
              </h1>
              <p className="text-sm text-muted-foreground">
                Deep insights into your spending patterns
              </p>
            </div>
            <TimeRangeSelector value={selectedTimeRange} onChange={handleTimeRangeChange} />
          </div>
        </header>

        <main className="px-8 py-5">
          {/* Time Range Indicator */}
          <div className="mb-4 flex items-center space-x-2 text-sm text-muted-foreground">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>
              Analyzing data from{' '}
              <strong className="text-foreground">
                {specificMonth
                  ? `${new Date(specificMonth.year, specificMonth.month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}`
                  : getTimeRangeLabel(selectedTimeRange)
                }
              </strong>
            </span>
          </div>

          {/* Filters */}
          <div className="fintech-card p-6 mb-6 animate-slide-in">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground">Filters</h3>
              {(specificMonth || selectedCardId) && (
                <button
                  onClick={() => {
                    setSpecificMonth(null);
                    setSelectedCardId(null);
                  }}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Clear all
                </button>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-4">
              {/* Specific Month Filter */}
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Specific Month
                </label>
                <MonthYearPicker
                  value={specificMonth}
                  onChange={(value) => {
                    setSpecificMonth(value);
                    if (value) {
                      // Clear time range when specific month is selected
                      setSelectedTimeRange('all_time');
                    }
                  }}
                />
              </div>

              {/* Card Filter */}
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Filter by Card
                </label>
                <SearchableSelect
                  options={[
                    { value: '', label: 'All Cards' },
                    ...cards.map(card => ({
                      value: card.id,
                      label: formatCardDisplayName(card.card_name, card.bank_name, card.card_type, card.last_four_digits)
                    }))
                  ]}
                  value={selectedCardId || ''}
                  onChange={(value) => setSelectedCardId(value || null)}
                  placeholder="Select a card..."
                  searchPlaceholder="Search cards..."
                  emptyMessage="No card found."
                />
              </div>
            </div>
          </div>

          {/* AI Insights Section */}
          {insights.length > 0 && (
            <div className="mb-6">
              <div className="mb-4">
                <h2 className="text-lg font-bold text-foreground mb-1">AI-Powered Insights</h2>
                <p className="text-sm text-muted-foreground">
                  Personalized spending insights generated by AI
                </p>
              </div>
              <InsightsList insights={insights} onDismiss={handleDismissInsight} />
            </div>
          )}

          {/* Overview KPIs */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
            <div className="fintech-card card-accent-indigo p-5 animate-slide-in" style={{ animationDelay: "0.1s" }}>
              <div className="flex items-center justify-between mb-3">
                <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Total Spending</h3>
              <p className="text-2xl font-bold text-foreground mb-1">
                ${analytics.total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-muted-foreground">{analytics.count} transactions</p>
            </div>

            <div className="fintech-card card-accent-teal p-5 animate-slide-in" style={{ animationDelay: "0.2s" }}>
              <div className="flex items-center justify-between mb-3">
                <div className="w-11 h-11 rounded-xl bg-accent/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Avg / Month</h3>
              <p className="text-2xl font-bold text-foreground mb-1">
                ${analytics.avgPerMonth.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-muted-foreground">Monthly average</p>
            </div>

            <div className="fintech-card card-accent-amber p-5 animate-slide-in" style={{ animationDelay: "0.3s" }}>
              <div className="flex items-center justify-between mb-3">
                <div className="w-11 h-11 rounded-xl bg-secondary/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
              <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Avg Transaction</h3>
              <p className="text-2xl font-bold text-foreground mb-1">
                ${analytics.avgPerTransaction.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-muted-foreground">Per transaction</p>
            </div>

            <div className="fintech-card card-accent-emerald p-5 animate-slide-in" style={{ animationDelay: "0.4s" }}>
              <div className="flex items-center justify-between mb-3">
                <div className="w-11 h-11 rounded-xl gradient-indigo-purple flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
              </div>
              <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Most Used Card</h3>
              <p className="text-lg font-bold text-foreground mb-1 truncate">
                {analytics.mostUsedCard ? formatCardDisplayName(analytics.mostUsedCard.card_name, analytics.mostUsedCard.bank_name, analytics.mostUsedCard.card_type, analytics.mostUsedCard.last_four_digits) : 'N/A'}
              </p>
              <p className="text-xs text-muted-foreground">Based on transaction count</p>
            </div>
          </div>

          {/* Charts Row 1 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
            {/* Card Comparison - Smart Layout */}
            {cardComparisonData.length === 1 ? (
              /* Single Card - Show as enhanced KPI */
              <div className="fintech-card chart-card p-5 animate-slide-in" style={{ animationDelay: "0.5s" }}>
                <div className="mb-4">
                  <h3 className="text-base font-bold text-foreground mb-0.5">Card Activity</h3>
                  <p className="text-xs text-muted-foreground">Your spending overview</p>
                </div>
                <div className="h-[280px] flex flex-col items-center justify-center">
                  <div className="w-20 h-20 rounded-full gradient-indigo-purple flex items-center justify-center mb-4">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                    </svg>
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-muted-foreground mb-2">{cardComparisonData[0].name}</p>
                    <p className="text-3xl font-bold text-foreground mb-2">
                      ${cardComparisonData[0].total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {cardComparisonData[0].count} transaction{cardComparisonData[0].count !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              /* Multiple Cards - Show comparison chart */
              <div className="fintech-card chart-card p-5 animate-slide-in" style={{ animationDelay: "0.5s" }}>
                <div className="mb-4">
                  <h3 className="text-base font-bold text-foreground mb-0.5">Card Comparison</h3>
                  <p className="text-xs text-muted-foreground">Total spending by card</p>
                </div>
                {cardComparisonData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={cardComparisonData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" opacity={0.3} />
                      <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 11 }} stroke="#CBD5E1" />
                      <YAxis tick={{ fill: '#64748B', fontSize: 11 }} stroke="#CBD5E1" tickFormatter={(value: number) => `$${value.toLocaleString()}`} />
                      <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}`, 'Total']} contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '8px 12px' }} />
                      <Bar dataKey="total" fill={FINTECH_COLORS.indigo} radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[280px] flex items-center justify-center text-muted-foreground">No card data</div>
                )}
              </div>
            )}

            {/* Monthly Trends */}
            <div className="fintech-card chart-card p-5 animate-slide-in" style={{ animationDelay: "0.6s" }}>
              <div className="mb-4">
                <h3 className="text-base font-bold text-foreground mb-0.5">Monthly Trends</h3>
                <p className="text-xs text-muted-foreground">Spending over time</p>
              </div>
              {monthlyTrendsData.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={monthlyTrendsData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" opacity={0.3} />
                    <XAxis dataKey="month" tick={{ fill: '#64748B', fontSize: 11 }} stroke="#CBD5E1" />
                    <YAxis tick={{ fill: '#64748B', fontSize: 11 }} stroke="#CBD5E1" tickFormatter={(value: number) => `$${value.toLocaleString()}`} />
                    <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}`, 'Total']} contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '8px 12px' }} />
                    <Line type="monotone" dataKey="total" stroke={FINTECH_COLORS.teal} strokeWidth={2.5} dot={{ fill: FINTECH_COLORS.teal, r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[280px] flex items-center justify-center text-muted-foreground">No trend data</div>
              )}
            </div>
          </div>

          {/* Category Breakdown - Full Width */}
          <div className="fintech-card chart-card p-6 mb-6 animate-slide-in" style={{ animationDelay: "0.7s" }}>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-foreground mb-0.5">Spending by Category</h3>
                <p className="text-xs text-muted-foreground">Click on any category to view detailed transactions</p>
              </div>
              {categoryData.length > TOP_CATEGORIES_COUNT && (
                <button
                  onClick={() => setShowAllCategories(!showAllCategories)}
                  className="text-sm font-medium text-primary hover:text-primary/80 transition-colors flex items-center gap-1"
                >
                  {showAllCategories ? (
                    <>
                      Show Less
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                    </>
                  ) : (
                    <>
                      Show All ({categoryData.length})
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </>
                  )}
                </button>
              )}
            </div>
            {categoryData.length > 0 ? (
              <div className="space-y-3">
                {(showAllCategories ? categoryData : categoryData.slice(0, TOP_CATEGORIES_COUNT)).map((category, index) => (
                  <div key={category.name}>
                    <button
                      onClick={() => handleCategoryClick(category.name)}
                      className="w-full group hover:bg-muted/30 p-4 rounded-xl transition-all duration-200 border border-transparent hover:border-border hover:shadow-sm"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-11 h-11 rounded-xl flex items-center justify-center text-2xl"
                            style={{ backgroundColor: `${category.color}15` }}
                          >
                            {category.icon}
                          </div>
                          <div className="text-left">
                            <div className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors">
                              {category.name}
                            </div>
                            <div className="text-xs text-muted-foreground mt-0.5">
                              {category.count} transaction{category.count !== 1 ? 's' : ''}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-base text-foreground">
                            ${category.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </div>
                          <div className="text-xs text-muted-foreground mt-0.5">
                            {category.percentage}%
                          </div>
                        </div>
                      </div>
                      {/* Progress Bar */}
                      <div className="w-full h-3 bg-muted/50 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500 ease-out"
                          style={{
                            width: `${category.percentage}%`,
                            backgroundColor: category.color,
                          }}
                        />
                      </div>
                    </button>
                    {/* Visual separator after top 3 categories */}
                    {index === 2 && categoryData.length > 3 && (
                      <div className="my-4 border-t border-border"></div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-10 flex items-center justify-center text-muted-foreground">No category data</div>
            )}
          </div>

          {/* Charts Row 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">

            {/* Day of Week */}
            <div className="fintech-card chart-card p-5 animate-slide-in" style={{ animationDelay: "0.8s" }}>
              <div className="mb-4">
                <h3 className="text-base font-bold text-foreground mb-0.5">Day of Week Analysis</h3>
                <p className="text-xs text-muted-foreground">When do you spend most?</p>
              </div>
              {dayOfWeekData.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={dayOfWeekData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" opacity={0.3} />
                    <XAxis dataKey="day" tick={{ fill: '#64748B', fontSize: 11 }} stroke="#CBD5E1" />
                    <YAxis tick={{ fill: '#64748B', fontSize: 11 }} stroke="#CBD5E1" tickFormatter={(value: number) => `$${value.toLocaleString()}`} />
                    <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}`, 'Total']} contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '8px 12px' }} />
                    <Bar dataKey="total" fill={FINTECH_COLORS.primary} radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[280px] flex items-center justify-center text-muted-foreground">No day data</div>
              )}
            </div>

            {/* Weekday vs Weekend Comparison */}
            <div className="fintech-card chart-card p-5 animate-slide-in" style={{ animationDelay: "0.9s" }}>
              <div className="mb-4">
                <h3 className="text-base font-bold text-foreground mb-0.5">Weekday vs Weekend</h3>
                <p className="text-xs text-muted-foreground">Spending pattern comparison</p>
              </div>
              {weekdayWeekendData.totalTransactions > 0 ? (
                <div className="h-[280px] flex flex-col justify-between">
                  {/* Comparison Cards */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    {/* Weekday Card */}
                    <div className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl p-4 border border-primary/20">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                          <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <span className="text-xs font-bold text-primary uppercase tracking-wider">Weekdays</span>
                      </div>
                      <p className="text-2xl font-bold text-foreground mb-1">
                        ${weekdayWeekendData.weekday.total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </p>
                      <p className="text-xs text-muted-foreground mb-2">
                        {weekdayWeekendData.weekday.count} transactions
                      </p>
                      <div className="pt-2 border-t border-primary/20">
                        <p className="text-xs text-muted-foreground">Avg per transaction</p>
                        <p className="text-sm font-semibold text-foreground">
                          ${weekdayWeekendData.weekday.avgPerDay.toFixed(2)}
                        </p>
                      </div>
                    </div>

                    {/* Weekend Card */}
                    <div className="bg-gradient-to-br from-accent/10 to-accent/5 rounded-xl p-4 border border-accent/20">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center">
                          <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <span className="text-xs font-bold text-accent uppercase tracking-wider">Weekend</span>
                      </div>
                      <p className="text-2xl font-bold text-foreground mb-1">
                        ${weekdayWeekendData.weekend.total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </p>
                      <p className="text-xs text-muted-foreground mb-2">
                        {weekdayWeekendData.weekend.count} transactions
                      </p>
                      <div className="pt-2 border-t border-accent/20">
                        <p className="text-xs text-muted-foreground">Avg per transaction</p>
                        <p className="text-sm font-semibold text-foreground">
                          ${weekdayWeekendData.weekend.avgPerDay.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Peak Day Highlight */}
                  {weekdayWeekendData.peakDay && (
                    <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent rounded-xl p-4 border border-amber-500/20">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center">
                            <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                          </div>
                          <div>
                            <p className="text-xs font-medium text-muted-foreground mb-0.5">Most Expensive Day</p>
                            <p className="text-sm font-bold text-foreground">{weekdayWeekendData.peakDay.day}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-bold text-foreground">
                            ${weekdayWeekendData.peakDay.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </p>
                          <p className="text-xs text-muted-foreground">total spent</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-[280px] flex items-center justify-center text-muted-foreground">No data available</div>
              )}
            </div>
          </div>

          {/* Top Merchants Table */}
          <div className="fintech-card overflow-hidden animate-slide-in" style={{ animationDelay: "1.0s" }}>
            <div className="px-5 py-4 border-b border-border">
              <h3 className="text-base font-bold text-foreground">Top Merchants</h3>
              <p className="text-xs text-muted-foreground mt-0.5">Your most frequented places</p>
            </div>
            <div className="overflow-x-auto">
              {topMerchants.length > 0 ? (
                <Table>
                  <TableHeader className="bg-muted/20">
                    <TableRow className="hover:bg-muted/20">
                      <TableHead className="px-5 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider w-16">#</TableHead>
                      <TableHead className="px-5 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Merchant</TableHead>
                      <TableHead className="px-5 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Category</TableHead>
                      <TableHead className="px-5 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right">Total Spent</TableHead>
                      <TableHead className="px-5 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right">Transactions</TableHead>
                      <TableHead className="px-5 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right">Avg/Transaction</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {topMerchants.map((merchant, index) => (
                      <TableRow key={index} className="hover:bg-muted/10 transition-all duration-200">
                        <TableCell className="px-5 py-4 text-sm font-bold text-primary">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10">
                            {index + 1}
                          </div>
                        </TableCell>
                        <TableCell className="px-5 py-4 text-sm font-semibold text-foreground">{merchant.name}</TableCell>
                        <TableCell className="px-5 py-4 text-sm">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{merchant.categoryIcon}</span>
                            <span className="text-muted-foreground">{merchant.category}</span>
                          </div>
                        </TableCell>
                        <TableCell className="px-5 py-4 text-right text-sm font-bold text-foreground">
                          ${merchant.total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="px-5 py-4 text-right text-sm text-muted-foreground">
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-primary/10 text-primary font-medium">
                            {merchant.count}
                          </span>
                        </TableCell>
                        <TableCell className="px-5 py-4 text-right text-sm text-muted-foreground">
                          ${merchant.avgTransaction.toFixed(2)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="px-5 py-10 text-center text-muted-foreground text-sm">No merchant data available</div>
              )}
            </div>
          </div>
        </main>

        <Footer />
      </div>

      {/* Category Transactions Modal */}
      <Dialog open={categoryModalOpen} onOpenChange={setCategoryModalOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{selectedCategory} Transactions</DialogTitle>
            <DialogDescription>
              {categoryTransactions.length} transaction{categoryTransactions.length !== 1 ? 's' : ''} totaling $
              {categoryTransactions.reduce((sum, t) => sum + Number(t.amount), 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </DialogDescription>
          </DialogHeader>
          <DialogBody>
            {categoryTransactions.length > 0 ? (
              <div className="overflow-x-auto -mx-6">
                <Table>
                  <TableHeader className="bg-muted/20">
                    <TableRow className="hover:bg-muted/20">
                      <TableHead className="px-4 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider w-[100px]">
                        Date
                      </TableHead>
                      <TableHead className="px-4 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
                        Description
                      </TableHead>
                      <TableHead className="px-4 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider w-[140px]">
                        Merchant
                      </TableHead>
                      <TableHead className="px-4 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider w-[180px]">
                        Card
                      </TableHead>
                      <TableHead className="px-4 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right w-[100px]">
                        Amount
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {categoryTransactions.map((transaction) => (
                      <TableRow key={transaction.id} className="hover:bg-muted/10 transition-all duration-200">
                        <TableCell className="px-4 py-3 whitespace-nowrap text-xs text-muted-foreground">
                          {new Date(transaction.transaction_date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                          })}
                        </TableCell>
                        <TableCell className="px-4 py-3 text-sm">
                          <div className="font-semibold text-foreground truncate max-w-[200px]">{transaction.description}</div>
                        </TableCell>
                        <TableCell className="px-4 py-3 text-xs text-muted-foreground">
                          <span className="truncate block max-w-[130px]">{transaction.merchant_name || '-'}</span>
                        </TableCell>
                        <TableCell className="px-4 py-3 whitespace-nowrap text-xs text-muted-foreground">
                          <span className="truncate block max-w-[170px]">{getCardName(transaction.card_id)}</span>
                        </TableCell>
                        <TableCell className="px-4 py-3 whitespace-nowrap text-right text-sm font-bold text-foreground">
                          ${Number(transaction.amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="px-6 py-12 text-center text-muted-foreground">
                No transactions found for this category
              </div>
            )}
          </DialogBody>
          <DialogFooter>
            <button
              onClick={() => setCategoryModalOpen(false)}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Close
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
