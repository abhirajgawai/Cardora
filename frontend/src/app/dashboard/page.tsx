'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { getCurrentUser } from '@/features/auth';
import { getCards } from '@/features/cards';
import { getTransactions } from '@/features/transactions';
import { getStatements } from '@/features/statements';
import { User } from '@/features/auth/types';
import { CreditCard } from '@/features/cards/types';
import { Transaction } from '@/features/transactions/types';
import { Statement } from '@/features/statements/types';
import { DashboardStats } from '@/shared/types';
import { LineChartData, PieChartData } from '@/features/analytics/types/chart';
import { extractErrorMessage, isAuthError } from '@/shared/lib/utils/errorHandler';
import { formatCurrency } from '@/shared/lib/utils/formatCurrency';
import { CHART_COLORS } from '@/shared/lib/utils/colors';
import Sidebar from '@/shared/components/layout/Sidebar';
import Footer from '@/shared/components/layout/Footer';
import PaymentAlertBanner from '@/features/insights/components/PaymentAlertBanner';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';


export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [statements, setStatements] = useState<Statement[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      // Check if user is authenticated before making API calls
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (!token) {
          router.push('/login');
          return;
        }
      }

      try {
        // Fetch user data
        const userData = await getCurrentUser();
        setUser(userData);

        // Fetch cards, transactions, and statements separately to handle errors better
        let cardsData: CreditCard[] = [];
        let transactionsData: Transaction[] = [];
        let statementsData: Statement[] = [];

        try {
          cardsData = await getCards();
          if (!Array.isArray(cardsData)) cardsData = [];
        } catch (cardError) {
          cardsData = [];
        }
        setCards(cardsData);

        try {
          transactionsData = await getTransactions({ limit: 10000 });
          if (!Array.isArray(transactionsData)) transactionsData = [];
        } catch (transactionError) {
          transactionsData = [];
        }
        setTransactions(transactionsData);

        try {
          statementsData = await getStatements();
          if (!Array.isArray(statementsData)) statementsData = [];
        } catch (statementError) {
          statementsData = [];
        }
        setStatements(statementsData);
      } catch (error) {
        if (!isAuthError(error)) {
          setError(extractErrorMessage(error));
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  // Calculate stats for all transactions
  const stats = useMemo(() => {
    const totalSpending = transactions.reduce(
      (sum, t) => sum + Number(t.amount),
      0
    );

    const transactionsWithConfidence = transactions.filter(
      (t) => t.confidence_score !== null
    );

    const avgConfidence =
      transactionsWithConfidence.length > 0
        ? transactionsWithConfidence.reduce(
            (sum, t) => sum + (Number(t.confidence_score) || 0) * 100,
            0
          ) / transactionsWithConfidence.length
        : 93;

    return {
      totalSpending,
      transactionCount: transactions.length,
      cardCount: cards.length,
      avgConfidence: Math.round(avgConfidence),
    };
  }, [transactions, cards]);

  // Process spending trend data (last 6 months)
  const spendingTrendData = useMemo(() => {
    const trendMap = new Map<string, number>();
    transactions.forEach((t) => {
      // Use statement_month and statement_year instead of transaction_date
      const monthKey = `${t.statement_year}-${String(t.statement_month).padStart(2, '0')}`;
      trendMap.set(monthKey, (trendMap.get(monthKey) || 0) + Number(t.amount));
    });

    return Array.from(trendMap.entries())
      .sort((a, b) => a[0].localeCompare(b[0]))
      .slice(-6) // Last 6 months
      .map(([month, amount]) => ({
        month: new Date(month + '-01').toLocaleDateString('en-US', {
          month: 'short',
          year: 'numeric',
        }),
        spending: Math.round(amount * 100) / 100,
      }));
  }, [transactions]);

  // Category icon mapping
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
      'Others': '📦',
      'Uncategorized': '❓',
    };
    return iconMap[categoryName] || '📦';
  };

  // Process category data with counts, icons, and colors
  const categoryData = useMemo(() => {
    const categoryMap = new Map<string, { value: number; count: number }>();
    transactions.forEach((t) => {
      const categoryName = t.category?.name || 'Uncategorized';
      const existing = categoryMap.get(categoryName) || { value: 0, count: 0 };
      existing.value += Number(t.amount);
      existing.count += 1;
      categoryMap.set(categoryName, existing);
    });

    const total = Array.from(categoryMap.values()).reduce((sum, val) => sum + val.value, 0);

    return Array.from(categoryMap.entries())
      .sort((a, b) => b[1].value - a[1].value)
      .slice(0, 5) // Top 5 categories
      .map(([name, data], index) => ({
        name,
        value: Math.round(data.value * 100) / 100,
        count: data.count,
        percentage: total > 0 ? Math.round((data.value / total) * 100) : 0,
        icon: getCategoryIcon(name),
        color: CHART_COLORS[index % CHART_COLORS.length],
      }));
  }, [transactions]);


  // Recent transactions (last 7)
  const recentTransactions = useMemo(() => {
    return [...transactions]
      .sort((a, b) => new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime())
      .slice(0, 7);
  }, [transactions]);

  // Month over month comparison
  const monthComparison = useMemo(() => {
    const now = new Date();
    const currentMonth = now.getMonth() + 1;
    const currentYear = now.getFullYear();
    const lastMonth = currentMonth === 1 ? 12 : currentMonth - 1;
    const lastMonthYear = currentMonth === 1 ? currentYear - 1 : currentYear;

    const currentMonthTotal = transactions
      .filter(t => t.statement_month === currentMonth && t.statement_year === currentYear)
      .reduce((sum, t) => sum + Number(t.amount), 0);

    const lastMonthTotal = transactions
      .filter(t => t.statement_month === lastMonth && t.statement_year === lastMonthYear)
      .reduce((sum, t) => sum + Number(t.amount), 0);

    const currentMonthCount = transactions
      .filter(t => t.statement_month === currentMonth && t.statement_year === currentYear)
      .length;

    const lastMonthCount = transactions
      .filter(t => t.statement_month === lastMonth && t.statement_year === lastMonthYear)
      .length;

    const change = lastMonthTotal > 0
      ? ((currentMonthTotal - lastMonthTotal) / lastMonthTotal) * 100
      : 0;

    return {
      currentMonth: { total: currentMonthTotal, count: currentMonthCount },
      lastMonth: { total: lastMonthTotal, count: lastMonthCount },
      change: Math.round(change),
      hasData: currentMonthCount > 0 || lastMonthCount > 0
    };
  }, [transactions]);

  // Most frequent merchant
  const topMerchant = useMemo(() => {
    const merchantMap = new Map<string, { total: number; count: number }>();
    transactions.forEach(t => {
      const merchant = t.merchant_name || t.description || 'Unknown';
      const existing = merchantMap.get(merchant) || { total: 0, count: 0 };
      existing.total += Number(t.amount);
      existing.count += 1;
      merchantMap.set(merchant, existing);
    });

    const sorted = Array.from(merchantMap.entries())
      .sort((a, b) => b[1].count - a[1].count);

    if (sorted.length === 0) return null;

    const [name, data] = sorted[0];
    return {
      name,
      total: Math.round(data.total * 100) / 100,
      count: data.count
    };
  }, [transactions]);

  // Statement periods - Show ALL uploaded periods
  const statementPeriods = useMemo(() => {
    const periodMap = new Map<string, { year: number; month: number; count: number }>();

    transactions.forEach(t => {
      const key = `${t.statement_year}-${String(t.statement_month).padStart(2, '0')}`;
      const existing = periodMap.get(key) || { year: t.statement_year, month: t.statement_month, count: 0 };
      existing.count += 1;
      periodMap.set(key, existing);
    });

    return Array.from(periodMap.values())
      .sort((a, b) => {
        if (a.year !== b.year) return b.year - a.year;
        return b.month - a.month;
      });
      // No slice - show all periods!
  }, [transactions]);

  // Detect missing months from oldest uploaded to current month
  const missingPeriods = useMemo(() => {
    if (statementPeriods.length === 0) return [];

    // Get the oldest period
    const sorted = [...statementPeriods].sort((a, b) => {
      if (a.year !== b.year) return a.year - b.year;
      return a.month - b.month;
    });

    const oldest = sorted[0];

    // Get current year and month
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1; // getMonth() returns 0-11
    const currentDay = now.getDate();

    // Generate all months from oldest to current month
    const allMonths: { year: number; month: number }[] = [];
    let year = oldest.year;
    let month = oldest.month;

    while (
      year < currentYear ||
      (year === currentYear && month <= currentMonth)
    ) {
      allMonths.push({ year, month });

      month++;
      if (month > 12) {
        month = 1;
        year++;
      }
    }

    // Find missing months (exclude uploaded ones)
    const uploadedKeys = new Set(
      statementPeriods.map(p => `${p.year}-${String(p.month).padStart(2, '0')}`)
    );

    // Get the earliest statement day from cards (if any)
    const statementDay = cards.length > 0
      ? cards.map(c => c.statement_day ? parseInt(c.statement_day) : null)
              .filter((day): day is number => day !== null)
              .sort((a, b) => a - b)[0]
      : null;

    return allMonths
      .filter(m => !uploadedKeys.has(`${m.year}-${String(m.month).padStart(2, '0')}`))
      .map(m => {
        // Determine if the statement should exist yet
        let statementGenerated = true;
        let statementGenerationDate: Date | null = null;

        if (statementDay !== null && statementDay !== undefined) {
          // Calculate the statement generation date for this missing month
          // Statement for month X is generated on day Y of month X+1
          const nextMonth = m.month === 12 ? 1 : m.month + 1;
          const nextYear = m.month === 12 ? m.year + 1 : m.year;

          statementGenerationDate = new Date(nextYear, nextMonth - 1, statementDay);

          // Check if statement generation date has passed
          statementGenerated = now >= statementGenerationDate;
        }

        return {
          year: m.year,
          month: m.month,
          statementGenerated,
          statementGenerationDate,
          statementDay,
        };
      });
  }, [statementPeriods, cards]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Show error state if there was an error loading data
  if (error && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-foreground mb-2">Failed to Load Dashboard</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen fintech-bg">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content - offset by sidebar width (256px = w-64) */}
      <div className="flex-1 ml-64">
        {/* Header */}
        <header className="bg-card border-b border-border px-8 py-5">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-card-foreground mb-1">
                Welcome back, {user?.full_name?.split(' ')[0]}!
              </h1>
              <p className="text-muted-foreground">
                Here's what's happening with your finances today.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {/* Upload Statement Button - Teal Accent for Pop */}
              <button
                onClick={() => router.push('/upload')}
                className="flex items-center space-x-2 px-6 py-2.5 gradient-teal-accent text-white font-semibold rounded-xl btn-hover-accent shadow-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <span>Upload Statement</span>
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="px-8 py-5">
          {/* Payment Alerts */}
          <PaymentAlertBanner />

          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
            {/* Total Spending Card */}
            <div className="fintech-card card-accent-indigo p-5 animate-slide-in" style={{ animationDelay: "0.1s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <h3 className="card-title text-sm mb-1 text-muted-foreground">
                Total Spending
              </h3>
              <p className="text-3xl font-bold text-card-foreground mb-2">
                {formatCurrency(stats.totalSpending)}
              </p>
              <p className="text-xs text-muted-foreground">
                {stats.transactionCount === 0 ? 'No transactions yet' : `Across ${stats.transactionCount} transactions`}
              </p>
            </div>

            {/* Transactions Card */}
            <div className="fintech-card card-accent-teal p-5 animate-slide-in" style={{ animationDelay: "0.2s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                  <svg className="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                </div>
              </div>
              <h3 className="card-title text-sm mb-1 text-muted-foreground">
                Transactions
              </h3>
              <p className="text-3xl font-bold text-foreground mb-2">
                {stats.transactionCount}
              </p>
              <p className="text-xs text-muted-foreground">
                {stats.transactionCount === 0 ? 'Start adding transactions' : 'Total transactions tracked'}
              </p>
            </div>

            {/* Active Cards Card */}
            <div className="fintech-card card-accent-amber p-5 animate-slide-in" style={{ animationDelay: "0.3s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                  <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
                <div className="px-3 py-1 rounded-full bg-secondary/10 text-secondary text-xs font-semibold">
                  Active
                </div>
              </div>
              <h3 className="card-title text-sm mb-1 text-muted-foreground">
                Credit Cards
              </h3>
              <p className="text-3xl font-bold text-foreground mb-2">
                {stats.cardCount}
              </p>
              <p className="text-xs text-muted-foreground">
                {stats.cardCount === 0 ? 'Add your first card' : 'Cards in your wallet'}
              </p>
            </div>

            {/* AI Confidence Card */}
            <div className="fintech-card card-accent-emerald p-5 animate-slide-in" style={{ animationDelay: "0.4s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl gradient-indigo-purple flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                  Excellent
                </div>
              </div>
              <h3 className="card-title text-sm mb-1 text-muted-foreground">
                AI Confidence
              </h3>
              <p className="text-3xl font-bold text-foreground mb-2">
                {stats.avgConfidence}%
              </p>
              <p className="text-xs text-muted-foreground">
                Average categorization accuracy
              </p>
            </div>
          </div>

          {/* Main Content Grid - Recent Transactions + Top Categories */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
            {/* Recent Transactions */}
            <div className="fintech-card animate-slide-in" style={{ animationDelay: "0.7s" }}>
              <div className="px-5 py-4 border-b border-border flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-foreground">Recent Transactions</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">Your latest spending activity</p>
                </div>
                {transactions.length > 7 && (
                  <button
                    onClick={() => router.push('/transactions')}
                    className="text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                  >
                    View All
                  </button>
                )}
              </div>
              <div className="p-5">
                {recentTransactions.length > 0 ? (
                  <div className="space-y-3">
                    {recentTransactions.map((transaction, index) => (
                      <button
                        key={transaction.id}
                        onClick={() => router.push('/transactions')}
                        className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-muted/30 transition-all duration-200 border border-transparent hover:border-border group"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                            style={{ backgroundColor: `${CHART_COLORS[index % CHART_COLORS.length]}15` }}
                          >
                            {getCategoryIcon(transaction.category?.name || 'Uncategorized')}
                          </div>
                          <div className="text-left">
                            <div className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors truncate max-w-[180px]">
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
                            {formatCurrency(transaction.amount)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {transaction.category?.name || 'Other'}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="py-10 text-center text-muted-foreground text-sm">
                    <svg className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <p className="font-medium mb-1">No transactions yet</p>
                    <p className="text-xs">Upload a statement to get started</p>
                  </div>
                )}
              </div>
            </div>

            {/* Top Categories - Horizontal Bars */}
            <div className="fintech-card p-5 animate-slide-in" style={{ animationDelay: "0.8s" }}>
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-foreground mb-0.5">Top Categories</h3>
                  <p className="text-xs text-muted-foreground">Where your money goes</p>
                </div>
                {categoryData.length > 0 && (
                  <button
                    onClick={() => router.push('/analytics')}
                    className="text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                  >
                    View All
                  </button>
                )}
              </div>
              {categoryData.length > 0 ? (
                <div className="space-y-3">
                  {categoryData.map((category) => (
                    <button
                      key={category.name}
                      onClick={() => router.push('/analytics')}
                      className="w-full group hover:bg-muted/30 p-3 rounded-lg transition-all duration-200 border border-transparent hover:border-border"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
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
                            {formatCurrency(category.value)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {category.percentage}%
                          </div>
                        </div>
                      </div>
                      <div className="w-full h-2 bg-muted/50 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500 ease-out"
                          style={{
                            width: `${category.percentage}%`,
                            backgroundColor: category.color,
                          }}
                        />
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="py-10 flex items-center justify-center text-muted-foreground text-sm">
                  <svg className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="font-medium">No category data</p>
                </div>
              )}
            </div>
          </div>

          {/* Month Comparison Cards */}
          {monthComparison.hasData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
              {/* This Month */}
              <div className="fintech-card card-accent-indigo p-5 animate-slide-in" style={{ animationDelay: "0.9s" }}>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  {monthComparison.change !== 0 && (
                    <div className={`px-2 py-1 rounded-full text-xs font-bold ${
                      monthComparison.change > 0
                        ? 'bg-red-500/10 text-red-500'
                        : 'bg-emerald-500/10 text-emerald-500'
                    }`}>
                      {monthComparison.change > 0 ? '+' : ''}{monthComparison.change}%
                    </div>
                  )}
                </div>
                <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">This Month</h3>
                <p className="text-2xl font-bold text-foreground mb-1">
                  {formatCurrency(monthComparison.currentMonth.total)}
                </p>
                <p className="text-xs text-muted-foreground">
                  {monthComparison.currentMonth.count} transaction{monthComparison.currentMonth.count !== 1 ? 's' : ''}
                </p>
              </div>

              {/* Last Month */}
              <div className="fintech-card card-accent-teal p-5 animate-slide-in" style={{ animationDelay: "1.0s" }}>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-11 h-11 rounded-xl bg-accent/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Last Month</h3>
                <p className="text-2xl font-bold text-foreground mb-1">
                  {formatCurrency(monthComparison.lastMonth.total)}
                </p>
                <p className="text-xs text-muted-foreground">
                  {monthComparison.lastMonth.count} transaction{monthComparison.lastMonth.count !== 1 ? 's' : ''}
                </p>
              </div>

              {/* Top Merchant */}
              <div className="fintech-card card-accent-amber p-5 animate-slide-in" style={{ animationDelay: "1.1s" }}>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-11 h-11 rounded-xl gradient-indigo-purple flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                </div>
                <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Most Frequent</h3>
                <p className="text-lg font-bold text-foreground mb-1 truncate" title={topMerchant?.name}>
                  {topMerchant?.name || 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">
                  {topMerchant ? `${topMerchant.count} visit${topMerchant.count !== 1 ? 's' : ''} • ${formatCurrency(topMerchant.total)}` : 'No data'}
                </p>
              </div>
            </div>
          )}

          {/* Statement Periods and Budget Progress Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
            {/* Statement Periods - All Uploaded */}
            <div className="fintech-card animate-slide-in" style={{ animationDelay: "1.2s" }}>
              <div className="px-5 py-4 border-b border-border">
                <h3 className="text-base font-bold text-foreground">Uploaded Statements</h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {statementPeriods.length === 0
                    ? 'No statements yet'
                    : `${statementPeriods.length} ${statementPeriods.length === 1 ? 'month' : 'months'} of data`}
                </p>
              </div>
              <div className="p-5">
                {statementPeriods.length > 0 ? (
                  <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                    {statementPeriods.map((period, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 rounded-lg bg-muted/10 hover:bg-muted/20 transition-colors"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                            <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-foreground">
                              {new Date(period.year, period.month - 1, 1).toLocaleDateString('en-US', {
                                month: 'long',
                                year: 'numeric'
                              })}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {period.count} {period.count === 1 ? 'transaction' : 'transactions'}
                            </p>
                          </div>
                        </div>
                        <div className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-500 text-xs font-semibold">
                          ✓ Uploaded
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    <svg className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="font-medium mb-1">No statements uploaded yet</p>
                    <button
                      onClick={() => router.push('/upload')}
                      className="text-primary text-xs hover:underline mt-2"
                    >
                      Upload your first statement →
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Missing Periods - Prompt to Upload */}
            <div className="fintech-card animate-slide-in" style={{ animationDelay: "1.3s" }}>
              <div className="px-5 py-4 border-b border-border">
                <h3 className="text-base font-bold text-foreground">Missing Months</h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {missingPeriods.length === 0
                    ? 'Complete coverage!'
                    : `${missingPeriods.length} ${missingPeriods.length === 1 ? 'month' : 'months'} to upload`}
                </p>
              </div>
              <div className="p-5">
                {missingPeriods.length > 0 ? (
                  <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                    {missingPeriods.map((period, index) => {
                      // Determine styling based on whether statement is generated
                      const isPending = !period.statementGenerated && !!period.statementGenerationDate;
                      const bgColor = isPending ? 'bg-blue-500/5' : 'bg-amber-500/5';
                      const borderColor = isPending ? 'border-blue-500/20' : 'border-amber-500/20';
                      const hoverColor = isPending ? 'hover:bg-blue-500/10' : 'hover:bg-amber-500/10';
                      const iconBg = isPending ? 'bg-blue-500/10' : 'bg-amber-500/10';
                      const iconColor = isPending ? 'text-blue-500' : 'text-amber-500';
                      const textColor = isPending ? 'text-blue-600' : 'text-amber-600';
                      const buttonBg = isPending ? 'bg-blue-500 hover:bg-blue-600' : 'bg-amber-500 hover:bg-amber-600';

                      return (
                        <div
                          key={index}
                          className={`flex items-center justify-between p-3 rounded-lg ${bgColor} border ${borderColor} ${hoverColor} transition-colors`}
                        >
                          <div className="flex items-center space-x-3 flex-1">
                            <div className={`w-10 h-10 rounded-xl ${iconBg} flex items-center justify-center`}>
                              {isPending ? (
                                // Clock icon for pending statements
                                <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                              ) : (
                                // Warning icon for missing statements
                                <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                              )}
                            </div>
                            <div>
                              <p className="text-sm font-semibold text-foreground">
                                {new Date(period.year, period.month - 1, 1).toLocaleDateString('en-US', {
                                  month: 'long',
                                  year: 'numeric'
                                })}
                              </p>
                              <p className={`text-xs ${textColor}`}>
                                {period.statementGenerated ? (
                                  // Statement generation date has passed
                                  'Statement not uploaded'
                                ) : period.statementGenerationDate ? (
                                  // Statement hasn't been generated yet
                                  `Statement will be generated on ${period.statementGenerationDate.toLocaleDateString('en-US', {
                                    month: 'short',
                                    day: 'numeric'
                                  })}`
                                ) : (
                                  // No statement day configured
                                  'Statement not uploaded'
                                )}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => router.push('/upload')}
                            className={`px-3 py-1 rounded-full ${buttonBg} text-white text-xs font-semibold transition-colors flex-shrink-0`}
                            disabled={isPending}
                            title={isPending ? "Statement not yet generated by bank" : "Upload statement"}
                          >
                            {isPending ? 'Pending' : 'Upload'}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                ) : statementPeriods.length > 0 ? (
                  <div className="text-center py-8">
                    <svg className="w-12 h-12 mx-auto mb-3 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm font-semibold text-foreground mb-1">All caught up!</p>
                    <p className="text-xs text-muted-foreground">
                      {(() => {
                        const sorted = [...statementPeriods].sort((a, b) => {
                          if (a.year !== b.year) return a.year - b.year;
                          return a.month - b.month;
                        });
                        const oldest = sorted[0];
                        const now = new Date();
                        return `Complete coverage from ${new Date(oldest.year, oldest.month - 1, 1).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })} to ${now.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}`;
                      })()}
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    <svg className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="font-medium mb-1">Upload statements to track coverage</p>
                    <p className="text-xs">We'll help you identify any missing months</p>
                  </div>
                )}
              </div>
            </div>
          </div>

        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}
