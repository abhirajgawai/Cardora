'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser } from '@/lib/api/auth';
import { getTransactions } from '@/lib/api/transactions';
import { getCards } from '@/lib/api/cards';
import { User, Transaction, CreditCard } from '@/models';
import { extractErrorMessage, isAuthError } from '@/utils/errorHandler';
import { formatCardDisplayName } from '@/utils/cardFormatter';
import Sidebar from '@/components/Sidebar';
import Footer from '@/components/Footer';
import { SearchableSelect } from '@/components/ui/SearchableSelect';

const ITEMS_PER_PAGE = 25;

type SortField = 'date' | 'amount' | 'description' | 'category' | 'merchant';
type SortDirection = 'asc' | 'desc';

export default function TransactionsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [cards, setCards] = useState<CreditCard[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [merchantFilter, setMerchantFilter] = useState('all');
  const [dateRangeFilter, setDateRangeFilter] = useState('all');
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');

  // Sort states
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch user data
        const userData = await getCurrentUser();
        setUser(userData);

        // Fetch cards
        try {
          const cardsData = await getCards();
          if (!Array.isArray(cardsData)) {
            console.warn('Cards data is not an array:', cardsData);
            setCards([]);
          } else {
            setCards(cardsData);
          }
        } catch (cardError) {
          console.warn('Failed to fetch cards:', extractErrorMessage(cardError));
          setCards([]);
        }

        // Fetch all transactions
        try {
          const transactionsData = await getTransactions({ limit: 10000 });
          if (!Array.isArray(transactionsData)) {
            console.warn('Transactions data is not an array:', transactionsData);
            setTransactions([]);
          } else {
            setTransactions(transactionsData);
          }
        } catch (transactionError) {
          console.warn('Failed to fetch transactions:', extractErrorMessage(transactionError));
          setTransactions([]);
        }
      } catch (error) {
        console.error('Transactions page error:', extractErrorMessage(error));
        if (isAuthError(error)) {
          console.log('Authentication failed (401), clearing token and redirecting to login');
          localStorage.removeItem('access_token');
          router.push('/login');
        } else {
          console.error('Failed to load transactions data:', extractErrorMessage(error));
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  // Get unique categories for filter dropdown
  const categories = useMemo(() => {
    const uniqueCategories = new Set<string>();
    transactions.forEach((t) => {
      if (t.category?.name) {
        uniqueCategories.add(t.category.name);
      }
    });
    return Array.from(uniqueCategories).sort();
  }, [transactions]);

  // Get unique merchants for filter dropdown
  const merchants = useMemo(() => {
    const uniqueMerchants = new Set<string>();
    transactions.forEach((t) => {
      if (t.merchant_name) {
        uniqueMerchants.add(t.merchant_name);
      }
    });
    return Array.from(uniqueMerchants).sort();
  }, [transactions]);

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

    // Apply category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter((t) => t.category?.name === categoryFilter);
    }

    // Apply merchant filter
    if (merchantFilter !== 'all') {
      filtered = filtered.filter((t) => t.merchant_name === merchantFilter);
    }

    // Apply date range filter
    if (dateRangeFilter !== 'all') {
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
  }, [transactions, searchQuery, categoryFilter, merchantFilter, dateRangeFilter, minAmount, maxAmount, sortField, sortDirection]);

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
    setDateRangeFilter('all');
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
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 ml-64">
        {/* Header */}
        <header className="bg-card border-b border-border px-8 py-5">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-card-foreground mb-1">
                Transactions
              </h1>
              <p className="text-muted-foreground">
                View and manage all your transactions
              </p>
            </div>
            <div className="flex items-center space-x-4">
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
        <main className="px-8 py-5">
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
            {(searchQuery || categoryFilter !== 'all' || merchantFilter !== 'all' || dateRangeFilter !== 'all' || minAmount || maxAmount) && (
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
                  <table className="w-full">
                    <thead className="bg-muted/30">
                      <tr>
                        <th
                          className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('date')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Date</span>
                            <SortIcon field="date" />
                          </div>
                        </th>
                        <th
                          className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('description')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Description</span>
                            <SortIcon field="description" />
                          </div>
                        </th>
                        <th
                          className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('merchant')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Merchant</span>
                            <SortIcon field="merchant" />
                          </div>
                        </th>
                        <th
                          className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('category')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Category</span>
                            <SortIcon field="category" />
                          </div>
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                          Card
                        </th>
                        <th
                          className="px-6 py-4 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                          onClick={() => handleSort('amount')}
                        >
                          <div className="flex items-center justify-end space-x-1">
                            <span>Amount</span>
                            <SortIcon field="amount" />
                          </div>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {paginatedTransactions.map((transaction) => (
                        <tr key={transaction.id} className="hover:bg-muted/20 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                            {new Date(transaction.transaction_date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </td>
                          <td className="px-6 py-4 text-sm text-foreground">
                            <div className="font-medium">{transaction.description}</div>
                          </td>
                          <td className="px-6 py-4 text-sm text-muted-foreground">
                            {transaction.merchant_name || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                              {transaction.category?.name || 'Uncategorized'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                            {getCardName(transaction.card_id)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-foreground">
                            ${Number(transaction.amount).toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

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
                      {searchQuery || categoryFilter !== 'all' || merchantFilter !== 'all' || dateRangeFilter !== 'all' || minAmount || maxAmount
                        ? 'Filtered Total'
                        : 'Grand Total'}
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-foreground">
                      ${filteredTotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
