'use client';

import { Sparkles, X, CheckCircle } from 'lucide-react';
import { useState } from 'react';

export interface Insight {
  id: string;
  title: string;
  description: string;
  insight_type: string;
  priority: 'high' | 'medium' | 'low';
  status: 'active' | 'dismissed' | 'completed';
  created_at: string;
  data?: Record<string, any>;
}

interface HeroInsightCardProps {
  insight: Insight;
  onDismiss?: (id: string) => void;
  onComplete?: (id: string) => void;
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

export default function HeroInsightCard({ insight, onDismiss, onComplete }: HeroInsightCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="relative fintech-card overflow-hidden"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${priorityColors[insight.priority]} opacity-5`} />

      {/* Content */}
      <div className="relative p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl bg-gradient-to-br ${priorityColors[insight.priority]}`}>
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-foreground">{insight.title}</h3>
                <span className={`px-2 py-0.5 text-xs font-bold rounded-full border ${priorityBadgeColors[insight.priority]}`}>
                  {insight.priority.toUpperCase()}
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
            {onComplete && insight.status === 'active' && (
              <button
                onClick={() => onComplete(insight.id)}
                className="p-2 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500/20 transition-colors"
                title="Mark as completed"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
            )}
            {onDismiss && (
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

        {/* Additional Data */}
        {insight.data && Object.keys(insight.data).length > 0 && (
          <div className="mt-4 p-4 rounded-lg bg-muted/30 border border-border">
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(insight.data).map(([key, value]) => (
                <div key={key}>
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p className="text-sm font-semibold text-foreground mt-0.5">
                    {typeof value === 'number' && key.includes('amount')
                      ? `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                      : String(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Gradient Bar */}
      <div className={`h-1 bg-gradient-to-r ${priorityColors[insight.priority]}`} />
    </div>
  );
}
