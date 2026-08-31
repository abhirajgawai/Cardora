'use client';

import { useEffect, useState, useMemo, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getCurrentUser } from '@/features/auth';
import { getTransactions } from '@/features/transactions';
import { getCards } from '@/features/cards';
import { getStatements } from '@/features/statements';
import { User } from '@/features/auth/types';
import { Transaction } from '@/features/transactions/types';
import { CreditCard } from '@/features/cards/types';
import { formatCardDisplayName } from '@/shared/lib/utils/cardFormatter';
import { formatCurrency } from '@/shared/lib/utils/formatCurrency';
import Sidebar from '@/shared/components/layout/Sidebar';
import MobileTopBar from '@/shared/components/layout/MobileTopBar';
import Footer from '@/shared/components/layout/Footer';
import { SearchableSelect } from '@/shared/components/ui/SearchableSelect';
import MonthYearPicker, { MonthYearValue } from '@/shared/components/common/MonthYearPicker';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/components/ui/table';

// Force dynamic rendering for this page since it uses useSearchParams
export const dynamic = 'force-dynamic';

const ITEMS_PER_PAGE = 25;

type SortField = 'date' | 'amount' | 'description' | 'category' | 'merchant';
type SortDirection = 'asc' | 'desc';

function TransactionsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [merchantFilter, setMerchantFilter] = useState('all');
  const [cardFilter, setCardFilter] = useState('all');
  const [dateRangeFilter, setDateRangeFilter] = useState('all');
  const [specificMonth, setSpecificMonth] = useState<MonthYearValue | null>(null);
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');

  // Sort states
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch user data
        const userData = await getCurrentUser();
        setUser(userData);

        // Fetch cards
        try {
          const cardsData = await getCards();
          setCards(Array.isArray(cardsData) ? cardsData : []);
        } catch {
          setCards([]);
        }

        // Fetch statements to get the most recent one
        try {
          const statementsData = await getStatements();
          if (isInitialLoad && Array.isArray(statementsData) && statementsData.length > 0) {
            // Get the most recent statement (backend returns sorted by newest first)
            const mostRecentStatement = statementsData[0];
            // Set default filter to most recent statement
            setSpecificMonth({
              month: mostRecentStatement.statement_month,
              year: mostRecentStatement.statement_year
            });
          }
        } catch {
          // statement fetch failure is non-fatal — default filter stays null
        }

        // Fetch all transactions
        try {
          const transactionsData = await getTransactions({ limit: 10000 });
          setTransactions(Array.isArray(transactionsData) ? transactionsData : []);
        } catch {
          setTransactions([]);
        }

        // Mark initial load as complete
        setIsInitialLoad(false);
      } catch {
        // Auth errors (401) are handled by the Axios interceptor.
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router, isInitialLoad]);

  // Read cardId from URL query parameters and set card filter
  useEffect(() => {
    const cardIdFromUrl = searchParams.get('cardId');
    if (cardIdFromUrl) {
      setCardFilter(cardIdFromUrl);
      // Clear the specific month filter when coming from cards page
      setDateRangeFilter('all');
      setSpecificMonth(null);
    }
  }, [searchParams]);

  // Get available categories based on current filters (excluding category filter itself)
  const categories = useMemo(() => {
    let filtered = [...transactions];

    // Apply all filters EXCEPT category filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (t) =>
          t.description?.toLowerCase().includes(query) ||
          t.merchant_name?.toLowerCase().includes(query) ||
          t.category?.name?.toLowerCase().includes(query)
      );
    }

    if (cardFilter !== 'all') {
      filtered = filtered.filter((t) => t.card_id === cardFilter);
    }

    if (merchantFilter !== 'all') {
      filtered = filtered.filter((t) => t.merchant_name === merchantFilter);
    }

    if (specificMonth) {
      filtered = filtered.filter(
        (t) => t.statement_month === specificMonth.month && t.statement_year === specificMonth.year
      );
    } else if (dateRangeFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date();

      switch (dateRangeFilter) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          filterDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case '3months':
          filterDate.setMonth(now.getMonth() - 3);
          break;
        case '6months':
          filterDate.setMonth(now.getMonth() - 6);
          break;
        case 'year':
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
      }

      filtered = filtered.filter(
        (t) => new Date(t.transaction_date) >= filterDate
      );
    }

    if (minAmount) {
      filtered = filtered.filter((t) => Number(t.amount) >= Number(minAmount));
    }
    if (maxAmount) {
      filtered = filtered.filter((t) => Number(t.amount) <= Number(maxAmount));
    }

    const uniqueCategories = new Set<string>();
    filtered.forEach((t) => {
      if (t.category?.name) {
        uniqueCategories.add(t.category.name);
      }
    });
    return Array.from(uniqueCategories).sort();
  }, [transactions, searchQuery, cardFilter, merchantFilter, dateRangeFilter, specificMonth, minAmount, maxAmount]);

  // Get available merchants based on current filters (excluding merchant filter itself)
  const merchants = useMemo(() => {
    let filtered = [...transactions];

    // Apply all filters EXCEPT merchant filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (t) =>
          t.description?.toLowerCase().includes(query) ||
          t.merchant_name?.toLowerCase().includes(query) ||
          t.category?.name?.toLowerCase().includes(query)
      );
    }

    if (cardFilter !== 'all') {
      filtered = filtered.filter((t) => t.card_id === cardFilter);
    }

    if (categoryFilter !== 'all') {
      filtered = filtered.filter((t) => t.category?.name === categoryFilter);
    }

    if (specificMonth) {
      filtered = filtered.filter(
        (t) => t.statement_month === specificMonth.month && t.statement_year === specificMonth.year
      );
    } else if (dateRangeFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date();

      switch (dateRangeFilter) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          filterDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case '3months':
          filterDate.setMonth(now.getMonth() - 3);
          break;
        case '6months':
          filterDate.setMonth(now.getMonth() - 6);
          break;
        case 'year':
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
      }

      filtered = filtered.filter(
        (t) => new Date(t.transaction_date) >= filterDate
      );
    }

    if (minAmount) {
      filtered = filtered.filter((t) => Number(t.amount) >= Number(minAmount));
    }
    if (maxAmount) {
      filtered = filtered.filter((t) => Number(t.amount) <= Number(maxAmount));
    }

    const uniqueMerchants = new Set<string>();
    filtered.forEach((t) => {
      if (t.merchant_name) {
        uniqueMerchants.add(t.merchant_name);
      }
    });
    return Array.from(uniqueMerchants).sort();
  }, [transactions, searchQuery, cardFilter, categoryFilter, dateRangeFilter, specificMonth, minAmount, maxAmount]);

  // Helper function to get card name by card_id
  const getCardName = (cardId: string): string => {
    const card = cards.find((c) => c.id === cardId);
    if (!card) return 'Unknown Card';
    return formatCardDisplayName(card.card_name, card.bank_name, card.card_type, card.last_four_digits);
  };

  // Filter and sort transactions
  const filteredAndSortedTransactions = useMemo(() => {
    let filtered = [...transactions];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (t) =>
          t.description?.toLowerCase().includes(query) ||
          t.merchant_name?.toLowerCase().includes(query) ||
          t.category?.name?.toLowerCase().includes(query)
      );
    }

    // Apply card filter
    if (cardFilter !== 'all') {
      filtered = filtered.filter((t) => t.card_id === cardFilter);
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter((t) => t.category?.name === categoryFilter);
    }

    // Apply merchant filter
    if (merchantFilter !== 'all') {
      filtered = filtered.filter((t) => t.merchant_name === merchantFilter);
    }

    // Apply specific month filter (takes priority over date range)
    if (specificMonth) {
      filtered = filtered.filter(
        (t) => t.statement_month === specificMonth.month && t.statement_year === specificMonth.year
      );
    }
    // Apply date range filter (only if no specific month is selected)
    else if (dateRangeFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date();

      switch (dateRangeFilter) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          filterDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case '3months':
          filterDate.setMonth(now.getMonth() - 3);
          break;
        case '6months':
          filterDate.setMonth(now.getMonth() - 6);
          break;
        case 'year':
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
      }

      filtered = filtered.filter(
        (t) => new Date(t.transaction_date) >= filterDate
      );
    }

    // Apply amount range filter
    if (minAmount) {
      filtered = filtered.filter((t) => Number(t.amount) >= Number(minAmount));
    }
    if (maxAmount) {
      filtered = filtered.filter((t) => Number(t.amount) <= Number(maxAmount));
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'date':
          aValue = new Date(a.transaction_date).getTime();
          bValue = new Date(b.transaction_date).getTime();
          break;
        case 'amount':
          aValue = Number(a.amount);
          bValue = Number(b.amount);
          break;
        case 'description':
          aValue = a.description?.toLowerCase() || '';
          bValue = b.description?.toLowerCase() || '';
          break;
        case 'category':
          aValue = a.category?.name?.toLowerCase() || '';
          bValue = b.category?.name?.toLowerCase() || '';
          break;
        case 'merchant':
          aValue = a.merchant_name?.toLowerCase() || '';
          bValue = b.merchant_name?.toLowerCase() || '';
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [transactions, searchQuery, cardFilter, categoryFilter, merchantFilter, dateRangeFilter, specificMonth, minAmount, maxAmount, sortField, sortDirection]);

  // Paginate transactions
  const paginatedTransactions = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    return filteredAndSortedTransactions.slice(startIndex, endIndex);
  }, [filteredAndSortedTransactions, currentPage]);

  const totalPages = Math.ceil(filteredAndSortedTransactions.length / ITEMS_PER_PAGE);

  // Calculate total amount for filtered transactions
  const filteredTotal = useMemo(() => {
    return filteredAndSortedTransactions.reduce(
      (sum, t) => sum + Number(t.amount),
      0
    );
  }, [filteredAndSortedTransactions]);

  // Handle sort toggle
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
    setCurrentPage(1); // Reset to first page when sorting
  };

  // Reset filters
  const resetFilters = () => {
    setSearchQuery('');
    setCategoryFilter('all');
    setMerchantFilter('all');
    setCardFilter('all');
    setDateRangeFilter('all');
    setSpecificMonth(null);
    setMinAmount('');
    setMaxAmount('');
    setCurrentPage(1);
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return (
        <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    return sortDirection === 'asc' ? (
      <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading your transactions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen fintech-bg">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <MobileTopBar onMenuClick={() => setSidebarOpen(true)} />

      {/* Main Content */}
      <div className="flex-1 lg:ml-64 pt-14 lg:pt-0">
        {/* Header */}
        <header className="bg-card border-b border-border px-4 sm:px-6 lg:px-8 py-3 sm:py-5">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-card-foreground mb-1">
                Transactions
              </h1>
              <p className="text-muted-foreground">
                View and manage all your transactions
              </p>
            </div>
            <div className="hidden sm:flex items-center space-x-4">
              {/* User Profile */}
              <div className="flex items-center space-x-3">
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

        {/* Main Content */}
        <main className="px-4 sm:px-6 lg:px-8 py-4 sm:py-5">
          {/* Filters Section */}
          <div className="fintech-card p-5 mb-5 animate-slide-in">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-foreground">Filters & Search</h3>
              <button
                onClick={resetFilters}
                className="text-sm text-primary hover:text-primary/80 font-medium transition-colors"
              >
                Reset All
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search Input */}
              <div className="lg:col-span-2">
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Search
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search by description, merchant, or category..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full px-4 py-2 pl-10 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                  />
                  <svg
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
              </div>

              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Category
                </label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All Categories' },
                    ...categories.map(cat => ({ value: cat, label: cat }))
                  ]}
                  value={categoryFilter}
                  onChange={(value) => {
                    setCategoryFilter(value);
                    setCurrentPage(1);
                  }}
                  placeholder="Select category..."
                  searchPlaceholder="Search categories..."
                  emptyMessage="No category found."
                />
              </div>

              {/* Merchant Filter */}
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Merchant
                </label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All Merchants' },
                    ...merchants.map(merchant => ({ value: merchant, label: merchant }))
                  ]}
                  value={merchantFilter}
                  onChange={(value) => {
                    setMerchantFilter(value);
                    setCurrentPage(1);
                  }}
                  placeholder="Select merchant..."
                  searchPlaceholder="Search merchants..."
                  emptyMessage="No merchant found."
                />
              </div>

              {/* Card Filter */}
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Card
                </label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All Cards' },
                    ...cards.map(card => ({
                      value: card.id,
                      label: formatCardDisplayName(card.card_name, card.bank_name, card.card_type, card.last_four_digits)
                    }))
                  ]}
                  value={cardFilter}
                  onChange={(value) => {
                    setCardFilter(value);
                    setCurrentPage(1);
                  }}
                  placeholder="Select card..."
                  searchPlaceholder="Search cards..."
                  emptyMessage="No card found."
                />
              </div>

              {/* Specific Month Filter */}
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Specific Month
                </label>
                <MonthYearPicker
                  value={specificMonth}
                  onChange={(value) => {
                    setSpecificMonth(value);
                    if (value) {
                      setDateRangeFilter('all'); // Clear date range filter when specific month is selected
                    }
                    setCurrentPage(1);
                  }}
                />
              </div>

              {/* Date Range Filter */}
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Date Range
                </label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All Time' },
                    { value: 'today', label: 'Today' },
                    { value: 'week', label: 'Last 7 Days' },
                    { value: 'month', label: 'Last Month' },
                    { value: '3months', label: 'Last 3 Months' },
                    { value: '6months', label: 'Last 6 Months' },
                    { value: 'year', label: 'Last Year' }
                  ]}
                  value={dateRangeFilter}
                  onChange={(value) => {
                    setDateRangeFilter(value);
                    if (value !== 'all') {
                      setSpecificMonth(null); // Clear specific month when date range is selected
                    }
                    setCurrentPage(1);
                  }}
                  placeholder="Select date range..."
                  searchPlaceholder="Search date ranges..."
                  emptyMessage="No date range found."
                />
              </div>

              {/* Amount Range */}
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Min Amount
                </label>
                <input
                  type="number"
                  placeholder="$0.00"
                  value={minAmount}
                  onChange={(e) => {
                    setMinAmount(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Max Amount
                </label>
                <input
                  type="number"
                  placeholder="$9999.99"
                  value={maxAmount}
                  onChange={(e) => {
                    setMaxAmount(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                />
              </div>
            </div>

            {/* Active Filters Summary */}
            {(searchQuery || categoryFilter !== 'all' || merchantFilter !== 'all' || dateRangeFilter !== 'all' || specificMonth || minAmount || maxAmount) && (
              <div className="mt-4 pt-4 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  Showing <span className="font-bold text-foreground">{filteredAndSortedTransactions.length}</span> of{' '}
                  <span className="font-bold text-foreground">{transactions.length}</span> transactions
                </p>
              </div>
            )}
          </div>

          {/* Transactions Table */}
          <div className="fintech-card overflow-hidden animate-slide-in" style={{ animationDelay: "0.1s" }}>
            <div className="px-6 py-5 border-b border-border">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-foreground">
                    All Transactions
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {filteredAndSortedTransactions.length === 0
                      ? 'No transactions found'
                      : `Showing ${(currentPage - 1) * ITEMS_PER_PAGE + 1}-${Math.min(
                          currentPage * ITEMS_PER_PAGE,
                          filteredAndSortedTransactions.length
                        )} of ${filteredAndSortedTransactions.length} transactions`}
                  </p>
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              {filteredAndSortedTransactions.length > 0 ? (
                <>
                  <Table>
                    <TableHeader className="bg-muted/20">
                      <TableRow className="hover:bg-muted/20">
                        <TableHead
                          className="px-6 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('date')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Date</span>
                            <SortIcon field="date" />
                          </div>
                        </TableHead>
                        <TableHead
                          className="px-6 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('description')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Description</span>
                            <SortIcon field="description" />
                          </div>
                        </TableHead>
                        <TableHead
                          className="px-6 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('merchant')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Merchant</span>
                            <SortIcon field="merchant" />
                          </div>
                        </TableHead>
                        <TableHead
                          className="px-6 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('category')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Category</span>
                            <SortIcon field="category" />
                          </div>
                        </TableHead>
                        <TableHead className="px-6 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
                          Card
                        </TableHead>
                        <TableHead
                          className="px-6 py-3.5 text-[11px] font-bold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors text-right"
                          onClick={() => handleSort('amount')}
                        >
                          <div className="flex items-center justify-end space-x-1">
                            <span>Amount</span>
                            <SortIcon field="amount" />
                          </div>
                        </TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {paginatedTransactions.map((transaction) => (
                        <TableRow key={transaction.id} className="hover:bg-muted/10 transition-all duration-200">
                          <TableCell className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground font-medium">
                            {new Date(transaction.transaction_date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </TableCell>
                          <TableCell className="px-6 py-4 text-sm">
                            <div className="font-semibold text-foreground">{transaction.description}</div>
                          </TableCell>
                          <TableCell className="px-6 py-4 text-sm text-muted-foreground">
                            {transaction.merchant_name || '-'}
                          </TableCell>
                          <TableCell className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className="inline-flex items-center px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                              {transaction.category?.name || 'Uncategorized'}
                            </span>
                          </TableCell>
                          <TableCell className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                            {getCardName(transaction.card_id)}
                          </TableCell>
                          <TableCell className="px-6 py-4 whitespace-nowrap text-right text-sm font-bold text-foreground">
                            {formatCurrency(transaction.amount)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Pagination Controls */}
                  {totalPages > 1 && (
                    <div className="px-6 py-4 border-t border-border flex items-center justify-between">
                      <button
                        onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                        className="px-4 py-2 text-sm font-medium text-primary bg-primary/10 rounded-lg hover:bg-primary/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Previous
                      </button>

                      <div className="flex items-center space-x-2">
                        {/* Show page numbers with ellipsis for large page counts */}
                        {totalPages <= 7 ? (
                          // Show all pages if 7 or less
                          Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                            <button
                              key={page}
                              onClick={() => setCurrentPage(page)}
                              className={`w-10 h-10 rounded-lg text-sm font-medium transition-colors ${
                                currentPage === page
                                  ? 'bg-primary text-white'
                                  : 'text-muted-foreground hover:bg-muted'
                              }`}
                            >
                              {page}
                            </button>
                          ))
                        ) : (
                          // Show pages with ellipsis for more than 7 pages
                          <>
                            {currentPage > 3 && (
                              <>
                                <button
                                  onClick={() => setCurrentPage(1)}
                                  className="w-10 h-10 rounded-lg text-sm font-medium text-muted-foreground hover:bg-muted transition-colors"
                                >
                                  1
                                </button>
                                <span className="text-muted-foreground">...</span>
                              </>
                            )}
                            {Array.from({ length: 5 }, (_, i) => {
                              let page = currentPage - 2 + i;
                              if (page < 1) page = 1;
                              if (page > totalPages) page = totalPages;
                              return page;
                            })
                              .filter((page, index, array) => array.indexOf(page) === index)
                              .map((page) => (
                                <button
                                  key={page}
                                  onClick={() => setCurrentPage(page)}
                                  className={`w-10 h-10 rounded-lg text-sm font-medium transition-colors ${
                                    currentPage === page
                                      ? 'bg-primary text-white'
                                      : 'text-muted-foreground hover:bg-muted'
                                  }`}
                                >
                                  {page}
                                </button>
                              ))}
                            {currentPage < totalPages - 2 && (
                              <>
                                <span className="text-muted-foreground">...</span>
                                <button
                                  onClick={() => setCurrentPage(totalPages)}
                                  className="w-10 h-10 rounded-lg text-sm font-medium text-muted-foreground hover:bg-muted transition-colors"
                                >
                                  {totalPages}
                                </button>
                              </>
                            )}
                          </>
                        )}
                      </div>

                      <button
                        onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                        disabled={currentPage >= totalPages}
                        className="px-4 py-2 text-sm font-medium text-primary bg-primary/10 rounded-lg hover:bg-primary/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Next
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <div className="px-6 py-12">
                  <div className="max-w-md mx-auto text-center">
                    <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                        />
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">
                      No transactions found
                    </h3>
                    <p className="text-muted-foreground mb-6">
                      {transactions.length === 0
                        ? 'Upload your first credit card statement to get started!'
                        : 'Try adjusting your filters to see more results.'}
                    </p>
                    {transactions.length === 0 && (
                      <button
                        onClick={() => router.push('/upload')}
                        className="inline-flex items-center space-x-2 px-6 py-3 gradient-indigo-purple text-white font-medium rounded-xl hover:opacity-90 transition-opacity shadow-lg"
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
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Total Summary */}
            {filteredAndSortedTransactions.length > 0 && (
              <div className="px-6 py-4 bg-muted/30 border-t border-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span className="text-sm font-medium text-muted-foreground">
                      {searchQuery || categoryFilter !== 'all' || merchantFilter !== 'all' || dateRangeFilter !== 'all' || specificMonth || minAmount || maxAmount
                        ? 'Filtered Total'
                        : 'Grand Total'}
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-foreground">
                      {formatCurrency(filteredTotal)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {filteredAndSortedTransactions.length} {filteredAndSortedTransactions.length === 1 ? 'transaction' : 'transactions'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}

// Wrap in Suspense to handle useSearchParams
export default function TransactionsPage() {
  return (
    <Suspense fallback={
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
          <p className="mt-2 text-sm text-muted-foreground">Loading transactions...</p>
        </div>
      </div>
    }>
      <TransactionsPageContent />
    </Suspense>
  );
}
