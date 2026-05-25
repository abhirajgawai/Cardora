import apiClient from '@/shared/lib/api/client';
import {
  GetPaymentAlertsResponse,
  GetCardPaymentAlertsResponse,
  DismissPaymentAlertResponse,
  PayoffCalculation
} from '../types';

export const getPaymentAlerts = async (includeDismissed: boolean = false): Promise<GetPaymentAlertsResponse> => {
  const response = await apiClient.get<GetPaymentAlertsResponse>('/insights/payment-alerts', {
    params: { include_dismissed: includeDismissed }
  });
  return response.data;
};

export const getCardPaymentAlerts = async (
  cardId: string,
  includeDismissed: boolean = false
): Promise<GetCardPaymentAlertsResponse> => {
  const response = await apiClient.get<GetCardPaymentAlertsResponse>(`/insights/payment-alerts/card/${cardId}`, {
    params: { include_dismissed: includeDismissed }
  });
  return response.data;
};

export const dismissPaymentAlert = async (alertId: string): Promise<DismissPaymentAlertResponse> => {
  const response = await apiClient.put<DismissPaymentAlertResponse>(`/insights/payment-alerts/${alertId}/dismiss`);
  return response.data;
};

export const calculatePayoff = async (
  balance: number,
  apr: number,
  monthlyPayment: number
): Promise<PayoffCalculation> => {
  const response = await apiClient.post<PayoffCalculation>('/insights/calculate-payoff', {
    balance,
    apr,
    monthly_payment: monthlyPayment
  });
  return response.data;
};
