import React from 'react';
import { Calendar } from 'cardora';

export const StatementMonth = () => (
  <div style={{ padding: 24, display: 'inline-block' }}>
    <Calendar
      mode="single"
      selected={new Date(2025, 5, 15)}
      onSelect={() => {}}
    />
  </div>
);

export const RangePicker = () => (
  <div style={{ padding: 24, display: 'inline-block' }}>
    <Calendar
      mode="range"
      selected={{ from: new Date(2025, 5, 1), to: new Date(2025, 5, 14) }}
      onSelect={() => {}}
    />
  </div>
);
