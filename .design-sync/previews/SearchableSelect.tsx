import React from 'react';
import { SearchableSelect } from 'cardora';

const CATEGORIES = [
  { value: 'groceries', label: 'Groceries' },
  { value: 'food', label: 'Food & Dining' },
  { value: 'transport', label: 'Transport' },
  { value: 'entertainment', label: 'Entertainment' },
  { value: 'shopping', label: 'Shopping' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'utilities', label: 'Utilities' },
];

export const CategoryFilter = () => (
  <div style={{ padding: 24, width: 260 }}>
    <SearchableSelect
      options={CATEGORIES}
      value=""
      onChange={() => {}}
      placeholder="Search categories..."
    />
  </div>
);

export const WithSelection = () => (
  <div style={{ padding: 24, width: 260 }}>
    <SearchableSelect
      options={CATEGORIES}
      value="food"
      onChange={() => {}}
      placeholder="Search categories..."
    />
  </div>
);
