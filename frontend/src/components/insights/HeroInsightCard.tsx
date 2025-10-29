'use client';

import { Sparkles, X, CheckCircle } from 'lucide-react';
import { useState } from 'react';

export interface Insight {
  id: string;
  title: string;
  description: string;
  insight_type: string;
  impact_score: number; // 1-10
  potential_savings?: number | null;
  created_at: string;
  dismissed_at?: string | null;
}

// Helper to map impact_score to priority
function getPriority(impact_score: number): 'high' | 'medium' | 'low' {
  if (impact_score >= 8) return 'high';
  if (impact_score >= 5) return 'medium';
  return 'low';
}

interface HeroInsightCardProps {
  insight: Insight;
  onDismiss?: (id: string) => void;
  onComplete?: (id: string) => void;
  onViewDetails?: () => void;
}

const priorityColors = {
  high: 'from-red-500 to-orange-500',
  medium: 'from-primary to-accent',
  low: 'from-blue-500 to-cyan-500',
};

const priorityBadgeColors = {
  high: 'bg-red-500/10 text-red-500 border-red-500/20',
  medium: 'bg-primary/10 text-primary border-primary/20',
  low: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
};

export default function HeroInsightCard({ insight, onDismiss, onComplete, onViewDetails }: HeroInsightCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const priority = getPriority(insight.impact_score);
  const isActive = !insight.dismissed_at;

  return (
    <div
      className="relative fintech-card overflow-hidden"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${priorityColors[priority]} opacity-5`} />

      {/* Content */}
      <div className="relative p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl bg-gradient-to-br ${priorityColors[priority]}`}>
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-foreground">{insight.title}</h3>
                <span className={`px-2 py-0.5 text-xs font-bold rounded-full border ${priorityBadgeColors[priority]}`}>
                  {priority.toUpperCase()}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                {new Date(insight.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {onComplete && isActive && (
              <button
                onClick={() => onComplete(insight.id)}
                className="p-2 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500/20 transition-colors"
                title="Mark as completed"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
            )}
            {onDismiss && isActive && (
              <button
                onClick={() => onDismiss(insight.id)}
                className="p-2 rounded-lg bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        <p className="text-sm text-foreground leading-relaxed mb-4">
          {insight.description}
        </p>

        {/* Potential Savings */}
        {insight.potential_savings && insight.potential_savings > 0 && (
          <div className="mt-4 p-4 rounded-lg bg-muted/30 border border-border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Potential Monthly Savings
                </p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  ${insight.potential_savings.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Impact Score
                </p>
                <p className="text-lg font-bold text-foreground mt-1">
                  {insight.impact_score}/10
                </p>
              </div>
            </div>
          </div>
        )}

        {/* View Details Button */}
        {onViewDetails && (
          <button
            onClick={onViewDetails}
            className="mt-4 w-full px-4 py-3 bg-primary hover:bg-primary/90 text-white font-semibold rounded-lg transition-all flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
          >
            <span>View Linked Transactions</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        )}
      </div>

      {/* Bottom Gradient Bar */}
      <div className={`h-1 bg-gradient-to-r ${priorityColors[priority]}`} />
    </div>
  );
}
