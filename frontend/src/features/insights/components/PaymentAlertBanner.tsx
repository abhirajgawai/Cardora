'use client';

import { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, AlertCircle, X, ChevronRight } from 'lucide-react';
import { PaymentAlert } from '../types';
import { getPaymentAlerts, dismissPaymentAlert } from '../api/insightsApi';

interface PaymentAlertBannerProps {
  onAlertClick?: (alert: PaymentAlert) => void;
}

const severityConfig = {
  critical: {
    icon: AlertTriangle,
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    textColor: 'text-red-500',
    dotColor: 'bg-red-500',
  },
  high: {
    icon: AlertCircle,
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    textColor: 'text-orange-500',
    dotColor: 'bg-orange-500',
  },
  medium: {
    icon: AlertCircle,
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    textColor: 'text-yellow-600',
    dotColor: 'bg-yellow-500',
  },
  low: {
    icon: CheckCircle,
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    textColor: 'text-green-500',
    dotColor: 'bg-green-500',
  },
};

export default function PaymentAlertBanner({ onAlertClick }: PaymentAlertBannerProps) {
  const [alerts, setAlerts] = useState<PaymentAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [dismissingId, setDismissingId] = useState<string | null>(null);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const response = await getPaymentAlerts(false);
      // Show only the top 3 most recent alerts
      setAlerts(response.alerts.slice(0, 3));
    } catch (error) {
      console.error('Failed to load payment alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = async (alertId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setDismissingId(alertId);
      await dismissPaymentAlert(alertId);
      setAlerts((prev) => prev.filter((alert) => alert.id !== alertId));
    } catch (error) {
      console.error('Failed to dismiss alert:', error);
    } finally {
      setDismissingId(null);
    }
  };

  if (loading) {
    return null; // Or a loading skeleton
  }

  if (alerts.length === 0) {
    return null; // No alerts to show
  }

  return (
    <div className="space-y-3 mb-6">
      {alerts.map((alert) => {
        const severity = alert.data?.severity || 'medium';
        const config = severityConfig[severity as keyof typeof severityConfig] || severityConfig.medium;
        const IconComponent = config.icon;

        return (
          <div
            key={alert.id}
            className={`fintech-card p-4 border-l-4 ${config.borderColor} ${config.bgColor} cursor-pointer hover:shadow-md transition-all`}
            onClick={() => onAlertClick?.(alert)}
          >
            <div className="flex items-start gap-4">
              {/* Icon */}
              <div className={`p-2 rounded-lg ${config.bgColor} border ${config.borderColor} flex-shrink-0`}>
                <IconComponent className={`w-5 h-5 ${config.textColor}`} />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3 mb-1">
                  <h4 className="text-sm font-semibold text-foreground">
                    {alert.title}
                  </h4>

                  {/* Dismiss button */}
                  <button
                    onClick={(e) => handleDismiss(alert.id, e)}
                    disabled={dismissingId === alert.id}
                    className="p-1 rounded-lg hover:bg-background/50 transition-colors flex-shrink-0"
                    title="Dismiss alert"
                  >
                    <X className="w-4 h-4 text-muted-foreground" />
                  </button>
                </div>

                <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
                  {alert.description}
                </p>

                {/* Financial Summary */}
                {alert.data?.financial_summary && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Amount Paid</span>
                      <span className="text-sm font-semibold text-foreground">
                        ${alert.data.financial_summary.amount_paid.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Balance</span>
                      <span className="text-sm font-semibold text-foreground">
                        ${alert.data.financial_summary.revolving_balance.toLocaleString()}
                      </span>
                    </div>
                    {alert.data.interest_breakdown && (
                      <>
                        <div className="flex flex-col">
                          <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Monthly Interest</span>
                          <span className={`text-sm font-semibold ${config.textColor}`}>
                            ${alert.data.interest_breakdown.monthly_interest.toFixed(2)}
                          </span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Annual Cost</span>
                          <span className={`text-sm font-semibold ${config.textColor}`}>
                            ${alert.data.interest_breakdown.annual_cost.toFixed(2)}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                )}

                {/* View Details Link */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onAlertClick?.(alert);
                  }}
                  className={`flex items-center gap-1 text-xs ${config.textColor} hover:underline`}
                >
                  View recommendations
                  <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
