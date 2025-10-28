'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser } from '@/lib/api/auth';
import { getCards } from '@/lib/api/cards';
import { getTransactions } from '@/lib/api/transactions';
import { getHeroInsight, Insight } from '@/lib/api/insights';
import { getStatementStatus } from '@/lib/api/statements';
import { User, CreditCard, Transaction } from '@/models';
import { DashboardStats, LineChartData, PieChartData } from '@/types';
import { extractErrorMessage, isAuthError } from '@/lib/utils/errorHandler';
import Sidebar from '@/components/layout/Sidebar';
import Footer from '@/components/layout/Footer';
import HeroInsightCard from '@/components/insights/HeroInsightCard';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Cardora V2 Refined Fintech Color Palette
const COLORS = [
  '#4B6EF5', // Modern Indigo - primary brand color
  '#00E0A1', // Teal Mint - accent for positive metrics
  '#F59E0B', // Amber - warning/highlight
  '#10B981', // Emerald - success
  '#8B5CF6', // Purple - secondary
  '#60A5FA', // Sky Blue - supplementary
  '#FB923C', // Coral - warm accent
];

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  // Insights state
  const [heroInsight, setHeroInsight] = useState<Insight | null>(null);
  const [insightsStatus, setInsightsStatus] = useState<'loading' | 'processing' | 'completed' | 'failed' | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      // Check if user is authenticated before making API calls
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.log('No auth token found, redirecting to login');
          router.push('/login');
          return;
        }
      }

      try {
        // Fetch user data
        const userData = await getCurrentUser();
        setUser(userData);

        // Fetch cards and transactions separately to handle errors better
        let cardsData: CreditCard[] = [];
        let transactionsData: Transaction[] = [];

        try {
          cardsData = await getCards();
          console.log('Cards data:', cardsData);
          // Ensure it's an array
          if (!Array.isArray(cardsData)) {
            console.warn('Cards data is not an array:', cardsData);
            cardsData = [];
          }
        } catch (cardError) {
          console.warn('Failed to fetch cards:', extractErrorMessage(cardError));
          cardsData = [];
        }
        setCards(cardsData);

        try {
          transactionsData = await getTransactions({ limit: 10000 });
          console.log('Transactions data:', transactionsData);
          // Ensure it's an array
          if (!Array.isArray(transactionsData)) {
            console.warn('Transactions data is not an array:', transactionsData);
            transactionsData = [];
          }
        } catch (transactionError) {
          console.warn('Failed to fetch transactions:', extractErrorMessage(transactionError));
          transactionsData = [];
        }
        setTransactions(transactionsData);
      } catch (error) {
        const errorMessage = extractErrorMessage(error);
        console.error('Dashboard error:', errorMessage);
        // Don't handle auth errors here - let the axios interceptor handle 401 redirects
        // Just log other errors and continue with empty data
        if (!isAuthError(error)) {
          console.error('Failed to load dashboard data:', errorMessage);
          setError(errorMessage);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  // Fetch insights on mount
  useEffect(() => {
    const fetchInsights = async () => {
      try {
        // Fetch hero insight
        const hero = await getHeroInsight().catch(() => null);
        setHeroInsight(hero);

        // If we have a hero insight, mark as completed
        if (hero) {
          setInsightsStatus('completed');
        }
      } catch (error) {
        console.error('Failed to fetch insights:', error);
      }
    };

    // Only fetch insights if user is loaded
    if (user) {
      fetchInsights();
    }
  }, [user]);

  // Poll statement status for insights generation
  useEffect(() => {
    const pollStatementStatus = async () => {
      // Get the latest statement ID from localStorage (set during upload)
      const latestStatementId = localStorage.getItem('latest_statement_id');
      if (!latestStatementId) return;

      try {
        const status = await getStatementStatus(latestStatementId);

        // Update insights status
        if (status.insights_status === 'processing') {
          setInsightsStatus('processing');
        } else if (status.insights_status === 'completed') {
          setInsightsStatus('completed');

          // Fetch the new hero insight
          const hero = await getHeroInsight().catch(() => null);
          setHeroInsight(hero);

          // Clear the statement ID from localStorage
          localStorage.removeItem('latest_statement_id');
        } else if (status.insights_status === 'failed') {
          setInsightsStatus('failed');
          localStorage.removeItem('latest_statement_id');
        }
      } catch (error) {
        console.error('Failed to poll statement status:', error);
      }
    };

    // Start polling if we have a pending statement
    const latestStatementId = localStorage.getItem('latest_statement_id');
    if (latestStatementId && user) {
      setInsightsStatus('processing');

      // Poll every 3 seconds
      const pollInterval = setInterval(pollStatementStatus, 3000);

      // Initial poll
      pollStatementStatus();

      // Cleanup interval on unmount
      return () => clearInterval(pollInterval);
    }
  }, [user]);

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

  // Process category data
  const categoryData = useMemo(() => {
    const categoryMap = new Map<string, number>();
    transactions.forEach((t) => {
      if (t.category?.name) {
        categoryMap.set(
          t.category.name,
          (categoryMap.get(t.category.name) || 0) + Number(t.amount)
        );
      }
    });

    return Array.from(categoryMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5) // Top 5 categories
      .map(([name, value]) => ({
        name,
        value: Math.round(value * 100) / 100,
      }));
  }, [transactions]);

  // Smart insights
  const insights = useMemo(() => {
    const insights: { type: 'info' | 'warning' | 'success'; message: string }[] = [];

    if (transactions.length === 0) {
      insights.push({
        type: 'info',
        message: 'Upload your first statement to start tracking your spending patterns!'
      });
      return insights;
    }

    // Calculate this month vs last month
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth() + 1;
    const currentYear = currentDate.getFullYear();
    const lastMonth = currentMonth === 1 ? 12 : currentMonth - 1;
    const lastMonthYear = currentMonth === 1 ? currentYear - 1 : currentYear;

    const thisMonthTotal = transactions
      .filter(t => t.statement_month === currentMonth && t.statement_year === currentYear)
      .reduce((sum, t) => sum + Number(t.amount), 0);

    const lastMonthTotal = transactions
      .filter(t => t.statement_month === lastMonth && t.statement_year === lastMonthYear)
      .reduce((sum, t) => sum + Number(t.amount), 0);

    if (thisMonthTotal > 0 && lastMonthTotal > 0) {
      const percentChange = ((thisMonthTotal - lastMonthTotal) / lastMonthTotal) * 100;
      if (Math.abs(percentChange) > 10) {
        insights.push({
          type: percentChange > 0 ? 'warning' : 'success',
          message: `You've spent ${Math.abs(percentChange).toFixed(0)}% ${percentChange > 0 ? 'more' : 'less'} this month compared to last month ($${thisMonthTotal.toFixed(2)} vs $${lastMonthTotal.toFixed(2)})`
        });
      }
    }

    // Top category insight
    if (categoryData.length > 0) {
      const topCategory = categoryData[0];
      const totalSpending = categoryData.reduce((sum, cat) => sum + cat.value, 0);
      const percentage = (topCategory.value / totalSpending) * 100;

      if (percentage > 30) {
        insights.push({
          type: 'info',
          message: `${topCategory.name} is your highest spending category at ${percentage.toFixed(0)}% of your total ($${topCategory.value.toFixed(2)})`
        });
      }
    }

    // High confidence insight
    if (stats.avgConfidence >= 90) {
      insights.push({
        type: 'success',
        message: `AI categorization is working excellently at ${stats.avgConfidence}% accuracy across ${stats.transactionCount} transactions`
      });
    }

    return insights.slice(0, 3); // Limit to 3 insights
  }, [transactions, categoryData, stats]);

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

    return allMonths.filter(
      m => !uploadedKeys.has(`${m.year}-${String(m.month).padStart(2, '0')}`)
    );
  }, [statementPeriods]);

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

              {/* User Profile */}
              <div className="flex items-center space-x-3 border-l border-border pl-4">
                <div className="text-right">
                  <p className="text-sm font-semibold text-foreground">
                    {user?.full_name}
                  </p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
                  {user?.full_name?.charAt(0).toUpperCase()}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="px-8 py-5">
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
                ${stats.totalSpending.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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

          {/* Insights Processing Status */}
          {insightsStatus === 'processing' && (
            <div className="mb-6 animate-slide-in" style={{ animationDelay: '0.6s' }}>
              <div className="fintech-card p-4 flex items-center space-x-3">
                <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin flex-shrink-0"></div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-foreground">Generating AI Insights...</p>
                  <p className="text-xs text-muted-foreground">Analyzing your spending patterns with Gemini AI</p>
                </div>
              </div>
            </div>
          )}

          {/* Hero Insight Card */}
          {heroInsight && (
            <div className="mb-6 animate-slide-in" style={{ animationDelay: '0.7s' }}>
              <HeroInsightCard
                insight={heroInsight}
                onDismiss={async () => {
                  // Refetch hero insight after dismissing
                  const hero = await getHeroInsight().catch(() => null);
                  setHeroInsight(hero);
                }}
                onComplete={async () => {
                  // Refetch hero insight after completing
                  const hero = await getHeroInsight().catch(() => null);
                  setHeroInsight(hero);
                }}
              />
            </div>
          )}

          {/* Old Smart Insights Section - Fallback */}
          {!heroInsight && insights.length > 0 && (
            <div className="mb-6 space-y-3">
              {insights.map((insight, index) => (
                <div
                  key={index}
                  className={`fintech-card p-4 flex items-start space-x-3 animate-slide-in ${
                    insight.type === 'warning' ? 'card-accent-amber' :
                    insight.type === 'success' ? 'card-accent-emerald' :
                    'card-accent-indigo'
                  }`}
                  style={{ animationDelay: `${0.5 + index * 0.1}s` }}
                >
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    insight.type === 'warning' ? 'bg-amber-500/10' :
                    insight.type === 'success' ? 'bg-emerald-500/10' :
                    'bg-primary/10'
                  }`}>
                    {insight.type === 'warning' && (
                      <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    )}
                    {insight.type === 'success' && (
                      <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                    {insight.type === 'info' && (
                      <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-foreground font-medium leading-relaxed">
                      {insight.message}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
            {/* Spending Trend Chart */}
            <div className="fintech-card p-5 animate-slide-in" style={{ animationDelay: "0.8s" }}>
              <div className="mb-6">
                <h3 className="card-title text-lg mb-1">
                  Spending Trend
                </h3>
                <p className="text-sm text-muted-foreground">
                  Your spending over the last 6 months
                </p>
              </div>
              {spendingTrendData.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={spendingTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                    <XAxis
                      dataKey="month"
                      tick={{ fill: '#64748B', fontSize: 12 }}
                      stroke="#E2E8F0"
                    />
                    <YAxis
                      tick={{ fill: '#64748B', fontSize: 12 }}
                      stroke="#E2E8F0"
                      tickFormatter={(value: number) => `$${value.toLocaleString()}`}
                    />
                    <Tooltip
                      formatter={(value: number) => [`$${value.toFixed(2)}`, 'Spending']}
                      contentStyle={{
                        backgroundColor: '#FFFFFF',
                        border: '1px solid #E2E8F0',
                        borderRadius: '12px',
                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                    <Line
                      type="monotone"
                      dataKey="spending"
                      stroke="#4B6EF5"
                      strokeWidth={3}
                      dot={{ fill: '#4B6EF5', r: 5 }}
                      activeDot={{ r: 7, fill: '#00E0A1' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[280px] flex items-center justify-center text-muted-foreground">
                  No spending data available
                </div>
              )}
            </div>

            {/* Category Breakdown Chart */}
            <div className="fintech-card p-5 animate-slide-in" style={{ animationDelay: "0.9s" }}>
              <div className="mb-6">
                <h3 className="card-title text-lg mb-1">
                  Category Breakdown
                </h3>
                <p className="text-sm text-muted-foreground">
                  Top 5 spending categories
                </p>
              </div>
              {categoryData.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(props: any) =>
                        `${props.name} (${(props.percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={90}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: number) => [`$${value.toFixed(2)}`, 'Amount']}
                      contentStyle={{
                        backgroundColor: '#FFFFFF',
                        border: '1px solid #E2E8F0',
                        borderRadius: '12px',
                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      wrapperStyle={{ paddingTop: '20px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[280px] flex items-center justify-center text-muted-foreground">
                  No category data available
                </div>
              )}
            </div>
          </div>

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
                    {missingPeriods.map((period, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 rounded-lg bg-amber-500/5 border border-amber-500/20 hover:bg-amber-500/10 transition-colors"
                      >
                        <div className="flex items-center space-x-3 flex-1">
                          <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                            <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-foreground">
                              {new Date(period.year, period.month - 1, 1).toLocaleDateString('en-US', {
                                month: 'long',
                                year: 'numeric'
                              })}
                            </p>
                            <p className="text-xs text-amber-600">
                              Statement not uploaded
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => router.push('/upload')}
                          className="px-3 py-1 rounded-full bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold transition-colors flex-shrink-0"
                        >
                          Upload
                        </button>
                      </div>
                    ))}
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

          {/* Budget Progress Section - Moved Down */}
          <div className="grid grid-cols-1 mb-6">
            {/* Budget Progress - Coming Soon */}
            <div className="fintech-card animate-slide-in relative overflow-hidden" style={{ animationDelay: "1.4s" }}>
              <div className="px-5 py-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-foreground">Budget Tracking</h3>
                    <p className="text-xs text-muted-foreground mt-0.5">Monitor your spending limits</p>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-gradient-to-r from-primary to-accent text-white text-xs font-bold">
                    Coming Soon
                  </span>
                </div>
              </div>
              <div className="p-5 relative">
                <div className="opacity-50 space-y-4">
                  {/* Mock budget items */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">Dining</span>
                      <span className="text-sm text-muted-foreground">$450 / $600</span>
                    </div>
                    <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-primary to-accent rounded-full" style={{ width: '75%' }}></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">Shopping</span>
                      <span className="text-sm text-muted-foreground">$320 / $400</span>
                    </div>
                    <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-accent to-primary rounded-full" style={{ width: '80%' }}></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">Transport</span>
                      <span className="text-sm text-muted-foreground">$150 / $300</span>
                    </div>
                    <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full" style={{ width: '50%' }}></div>
                    </div>
                  </div>
                </div>
                {/* Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-card via-card/90 to-transparent flex items-center justify-center">
                  <div className="text-center">
                    <svg className="w-16 h-16 mx-auto mb-3 text-primary opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm font-semibold text-foreground mb-1">Budget Tracking</p>
                    <p className="text-xs text-muted-foreground">Coming in the next update</p>
                  </div>
                </div>
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
