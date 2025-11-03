/**
 * Chart-specific type definitions for Recharts
 */

/**
 * Chart tooltip formatter return type
 */
export type ChartTooltipFormatter = [string, string];

/**
 * Chart value type (can be number or string from API)
 */
export type ChartValue = number | string;

/**
 * Generic chart data point
 */
export interface BaseChartData {
  [key: string]: ChartValue | string;
}

/**
 * Line chart data point
 */
export interface LineChartData extends BaseChartData {
  month: string;
  spending: number;
}

/**
 * Pie chart data point
 */
export interface PieChartData extends BaseChartData {
  name: string;
  value: number;
}

/**
 * Recharts tooltip props
 */
export interface ChartTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    name: string;
  }>;
  label?: string;
}
