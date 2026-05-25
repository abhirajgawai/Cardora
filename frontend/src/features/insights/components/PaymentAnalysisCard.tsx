'use client';

import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, DollarSign, Calendar, Percent } from 'lucide-react';
import { PaymentAlert } from '../types';

interface PaymentAnalysisCardProps {
  alert: PaymentAlert;
}

const statusConfig = {
  paid_full: {
    icon: CheckCircle,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    label: 'Paid in Full',
    emoji: '✓',
  },
  partial_paid: {
    icon: TrendingDown,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    label: 'Partial Payment',
    emoji: '⚠️',
  },
  minimum_paid: {
    icon: AlertTriangle,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    label: 'Minimum Payment Only',
    emoji: '⚠️',
  },
  late: {
    icon: AlertTriangle,
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    label: 'Payment Below Minimum',
    emoji: '🚨',
  },
  no_payment: {
    icon: AlertTriangle,
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    label: 'No Payment Detected',
    emoji: '🚨',
  },
};

export default function PaymentAnalysisCard({ alert }: PaymentAnalysisCardProps) {
  if (!alert.data) {
    return null;
  }

  const { financial_summary, interest_breakdown, recommendations, educational_content, payment_status } = alert.data;
  const config = statusConfig[payment_status as keyof typeof statusConfig] || statusConfig.partial_paid;
  const IconComponent = config.icon;
  const actionSteps = Array.isArray(educational_content?.action_steps)
    ? (educational_content.action_steps as string[])
    : Array.isArray(educational_content?.urgent_actions)
      ? (educational_content.urgent_actions as string[])
      : null;

  return (
    <div className={`fintech-card p-6 border-l-4 ${config.borderColor}`}>
      {/* Header */}
      <div className="flex items-start gap-4 mb-6">
        <div className={`p-3 rounded-xl ${config.bgColor} border ${config.borderColor}`}>
          <IconComponent className={`w-6 h-6 ${config.color}`} />
        </div>
        <div>
          <h3 className={`text-lg font-bold ${config.color} mb-1`}>
            {config.emoji} {alert.title}
          </h3>
          <p className="text-sm text-muted-foreground">
            {alert.description}
          </p>
        </div>
      </div>

      {/* Financial Summary Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className={`p-4 rounded-lg ${config.bgColor} border ${config.borderColor}`}>
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground uppercase tracking-wide">Amount Paid</span>
          </div>
          <p className="text-2xl font-bold text-foreground">
            ${financial_summary.amount_paid.toLocaleString()}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {financial_summary.paid_percentage.toFixed(1)}% of balance
          </p>
        </div>

        <div className={`p-4 rounded-lg ${config.bgColor} border ${config.borderColor}`}>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground uppercase tracking-wide">Revolving Balance</span>
          </div>
          <p className="text-2xl font-bold text-foreground">
            ${financial_summary.revolving_balance.toLocaleString()}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Carries to next month
          </p>
        </div>

        {interest_breakdown && (
          <>
            <div className={`p-4 rounded-lg ${config.bgColor} border ${config.borderColor}`}>
              <div className="flex items-center gap-2 mb-1">
                <Percent className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground uppercase tracking-wide">Monthly Interest</span>
              </div>
              <p className={`text-2xl font-bold ${config.color}`}>
                ${interest_breakdown.monthly_interest.toFixed(2)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                At {interest_breakdown.apr}% APR
              </p>
            </div>

            <div className={`p-4 rounded-lg ${config.bgColor} border ${config.borderColor}`}>
              <div className="flex items-center gap-2 mb-1">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground uppercase tracking-wide">Annual Cost</span>
              </div>
              <p className={`text-2xl font-bold ${config.color}`}>
                ${interest_breakdown.annual_cost.toFixed(2)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                If balance continues
              </p>
            </div>
          </>
        )}
      </div>

      {/* Educational Content */}
      {educational_content && Object.keys(educational_content).length > 0 && (
        <div className="mb-6 p-4 rounded-lg bg-muted/50 border border-border">
          <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            What This Means
          </h4>
          <div className="space-y-2">
            {typeof educational_content.debt_warning === 'string' && (
              <p className="text-sm text-foreground leading-relaxed">
                {educational_content.debt_warning}
              </p>
            )}
            {typeof educational_content.minimum_trap_explanation === 'string' && (
              <p className="text-sm text-muted-foreground leading-relaxed">
                {educational_content.minimum_trap_explanation}
              </p>
            )}
            {typeof educational_content.message === 'string' && (
              <p className="text-sm text-foreground leading-relaxed">
                {educational_content.message}
              </p>
            )}
            {typeof educational_content.interest_explanation === 'string' && (
              <p className="text-sm text-muted-foreground leading-relaxed">
                {educational_content.interest_explanation}
              </p>
            )}
          </div>

          {/* Action Steps */}
          {actionSteps && (
            <div className="mt-4">
              <h5 className="text-xs font-semibold text-foreground uppercase tracking-wide mb-2">
                Action Steps
              </h5>
              <ul className="space-y-1">
                {actionSteps.map((step, index) => (
                  <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                    <span className={`flex-shrink-0 w-5 h-5 rounded-full ${config.bgColor} ${config.color} flex items-center justify-center text-xs font-bold`}>
                      {index + 1}
                    </span>
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Payment Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-500" />
            Payment Recommendations
          </h4>
          <div className="space-y-2">
            {recommendations.map((rec, index) => (
              <div
                key={index}
                className="p-3 rounded-lg bg-green-500/5 border border-green-500/20 hover:bg-green-500/10 transition-colors"
              >
                <p className="text-sm text-foreground font-medium">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
