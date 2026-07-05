/**
 * Cardora brand color palette — used for charts and data visualisations.
 * Import from here so all charts stay visually consistent.
 */

export const CHART_COLORS = [
  '#4B6EF5', // Modern Indigo — primary brand
  '#00E0A1', // Teal Mint — accent
  '#F59E0B', // Amber — warning / highlight
  '#10B981', // Emerald — success
  '#8B5CF6', // Purple — secondary
  '#60A5FA', // Sky Blue — supplementary
  '#FB923C', // Coral — warm accent
  '#64748B', // Slate — neutral
  '#1E1B4B', // Deep Navy
  '#E2E8F0', // Light Gray — subtle
] as const;

/** Named aliases for the most commonly referenced colours. */
export const BRAND_COLORS = {
  primary: '#4B6EF5',
  accent:  '#00E0A1',
  navy:    '#1E1B4B',
  slate:   '#64748B',
} as const;
