'use client';

import { useRouter } from 'next/navigation';
import { StatementUploadResponse } from '@/models';

interface UploadResultsProps {
  result: StatementUploadResponse;
  onUploadAnother: () => void;
}

export default function UploadResults({ result, onUploadAnother }: UploadResultsProps) {
  const router = useRouter();
  const { statement, extracted_transactions, message, stats } = result;

  // Get category distribution
  const categoryEntries = stats.categories_assigned
    ? Object.entries(stats.categories_assigned).sort((a, b) => b[1] - a[1])
    : [];

  // Get the card info from the first transaction if available
  const cardInfo = extracted_transactions[0]?.card;

  return (
    <div className="animate-fade-in space-y-6">
      {/* Success Message */}
      <div className="bg-accent/10 border border-accent/20 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <svg className="w-6 h-6 text-accent" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-accent mb-1">Upload Successful!</h3>
            <p className="text-sm text-accent/90">{message}</p>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="bg-card rounded-2xl border border-border overflow-hidden">
        <div className="px-6 py-5 bg-gradient-to-r from-primary/5 to-secondary/5 border-b border-border">
          <h3 className="text-lg font-bold text-foreground mb-4">Extraction Summary</h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Transactions */}
            <div className="bg-card rounded-xl p-4 border border-border">
              <p className="text-xs font-medium text-muted-foreground mb-1">Transactions</p>
              <p className="text-2xl font-bold text-foreground">{stats.total_transactions}</p>
            </div>

            {/* Total Amount */}
            <div className="bg-card rounded-xl p-4 border border-border">
              <p className="text-xs font-medium text-muted-foreground mb-1">Total Amount</p>
              <p className="text-2xl font-bold text-foreground">
                ${stats.total_amount.toFixed(2)}
              </p>
            </div>

            {/* AI Confidence */}
            <div className="bg-card rounded-xl p-4 border border-border">
              <p className="text-xs font-medium text-muted-foreground mb-1">AI Confidence</p>
              <p className="text-2xl font-bold text-accent">
                {Math.round(stats.avg_confidence * 100)}%
              </p>
            </div>

            {/* Categories */}
            <div className="bg-card rounded-xl p-4 border border-border">
              <p className="text-xs font-medium text-muted-foreground mb-1">Categories</p>
              <p className="text-2xl font-bold text-foreground">{categoryEntries.length}</p>
            </div>
          </div>
        </div>

        <div className="p-6">
          {/* Card Information (if available) */}
          {cardInfo && (
            <div className="mb-6">
              <h4 className="font-semibold text-foreground mb-3">Card Information</h4>
              <div className="gradient-indigo-purple rounded-xl p-6 text-white">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <p className="text-sm opacity-90">{cardInfo.bank_name}</p>
                    <p className="text-xs opacity-75">{cardInfo.card_name}</p>
                  </div>
                  <div className="w-10 h-10">
                    <svg fill="currentColor" viewBox="0 0 24 24">
                      <circle cx="9" cy="12" r="5" opacity="0.7" />
                      <circle cx="15" cy="12" r="5" opacity="0.7" />
                    </svg>
                  </div>
                </div>
                <p className="text-2xl font-mono mb-4">•••• •••• •••• {cardInfo.last_four_digits}</p>
                <div className="flex justify-between items-center text-sm">
                  <div>
                    <p className="opacity-75">Statement Period</p>
                    <p className="font-semibold text-lg">
                      {statement.statement_month}/{statement.statement_year}
                    </p>
                  </div>
                  {cardInfo.credit_limit && (
                    <div className="text-right">
                      <p className="opacity-75">Credit Limit</p>
                      <p className="font-semibold text-lg">
                        ${Number(cardInfo.credit_limit).toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>
                <div className="mt-4 pt-4 border-t border-white border-opacity-20">
                  <span className="inline-flex items-center space-x-1 text-xs bg-card bg-opacity-20 px-3 py-1 rounded-full">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span>Auto-created from PDF</span>
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Category Distribution */}
          {categoryEntries.length > 0 && (
            <div className="mb-6">
              <h4 className="font-semibold text-foreground mb-4">Category Distribution</h4>
              <div className="space-y-3">
                {categoryEntries.map(([categoryName, count], index) => {
                  const percentage = (count / stats.total_transactions) * 100;
                  const colors = [
                    '#818CF8',
                    '#34D399',
                    '#FBBF24',
                    '#F472B6',
                    '#A78BFA',
                    '#60A5FA',
                    '#FB923C',
                  ];
                  const color = colors[index % colors.length];

                  return (
                    <div key={categoryName}>
                      <div className="flex justify-between items-center mb-1">
                        <div className="flex items-center space-x-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: color }}
                          />
                          <span className="text-sm text-foreground">{categoryName}</span>
                        </div>
                        <span className="text-sm font-medium text-foreground">
                          {count} {count === 1 ? 'transaction' : 'transactions'}
                        </span>
                      </div>
                      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{ width: `${percentage}%`, backgroundColor: color }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <button
              onClick={onUploadAnother}
              className="flex-1 px-6 py-3 bg-muted text-foreground font-medium rounded-xl hover:bg-muted/80 transition-colors"
            >
              Upload Another
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="flex-1 px-6 py-3 gradient-indigo-purple text-white font-medium rounded-xl hover:opacity-90 transition-opacity shadow-lg"
            >
              View Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
