'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getCards, updateCard, deleteCard } from '@/features/cards';
import { getTransactions } from '@/features/transactions';
import { CreditCard } from '@/features/cards/types';
import { Transaction } from '@/features/transactions/types';
import { extractErrorMessage } from '@/shared/lib/utils/errorHandler';
import { formatCardType, formatBankName, formatCardDisplayName } from '@/shared/lib/utils/cardFormatter';
import { formatCurrency } from '@/shared/lib/utils/formatCurrency';
import Sidebar from '@/shared/components/layout/Sidebar';
import Footer from '@/shared/components/layout/Footer';
import { SearchableSelect } from '@/shared/components/ui/SearchableSelect';

// Card brand colors
const CARD_COLORS: { [key: string]: { bg: string; border: string; accent: string } } = {
  'DBS': { bg: 'bg-gradient-to-br from-red-500 to-red-600', border: 'border-red-300', accent: 'text-red-600' },
  'OCBC': { bg: 'bg-gradient-to-br from-red-600 to-red-700', border: 'border-red-400', accent: 'text-red-700' },
  'UOB': { bg: 'bg-gradient-to-br from-blue-600 to-blue-700', border: 'border-blue-300', accent: 'text-blue-600' },
  'Citibank': { bg: 'bg-gradient-to-br from-blue-500 to-blue-600', border: 'border-blue-300', accent: 'text-blue-600' },
  'HSBC': { bg: 'bg-gradient-to-br from-red-700 to-red-800', border: 'border-red-400', accent: 'text-red-700' },
  'Standard Chartered': { bg: 'bg-gradient-to-br from-green-600 to-green-700', border: 'border-green-300', accent: 'text-green-600' },
  'Maybank': { bg: 'bg-gradient-to-br from-yellow-500 to-yellow-600', border: 'border-yellow-300', accent: 'text-yellow-600' },
  'Default': { bg: 'bg-gradient-to-br from-indigo-500 to-indigo-600', border: 'border-indigo-300', accent: 'text-indigo-600' },
};

interface CardWithStats extends CreditCard {
  totalSpent: number;
  transactionCount: number;
  thisMonthSpent: number;
  lastMonthSpent: number;
  mostFrequentCategory: string | null;
  avgTransactionAmount: number;
}

