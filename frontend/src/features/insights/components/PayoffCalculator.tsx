'use client';

import { useState } from 'react';
import { Calculator, TrendingUp, DollarSign, Calendar } from 'lucide-react';
import { calculatePayoff } from '../api/insightsApi';
import { PayoffCalculation } from '../types';

interface PayoffCalculatorProps {
  initialBalance: number;
  initialApr: number;
  initialPayment?: number;
}

export default function PayoffCalculator({
  initialBalance,
  initialApr,
  initialPayment = 0
}: PayoffCalculatorProps) {
  const [balance, setBalance] = useState(initialBalance);
  const [apr, setApr] = useState(initialApr);
  const [monthlyPayment, setMonthlyPayment] = useState(initialPayment || Math.round(initialBalance * 0.02));
  const [result, setResult] = useState<PayoffCalculation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async () => {
    try {
      setLoading(true);
      setError(null);
      const calculation = await calculatePayoff(balance, apr, monthlyPayment);
      setResult(calculation);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to calculate payoff');
    } finally {
      setLoading(false);
    }
  };

  const minMonthlyInterest = (balance * (apr / 12 / 100)).toFixed(2);

  return (
    <div className="fintech-card p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 rounded-lg bg-primary/10 border border-primary/20">
          <Calculator className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-foreground">Debt Payoff Calculator</h3>
          <p className="text-sm text-muted-foreground">See how different payments affect your timeline</p>
        </div>
      </div>

      {/* Input Fields */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Current Balance
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="number"
              value={balance}
              onChange={(e) => setBalance(parseFloat(e.target.value) || 0)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="0.00"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            APR (Annual Percentage Rate)
          </label>
          <div className="relative">
            <input
              type="number"
              value={apr}
              onChange={(e) => setApr(parseFloat(e.target.value) || 0)}
              step="0.01"
              className="w-full px-4 py-2.5 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="0.00"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">%</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Minimum interest per month: ${minMonthlyInterest}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Monthly Payment
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="number"
              value={monthlyPayment}
              onChange={(e) => setMonthlyPayment(parseFloat(e.target.value) || 0)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="0.00"
            />
          </div>
          <div className="mt-2 flex gap-2">
            <button
              onClick={() => setMonthlyPayment(Math.round(balance * 0.02))}
              className="text-xs px-3 py-1 rounded-md bg-muted hover:bg-muted/80 text-foreground transition-colors"
            >
              Min (2%)
            </button>
            <button
              onClick={() => setMonthlyPayment(Math.round(balance * 0.05))}
              className="text-xs px-3 py-1 rounded-md bg-muted hover:bg-muted/80 text-foreground transition-colors"
            >
              5%
            </button>
            <button
              onClick={() => setMonthlyPayment(Math.round(balance / 12))}
              className="text-xs px-3 py-1 rounded-md bg-muted hover:bg-muted/80 text-foreground transition-colors"
            >
              12 months
            </button>
          </div>
        </div>
      </div>

      {/* Calculate Button */}
      <button
        onClick={handleCalculate}
        disabled={loading || balance <= 0 || apr < 0 || monthlyPayment <= 0}
        className="w-full py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Calculating...' : 'Calculate Payoff'}
      </button>

      {/* Error */}
      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-500 text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {result && result.result && (
        <div className="mt-6 space-y-4">
          <div className="h-px bg-border" />

          <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-500" />
            Payoff Projection
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-muted/50 border border-border">
              <div className="flex items-center gap-2 mb-1">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground uppercase tracking-wide">Time to Pay Off</span>
              </div>
              <p className="text-2xl font-bold text-foreground">
                {result.result.months_to_payoff}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                months ({(result.result.months_to_payoff / 12).toFixed(1)} years)
              </p>
            </div>

            <div className="p-4 rounded-lg bg-muted/50 border border-border">
              <div className="flex items-center gap-2 mb-1">
                <DollarSign className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground uppercase tracking-wide">Total Interest</span>
              </div>
              <p className="text-2xl font-bold text-orange-500">
                ${result.result.total_interest_paid.toLocaleString()}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Interest paid
              </p>
            </div>

            <div className="p-4 rounded-lg bg-muted/50 border border-border">
              <div className="flex items-center gap-2 mb-1">
                <DollarSign className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground uppercase tracking-wide">Total Paid</span>
              </div>
              <p className="text-2xl font-bold text-foreground">
                ${result.result.total_amount_paid.toLocaleString()}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Principal + Interest
              </p>
            </div>
          </div>

          {/* Insight */}
          <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
            <p className="text-sm text-foreground">
              <span className="font-semibold">💡 Tip:</span> By paying ${monthlyPayment} per month,
              you'll be debt-free in <span className="font-bold">{result.result.months_to_payoff} months</span>.
              Try increasing your payment to see how much interest you can save!
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
