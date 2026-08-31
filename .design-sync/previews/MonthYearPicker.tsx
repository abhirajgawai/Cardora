import React from 'react';
import { MonthYearPicker } from 'cardora';

export const WithValue = () => (
  <div style={{ padding: 24 }}>
    <MonthYearPicker
      value={{ month: 5, year: 2025 }}
      onChange={() => {}}
    />
  </div>
);

export const Empty = () => (
  <div style={{ padding: 24 }}>
    <MonthYearPicker
      value={null}
      onChange={() => {}}
    />
  </div>
);

export const WithAvailableMonths = () => (
  <div style={{ padding: 24 }}>
    <MonthYearPicker
      value={{ month: 3, year: 2025 }}
      onChange={() => {}}
      availableMonths={[
        { month: 1, year: 2025 },
        { month: 2, year: 2025 },
        { month: 3, year: 2025 },
        { month: 4, year: 2025 },
        { month: 5, year: 2025 },
      ]}
    />
  </div>
);