export default function CardsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [cards, setCards] = useState<CardWithStats[]>([]);
  const [filteredCards, setFilteredCards] = useState<CardWithStats[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  // Filters
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');
  const [filterBank, setFilterBank] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'spending' | 'date' | 'name'>('spending');

  // Modals
  const [editingCard, setEditingCard] = useState<CardWithStats | null>(null);
  const [deletingCard, setDeletingCard] = useState<CardWithStats | null>(null);
  const [viewingTransactions, setViewingTransactions] = useState<CardWithStats | null>(null);

  // Edit form state
  const [editForm, setEditForm] = useState({
    card_name: '',
    card_type: '',
    credit_limit: '',
    is_active: true,
  });

  useEffect(() => {
    fetchData();
  }, [router]);

  useEffect(() => {
    applyFiltersAndSort();
  }, [cards, filterStatus, filterBank, sortBy]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch cards
      const cardsData = await getCards();
      const safeCards = Array.isArray(cardsData) ? cardsData : [];

      // Fetch all transactions with pagination (API limit is 100 per request)
      let allTransactions: Transaction[] = [];
      let page = 1;
      let hasMore = true;

      while (hasMore) {
        try {
          const transactionsData = await getTransactions({ limit: 100, page });
          const pageTransactions = Array.isArray(transactionsData) ? transactionsData : [];

          if (pageTransactions.length === 0) {
            hasMore = false;
          } else {
            allTransactions = [...allTransactions, ...pageTransactions];
            page++;

            // Stop if we got less than 100 (last page)
            if (pageTransactions.length < 100) {
              hasMore = false;
            }
          }
        } catch {
          hasMore = false;
        }
      }

      setTransactions(allTransactions);

      // Calculate stats for each card
      const now = new Date();
      const firstDayThisMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      const firstDayLastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const lastDayLastMonth = new Date(now.getFullYear(), now.getMonth(), 0);

      const cardsWithStats: CardWithStats[] = safeCards.map(card => {
        const cardTransactions = allTransactions.filter(t => t.card_id === card.id);

        const totalSpent = cardTransactions.reduce((sum, t) => sum + Number(t.amount), 0);
        const transactionCount = cardTransactions.length;

        const thisMonthTransactions = cardTransactions.filter(t =>
          new Date(t.transaction_date) >= firstDayThisMonth
        );
        const thisMonthSpent = thisMonthTransactions.reduce((sum, t) => sum + Number(t.amount), 0);

        const lastMonthTransactions = cardTransactions.filter(t => {
          const date = new Date(t.transaction_date);
          return date >= firstDayLastMonth && date <= lastDayLastMonth;
        });
        const lastMonthSpent = lastMonthTransactions.reduce((sum, t) => sum + Number(t.amount), 0);

        // Find most frequent category
        const categoryCount = new Map<string, number>();
        cardTransactions.forEach(t => {
          if (t.category?.name) {
            categoryCount.set(t.category.name, (categoryCount.get(t.category.name) || 0) + 1);
          }
        });
        let mostFrequentCategory: string | null = null;
        let maxCount = 0;
        categoryCount.forEach((count, category) => {
          if (count > maxCount) {
            maxCount = count;
            mostFrequentCategory = category;
          }
        });

        const avgTransactionAmount = transactionCount > 0 ? totalSpent / transactionCount : 0;

        return {
          ...card,
          totalSpent,
          transactionCount,
          thisMonthSpent,
          lastMonthSpent,
          mostFrequentCategory,
          avgTransactionAmount,
        };
      });

      setCards(cardsWithStats);
    } catch {
      // Auth errors (401) are handled by the Axios interceptor.
    } finally {
      setLoading(false);
    }
  };

  const applyFiltersAndSort = () => {
    let filtered = [...cards];

    // Filter by status
    if (filterStatus === 'active') {
      filtered = filtered.filter(c => c.is_active);
    } else if (filterStatus === 'inactive') {
      filtered = filtered.filter(c => !c.is_active);
    }

    // Filter by bank
    if (filterBank !== 'all') {
      filtered = filtered.filter(c => c.bank_name === filterBank);
    }

    // Sort
    if (sortBy === 'spending') {
      filtered.sort((a, b) => b.totalSpent - a.totalSpent);
    } else if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    } else if (sortBy === 'name') {
      filtered.sort((a, b) => (a.card_name || a.bank_name).localeCompare(b.card_name || b.bank_name));
    }

    setFilteredCards(filtered);
  };

  const getCardColor = (bankName: string) => {
    const bank = Object.keys(CARD_COLORS).find(key => bankName.includes(key));
    return bank ? CARD_COLORS[bank] : CARD_COLORS.Default;
  };

  const handleEditClick = (card: CardWithStats) => {
    setEditingCard(card);
    setEditForm({
      card_name: card.card_name || '',
      card_type: card.card_type || '',
      credit_limit: card.credit_limit?.toString() || '',
      is_active: card.is_active,
    });
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingCard) return;

    try {
      await updateCard(editingCard.id, {
        card_name: editForm.card_name || undefined,
        card_type: editForm.card_type || undefined,
        credit_limit: editForm.credit_limit ? Number(editForm.credit_limit) : undefined,
        is_active: editForm.is_active,
      });

      setEditingCard(null);
      fetchData();
    } catch (error) {
      alert('Failed to update card: ' + extractErrorMessage(error));
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingCard) return;

    try {
      await deleteCard(deletingCard.id);
      setDeletingCard(null);
      fetchData();
    } catch (error) {
      alert('Failed to delete card: ' + extractErrorMessage(error));
    }
  };

  const handleToggleActive = async (card: CardWithStats) => {
    try {
      await updateCard(card.id, { is_active: !card.is_active });
      fetchData();
    } catch (error) {
      alert('Failed to toggle card status: ' + extractErrorMessage(error));
    }
  };

  // Get unique banks for filter
  const uniqueBanks = Array.from(new Set(cards.map(c => c.bank_name))).sort();

  // Calculate summary stats
  const activeCards = cards.filter(c => c.is_active);
  const totalCreditLimit = activeCards.reduce((sum, c) => sum + (Number(c.credit_limit) || 0), 0);
  const totalUtilization = activeCards.reduce((sum, c) => sum + c.thisMonthSpent, 0);
  const utilizationPercent = totalCreditLimit > 0 ? (totalUtilization / totalCreditLimit) * 100 : 0;
  const highestSpendingCard = cards.length > 0 ? cards.reduce((max, c) => c.thisMonthSpent > max.thisMonthSpent ? c : max, cards[0]) : null;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading your cards...</p>
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
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-1">My Cards</h1>
            <p className="text-muted-foreground">
              Manage your credit cards and track spending
            </p>
          </div>
        </header>

        <main className="px-8 py-5">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
            <div className="fintech-card card-accent-indigo p-5 animate-slide-in" style={{ animationDelay: "0.1s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
              </div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-1">Active Cards</h3>
              <p className="text-3xl font-bold text-foreground">{activeCards.length}</p>
              <p className="text-xs text-muted-foreground mt-2">
                {cards.length - activeCards.length} inactive
              </p>
            </div>

            <div className="fintech-card card-accent-teal p-5 animate-slide-in" style={{ animationDelay: "0.2s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                  <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-1">Total Credit Limit</h3>
              <p className="text-3xl font-bold text-foreground">
                {formatCurrency(totalCreditLimit)}
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                Across all active cards
              </p>
            </div>

            <div className="fintech-card card-accent-amber p-5 animate-slide-in" style={{ animationDelay: "0.3s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                  <svg className="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-1">Total Utilization</h3>
              <p className="text-3xl font-bold text-foreground">{utilizationPercent.toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground mt-2">
                {formatCurrency(totalUtilization)} used
              </p>
            </div>

            <div className="fintech-card card-accent-emerald p-5 animate-slide-in" style={{ animationDelay: "0.4s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl gradient-indigo-purple flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
              </div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-1">Top Spending Card</h3>
              <p className="text-xl font-bold text-foreground truncate">
                {highestSpendingCard ? formatCardDisplayName(highestSpendingCard.card_name, highestSpendingCard.bank_name, highestSpendingCard.card_type, highestSpendingCard.last_four_digits) : 'N/A'}
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                {formatCurrency(highestSpendingCard?.thisMonthSpent ?? 0)} this month
              </p>
            </div>
          </div>

          {/* Filters and Sort */}
          <div className="fintech-card p-5 mb-5 animate-slide-in" style={{ animationDelay: "0.5s" }}>
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-semibold text-foreground mb-2">Status</label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All Cards' },
                    { value: 'active', label: 'Active Only' },
                    { value: 'inactive', label: 'Inactive Only' }
                  ]}
                  value={filterStatus}
                  onChange={(value) => setFilterStatus(value as any)}
                  placeholder="Select status..."
                  searchPlaceholder="Search status..."
                  emptyMessage="No status found."
                />
              </div>

              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-semibold text-foreground mb-2">Bank</label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All Banks' },
                    ...uniqueBanks.map(bank => ({ value: bank, label: bank }))
                  ]}
                  value={filterBank}
                  onChange={(value) => setFilterBank(value)}
                  placeholder="Select bank..."
                  searchPlaceholder="Search banks..."
                  emptyMessage="No bank found."
                />
              </div>

              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-semibold text-foreground mb-2">Sort By</label>
                <SearchableSelect
                  options={[
                    { value: 'spending', label: 'Highest Spending' },
                    { value: 'date', label: 'Newest First' },
                    { value: 'name', label: 'Card Name' }
                  ]}
                  value={sortBy}
                  onChange={(value) => setSortBy(value as any)}
                  placeholder="Sort by..."
                  searchPlaceholder="Search sort options..."
                  emptyMessage="No sort option found."
                />
              </div>
            </div>
          </div>

          {/* Cards Grid */}
          {filteredCards.length === 0 ? (
            <div className="fintech-card p-12 text-center animate-slide-in" style={{ animationDelay: "0.6s" }}>
              <div className="w-20 h-20 rounded-full bg-muted/30 flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">No Cards Found</h3>
              <p className="text-muted-foreground mb-6">
                {cards.length === 0
                  ? "Cards are automatically created when you upload credit card statements."
                  : "No cards match your current filters."}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredCards.map((card, index) => {
                const colors = getCardColor(card.bank_name);
                const creditLimitUtilization = card.credit_limit ? (card.thisMonthSpent / Number(card.credit_limit)) * 100 : 0;
                const monthChange = card.lastMonthSpent > 0
                  ? ((card.thisMonthSpent - card.lastMonthSpent) / card.lastMonthSpent) * 100
                  : 0;

                return (
                  <div
                    key={card.id}
                    className="fintech-card overflow-hidden animate-slide-in"
                    style={{ animationDelay: `${(index * 0.1) + 0.6}s` }}
                  >
                    {/* Card Visual */}
                    <div className={`${colors.bg} p-6 text-white relative h-48`}>
                      {!card.is_active && (
                        <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-black/30 backdrop-blur-sm text-xs font-semibold">
                          Inactive
                        </div>
                      )}
                      <div className="flex flex-col h-full justify-between">
                        <div>
                          <p className="text-xs opacity-80 mb-1">{formatCardType(card.card_type)}</p>
                          <p className="text-lg font-bold">{formatBankName(card.bank_name)}</p>
                        </div>
                        <div>
                          <p className="text-xs opacity-80 mb-1">Card Number</p>
                          <p className="text-2xl font-bold tracking-wider">
                            •••• •••• •••• {card.last_four_digits}
                          </p>
                        </div>
                      </div>
                      <div className="absolute bottom-4 right-6 opacity-20">
                        <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/>
                        </svg>
                      </div>
                    </div>

                    {/* Card Info */}
                    <div className="p-6">
                      <div className="mb-4">
                        <h3 className="text-lg font-bold text-foreground mb-1">
                          {formatCardDisplayName(card.card_name, card.bank_name, card.card_type, card.last_four_digits)}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          Added {new Date(card.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                        </p>
                      </div>

                      {/* Stats Grid */}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Total Spent</p>
                          <p className="text-lg font-bold text-foreground">
                            {formatCurrency(card.totalSpent)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Transactions</p>
                          <p className="text-lg font-bold text-foreground">{card.transactionCount}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">This Month</p>
                          <p className="text-lg font-bold text-foreground">
                            {formatCurrency(card.thisMonthSpent)}
                          </p>
                          {monthChange !== 0 && (
                            <p className={`text-xs ${monthChange > 0 ? 'text-red-600' : 'text-green-600'}`}>
                              {monthChange > 0 ? '+' : ''}{monthChange.toFixed(1)}% vs last month
                            </p>
                          )}
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Avg Transaction</p>
                          <p className="text-lg font-bold text-foreground">
                            {formatCurrency(card.avgTransactionAmount)}
                          </p>
                        </div>
                      </div>

                      {/* Credit Limit */}
                      {card.credit_limit && (
                        <div className="mb-4">
                          <div className="flex justify-between items-center mb-2">
                            <p className="text-xs text-muted-foreground">Credit Utilization</p>
                            <p className="text-sm font-semibold text-foreground">{creditLimitUtilization.toFixed(1)}%</p>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${
                                creditLimitUtilization > 80 ? 'bg-red-500' :
                                creditLimitUtilization > 50 ? 'bg-yellow-500' :
                                'bg-green-500'
                              }`}
                              style={{ width: `${Math.min(creditLimitUtilization, 100)}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            {formatCurrency(card.thisMonthSpent)} of {formatCurrency(Number(card.credit_limit))} limit
                          </p>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="flex gap-2 pt-4 border-t border-border">
                        <button
                          onClick={() => router.push(`/transactions?cardId=${card.id}`)}
                          className="flex-1 px-4 py-2 text-sm font-medium text-primary bg-primary/10 rounded-lg hover:bg-primary/20 transition-colors"
                        >
                          View Transactions
                        </button>
                        <button
                          onClick={() => handleEditClick(card)}
                          className="px-4 py-2 text-sm font-medium text-secondary bg-secondary/10 rounded-lg hover:bg-secondary/20 transition-colors"
                          title="Edit Card"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleToggleActive(card)}
                          className="px-4 py-2 text-sm font-medium text-accent bg-accent/10 rounded-lg hover:bg-accent/20 transition-colors"
                          title={card.is_active ? "Deactivate" : "Activate"}
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {card.is_active ? (
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                            ) : (
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            )}
                          </svg>
                        </button>
                        <button
                          onClick={() => setDeletingCard(card)}
                          className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                          title="Delete Card"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </main>

        <Footer />
      </div>

      {/* Edit Modal */}
      {editingCard && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-md w-full p-6 animate-scale-in">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-foreground">Edit Card</h2>
              <button
                onClick={() => setEditingCard(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-foreground mb-2">
                  Card Name / Nickname
                </label>
                <input
                  type="text"
                  value={editForm.card_name}
                  onChange={(e) => setEditForm({ ...editForm, card_name: e.target.value })}
                  placeholder="e.g., DBS Altitude Visa"
                  className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-foreground mb-2">
                  Card Type
                </label>
                <input
                  type="text"
                  value={editForm.card_type}
                  onChange={(e) => setEditForm({ ...editForm, card_type: e.target.value })}
                  placeholder="e.g., Visa, Mastercard"
                  className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-foreground mb-2">
                  Credit Limit ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={editForm.credit_limit}
                  onChange={(e) => setEditForm({ ...editForm, credit_limit: e.target.value })}
                  placeholder="e.g., 10000.00"
                  className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={editForm.is_active}
                  onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                  className="w-5 h-5 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                />
                <label htmlFor="is_active" className="ml-3 text-sm font-semibold text-foreground">
                  Card is Active
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setEditingCard(null)}
                  className="flex-1 px-4 py-2 text-sm font-medium text-muted-foreground bg-muted rounded-lg hover:bg-muted/80 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingCard && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-md w-full p-6 animate-scale-in">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-foreground text-center mb-2">Delete Card?</h2>
            <p className="text-muted-foreground text-center mb-6">
              This will permanently delete <strong>{formatCardDisplayName(deletingCard.card_name, deletingCard.bank_name, deletingCard.card_type, deletingCard.last_four_digits)}</strong> and all associated statements and transactions. This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeletingCard(null)}
                className="flex-1 px-4 py-2 text-sm font-medium text-foreground bg-muted rounded-lg hover:bg-muted/80 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
              >
                Delete Card
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Transactions Modal */}
      {viewingTransactions && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden animate-scale-in flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-border">
              <div>
                <h2 className="text-2xl font-bold text-foreground">
                  {formatCardDisplayName(viewingTransactions.card_name, viewingTransactions.bank_name, viewingTransactions.card_type, viewingTransactions.last_four_digits)}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {viewingTransactions.transactionCount} transactions
                </p>
              </div>
              <button
                onClick={() => setViewingTransactions(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-auto p-6">
              {transactions.filter(t => t.card_id === viewingTransactions.id).length > 0 ? (
                <div className="space-y-3">
                  {transactions
                    .filter(t => t.card_id === viewingTransactions.id)
                    .sort((a, b) => new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime())
                    .map(transaction => (
                      <div key={transaction.id} className="flex items-center justify-between p-4 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors">
                        <div className="flex-1">
                          <p className="font-semibold text-foreground">{transaction.description}</p>
                          {transaction.merchant_name && (
                            <p className="text-sm text-muted-foreground">{transaction.merchant_name}</p>
                          )}
                          <div className="flex items-center gap-2 mt-1">
                            <p className="text-xs text-muted-foreground">
                              {new Date(transaction.transaction_date).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                              })}
                            </p>
                            {transaction.category && (
                              <>
                                <span className="text-xs text-muted-foreground">•</span>
                                <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
                                  {transaction.category.name}
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                        <p className="text-lg font-bold text-foreground ml-4">
                          {formatCurrency(transaction.amount)}
                        </p>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No transactions found for this card
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
