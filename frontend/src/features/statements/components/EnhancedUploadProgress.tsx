'use client';

import { useEffect, useState } from 'react';
import { Progress } from '@/shared/components/ui/progress';

interface EnhancedUploadProgressProps {
  fileName: string;
  fileSize: number; // in bytes
  progress: number; // 0-100
  stage: 'uploading' | 'extracting' | 'processing' | 'complete';
  onCancel?: () => void;
}

const stageConfig = {
  uploading: {
    title: 'Uploading Statement',
    description: 'Securely transferring your PDF to our servers',
    icon: '📤',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  extracting: {
    title: 'Reading Statement',
    description: 'Extracting text and identifying card details',
    icon: '🔍',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
  processing: {
    title: 'AI Processing',
    description: 'Analyzing transactions and categorizing spending',
    icon: '🤖',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
  },
  complete: {
    title: 'Complete!',
    description: 'Your statement has been processed successfully',
    icon: '✨',
    color: 'text-accent',
    bgColor: 'bg-accent/10',
  },
};

const financialTips = [
  // Sweet mix of SG-specific, universal wisdom, fun facts, and psychology
  {
    icon: '💡',
    title: 'Compound Magic',
    tip: 'Albert Einstein called compound interest "the 8th wonder of the world." $100 invested at 10% becomes $2,594 in 35 years!',
  },
  {
    icon: '🏛️',
    title: 'CPF Advantage',
    tip: 'Your CPF Special Account earns 4% guaranteed interest - that\'s better than most savings accounts worldwide!',
  },
  {
    icon: '🧠',
    title: 'Money Psychology',
    tip: 'Studies show people who write down their financial goals are 42% more likely to achieve them. Start today!',
  },
  {
    icon: '🍜',
    title: 'Hawker Wisdom',
    tip: 'Eating at hawker centres 5x a week vs restaurants saves over $3,000 annually. That\'s a holiday fund!',
  },
  {
    icon: '📊',
    title: '50/30/20 Rule',
    tip: 'Budget your income: 50% needs, 30% wants, 20% savings. Simple but powerful framework for financial health.',
  },
  {
    icon: '💳',
    title: 'Credit Card Trap',
    tip: 'Paying only the minimum on a $5,000 balance at 24% APR takes 25 years and costs $8,900 in interest!',
  },
  {
    icon: '🌍',
    title: 'Global Fact',
    tip: 'The average millionaire has 7 income streams. Diversification isn\'t just for investments!',
  },
  {
    icon: '🎁',
    title: 'Cashback Smart',
    tip: 'SG cashback cards offer 1.5-8% returns. On $3,000 monthly spend, that\'s $540-$2,880 back per year!',
  },
  {
    icon: '⏰',
    title: 'Time is Money',
    tip: 'Starting to invest at 25 vs 35 can result in 2x more wealth by retirement, even with the same contributions.',
  },
  {
    icon: '🚇',
    title: 'Transport Math',
    tip: 'Public transport: $128/month. Car ownership: $1,000+/month. That\'s $10,464 yearly savings for other goals!',
  },
  {
    icon: '🎯',
    title: 'Specific Beats Vague',
    tip: 'People who set specific goals like "Save $10,000 by Dec 2025" succeed 90% more than those who say "save more."',
  },
  {
    icon: '📉',
    title: 'SG Tax Perk',
    tip: 'No capital gains tax in Singapore means your investment profits are tax-free. Major advantage for wealth building!',
  },
  {
    icon: '☕',
    title: 'Latte Factor',
    tip: 'That daily $5 coffee costs $1,825/year. Invested at 8% for 20 years? That\'s $89,000 in your retirement fund.',
  },
  {
    icon: '🏆',
    title: 'Billionaire Habit',
    tip: 'Warren Buffett reads 500+ pages daily. Bill Gates reads 50 books/year. Knowledge compounds faster than money.',
  },
  {
    icon: '💰',
    title: 'CPF Top-Up Magic',
    tip: 'Cash top-ups to CPF enjoy tax relief up to $16,000/year ($8K self + $8K family). Save on taxes while saving!',
  },
  {
    icon: '📱',
    title: 'Awareness Power',
    tip: 'Simply tracking your expenses reduces unnecessary spending by 15-20% on average. What gets measured gets managed.',
  },
  {
    icon: '🏠',
    title: 'Property Reality',
    tip: 'In Singapore, median HDB resale is $540K. With 20% down, you need $108K + stamp duty + renovation. Plan early!',
  },
  {
    icon: '🎲',
    title: 'Risk vs Reward',
    tip: 'Historically, stocks return 10% annually, bonds 5%, savings 1-2%. Higher returns need higher risk tolerance.',
  },
  {
    icon: '💎',
    title: 'REIT Income',
    tip: 'Singapore REITs yield 5-6% dividends quarterly. That\'s higher than CPF OA and more liquid than property!',
  },
  {
    icon: '🧘',
    title: 'Automation Wins',
    tip: 'Automate savings and bills. Research shows people who automate save 2x more than those who do it manually.',
  },
  {
    icon: '📈',
    title: 'Market Wisdom',
    tip: 'The S&P 500 has never lost money over any 20-year period. Long-term investing smooths out volatility.',
  },
  {
    icon: '🔔',
    title: 'Credit Score Matters',
    tip: 'Good credit scores get 1-2% better loan rates. On a $500K mortgage, that\'s $50,000+ saved over 25 years!',
  },
  {
    icon: '🎓',
    title: 'Learn to Earn',
    tip: 'Every dollar spent on self-education returns $10-50 in lifetime earnings. Best investment you can make.',
  },
  {
    icon: '🌟',
    title: 'SRS Tax Benefit',
    tip: 'Supplementary Retirement Scheme contributions get tax relief up to $15,300. Grow investments tax-free until withdrawal!',
  },
  {
    icon: '💪',
    title: 'Side Income',
    tip: 'Average person has 96,000 hours in their career. Monetizing just 5% of free time can double your retirement savings.',
  },
  {
    icon: '🛡️',
    title: 'Insurance First',
    tip: 'Term life insurance costs $40/month for $500K coverage in your 30s. That\'s just $14,400 for 30 years of protection.',
  },
  {
    icon: '🎯',
    title: 'Pay Yourself First',
    tip: 'Save before spending, not with what\'s left. Treat savings like a non-negotiable bill to your future self.',
  },
  {
    icon: '🌐',
    title: 'Inflation Reality',
    tip: 'At 3% inflation, your money loses half its purchasing power in 24 years. Invest to outpace inflation.',
  },
  {
    icon: '🏦',
    title: 'High-Interest Accounts',
    tip: 'SG banks offer 3-4% interest with salary crediting. On $50K savings, that\'s $1,500-2,000 extra per year!',
  },
  {
    icon: '⚡',
    title: 'Emergency Fund',
    tip: '78% of people live paycheck to paycheck. Build 6 months expenses emergency fund for true financial security.',
  },
];

export default function EnhancedUploadProgress({
  fileName,
  fileSize,
  progress,
  stage,
  onCancel,
}: EnhancedUploadProgressProps) {
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  const [showMilestone, setShowMilestone] = useState(false);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  // Rotate tips every 8 seconds for better readability
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % financialTips.length);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  // Show milestone celebrations
  useEffect(() => {
    if (progress === 30 || progress === 60 || progress === 100) {
      setShowMilestone(true);
      const timeout = setTimeout(() => setShowMilestone(false), 2000);
      return () => clearTimeout(timeout);
    }
  }, [progress]);

  const currentStage = stageConfig[stage];
  const currentTip = financialTips[currentTipIndex];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Main Progress Card */}
      <div className="bg-card rounded-2xl border border-border shadow-lg overflow-hidden">
        {/* Header with File Info */}
        <div className="bg-gradient-to-r from-primary/5 to-accent/5 px-6 py-4 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 flex-1 min-w-0">
              {/* PDF Icon */}
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                <svg
                  className="w-6 h-6 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>

              {/* File Details */}
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-foreground truncate" title={fileName}>
                  {fileName}
                </p>
                <p className="text-sm text-muted-foreground">{formatFileSize(fileSize)}</p>
              </div>
            </div>

            {/* Cancel Button */}
            {onCancel && stage !== 'complete' && (
              <button
                onClick={onCancel}
                className="text-muted-foreground hover:text-foreground transition-colors p-2 rounded-lg hover:bg-muted ml-4"
                title="Cancel upload"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Processing Stage Animation */}
        <div className="p-6">
          <div className="flex items-start space-x-4 mb-6">
            {/* Animated Icon */}
            <div
              className={`w-16 h-16 rounded-2xl ${currentStage.bgColor} flex items-center justify-center flex-shrink-0 animate-pulse-glow`}
            >
              <span className="text-3xl animate-bounce">{currentStage.icon}</span>
            </div>

            {/* Stage Info */}
            <div className="flex-1 min-w-0">
              <h3 className={`text-xl font-bold ${currentStage.color} mb-1`}>
                {currentStage.title}
              </h3>
              <p className="text-muted-foreground">{currentStage.description}</p>

              {/* Progress Percentage */}
              <div className="mt-3 flex items-center space-x-3">
                <Progress value={progress} className="h-3" />
                <span className="text-2xl font-bold text-foreground min-w-[4rem] text-right">
                  {progress}%
                </span>
              </div>
            </div>
          </div>

          {/* Stage Timeline */}
          <div className="relative flex items-start justify-between mt-6 px-2">
            {(['uploading', 'extracting', 'processing', 'complete'] as const).map(
              (stageName, index) => {
                const stageInfo = stageConfig[stageName];
                const isActive = stageName === stage;
                const isPast =
                  ['uploading', 'extracting', 'processing', 'complete'].indexOf(stage) > index;
                const isComplete = stage === 'complete' && stageName === 'complete';

                return (
                  <div key={stageName} className="flex flex-col items-center flex-1 relative">
                    {/* Stage Icon */}
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 z-10 ${
                        isComplete
                          ? 'bg-accent text-white scale-110 shadow-lg shadow-accent/50'
                          : isPast || isActive
                          ? 'bg-primary text-white shadow-md'
                          : 'bg-muted text-muted-foreground'
                      } ${isActive ? 'animate-pulse' : ''}`}
                    >
                      {isComplete ? (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      ) : (
                        <span className="text-lg">{stageInfo.icon}</span>
                      )}
                    </div>

                    {/* Stage Label */}
                    <p
                      className={`text-xs mt-2 text-center font-medium transition-colors ${
                        isActive ? 'text-foreground font-semibold' : 'text-muted-foreground'
                      }`}
                    >
                      {stageName.charAt(0).toUpperCase() + stageName.slice(1)}
                    </p>

                    {/* Connector Line to Next Stage */}
                    {index < 3 && (
                      <div className="absolute left-1/2 top-5 w-full h-0.5 flex items-center">
                        <div
                          className={`h-0.5 w-full ml-5 transition-all duration-500 ${
                            isPast ? 'bg-primary' : 'bg-muted'
                          }`}
                        />
                      </div>
                    )}
                  </div>
                );
              }
            )}
          </div>
        </div>
      </div>

      {/* Financial Tip Card - Rotating */}
      {stage !== 'complete' && (
        <div className="bg-gradient-to-br from-primary/5 to-accent/5 rounded-2xl border border-border p-6 animate-fade-in">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-xl bg-card flex items-center justify-center flex-shrink-0">
              <span className="text-2xl">{currentTip.icon}</span>
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-foreground mb-1">{currentTip.title}</h4>
              <p className="text-sm text-muted-foreground leading-relaxed">{currentTip.tip}</p>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Preview Skeleton - Show during processing */}
      {(stage === 'processing' || stage === 'complete') && stage !== 'complete' && (
        <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-foreground">Preparing your transactions...</h4>
            <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>

          {/* Skeleton Cards */}
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="flex items-center justify-between p-4 rounded-xl bg-muted/50 animate-pulse"
              style={{ animationDelay: `${i * 150}ms` }}
            >
              <div className="flex items-center space-x-3 flex-1">
                <div className="w-10 h-10 rounded-lg bg-primary/20" />
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-primary/20 rounded w-2/3" />
                  <div className="h-3 bg-primary/10 rounded w-1/3" />
                </div>
              </div>
              <div className="h-6 bg-primary/20 rounded w-20" />
            </div>
          ))}
        </div>
      )}

      {/* Milestone Celebration */}
      {showMilestone && (
        <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-50">
          <div className="bg-accent text-white px-8 py-4 rounded-2xl shadow-2xl animate-bounce">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">🎉</span>
              <span className="text-lg font-bold">
                {progress === 30 && 'Text Extracted!'}
                {progress === 60 && 'Card Details Found!'}
                {progress === 100 && 'All Done!'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
