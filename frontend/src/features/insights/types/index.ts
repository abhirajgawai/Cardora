/**
 * Insights feature types — Payment alerts and debt payoff
 */

// Payment Alerts Types
export interface PaymentAlert {
  id: string;
  alert_type: string;
  title: string;
  description: string;
  due_date: string | null;
  amount: number | null;
  created_at: string;
  dismissed_at: string | null;
  data?: PaymentAlertData;
}

export interface PaymentAlertData {
  payment_status: string;
  severity: string;
  financial_summary: {
    amount_paid: number;
    previous_balance: number;
    revolving_balance: number;
    paid_percentage: number;
    minimum_payment: number;
  };
  interest_breakdown: {
    monthly_interest: number;
    annual_cost: number;
    apr: number;
  };
  recommendations: string[];
  educational_content: Record<string, unknown>;
}

export interface GetPaymentAlertsResponse {
  alerts: PaymentAlert[];
  count: number;
}

export interface GetCardPaymentAlertsResponse {
  card_id: string;
  card_name: string;
  alerts: PaymentAlert[];
  count: number;
}

export interface DismissPaymentAlertResponse {
  message: string;
  alert: {
    id: string;
    dismissed_at: string;
  };
}

export interface PayoffCalculation {
  input: {
    balance: number;
    apr: number;
    monthly_payment: number;
  };
  result: {
    months_to_payoff: number;
    total_interest_paid: number;
    total_amount_paid: number;
    payoff_date_estimate: string;
  };
}
