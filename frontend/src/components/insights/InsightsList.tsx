'use client';

import { Sparkles, TrendingUp, AlertTriangle, Info, X, CheckCircle } from 'lucide-react';
import { Insight } from './HeroInsightCard';

interface InsightsListProps {
  insights: Insight[];
  onDismiss?: (id: string) => void;
  onComplete?: (id: string) => void;
  compact?: boolean;
}

const insightIcons = {
  spending_pattern: TrendingUp,
  unusual_activity: AlertTriangle,
  recommendation: Sparkles,
  alert: AlertTriangle,
  default: Info,
};

const priorityColors = {
  high: 'text-red-500 bg-red-500/10 border-red-500/20',
  medium: 'text-primary bg-primary/10 border-primary/20',
  low: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
};

export default function InsightsList({ insights, onDismiss, onComplete, compact = false }: InsightsListProps) {
  if (insights.length === 0) {
    return (
      <div className="fintech-card p-8 text-center">
        <Sparkles className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
        <p className="text-sm font-medium text-foreground mb-1">No insights yet</p>
        <p className="text-xs text-muted-foreground">
          Upload statements to get AI-powered insights
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {insights.map((insight) => {
        const IconComponent = insightIcons[insight.insight_type as keyof typeof insightIcons] || insightIcons.default;

        return (
          <div
            key={insight.id}
            className={`fintech-card ${compact ? 'p-4' : 'p-5'} card-hover relative`}
          >
            <div className="flex items-start gap-4">
              <div className={`p-2.5 rounded-lg ${priorityColors[insight.priority]} border flex-shrink-0`}>
                <IconComponent className="w-4 h-4" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex-1">
                    <h4 className={`${compact ? 'text-sm' : 'text-base'} font-semibold text-foreground mb-1`}>
                      {insight.title}
                    </h4>
                    <p className={`${compact ? 'text-xs' : 'text-sm'} text-muted-foreground leading-relaxed`}>
                      {insight.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {onComplete && insight.status === 'active' && (
                      <button
                        onClick={() => onComplete(insight.id)}
                        className="p-1.5 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500/20 transition-colors"
                        title="Mark as completed"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                    )}
                    {onDismiss && (
                      <button
                        onClick={() => onDismiss(insight.id)}
                        className="p-1.5 rounded-lg bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
                        title="Dismiss"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Additional Data */}
                {!compact && insight.data && Object.keys(insight.data).length > 0 && (
                  <div className="mt-3 p-3 rounded-lg bg-muted/30 border border-border">
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(insight.data).slice(0, 4).map(([key, value]) => (
                        <div key={key}>
                          <p className="text-[10px] text-muted-foreground uppercase tracking-wide">
                            {key.replace(/_/g, ' ')}
                          </p>
                          <p className="text-xs font-semibold text-foreground mt-0.5">
                            {typeof value === 'number' && key.includes('amount')
                              ? `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                              : String(value)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div className="flex items-center gap-3 mt-3">
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${priorityColors[insight.priority]}`}>
                    {insight.priority.toUpperCase()}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(insight.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                  {insight.status === 'completed' && (
                    <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-green-500/10 text-green-500 border border-green-500/20">
                      COMPLETED
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
