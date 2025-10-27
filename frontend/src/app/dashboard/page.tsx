'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser } from '@/lib/api/auth';
import { getCards } from '@/lib/api/cards';
import { getTransactions } from '@/lib/api/transactions';
import { User, CreditCard, Transaction } from '@/models';
import { DashboardStats, LineChartData, PieChartData } from '@/types';
import { extractErrorMessage, isAuthError } from '@/utils/errorHandler';
import Sidebar from '@/components/Sidebar';
import Footer from '@/components/Footer';
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
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    const fetchData = async () => {
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
        console.error('Dashboard error:', extractErrorMessage(error));
        if (isAuthError(error)) {
          console.log('Authentication failed (401), clearing token and redirecting to login');
          localStorage.removeItem('access_token');
          router.push('/login');
        } else {
          console.error('Failed to load dashboard data:', extractErrorMessage(error));
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

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
            {/* Spending Trend Chart */}
            <div className="fintech-card p-5 animate-slide-in" style={{ animationDelay: "0.5s" }}>
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
            <div className="fintech-card p-5 animate-slide-in" style={{ animationDelay: "0.6s" }}>
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
                      label={(props: { name: string; percent: number }) =>
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

        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}
