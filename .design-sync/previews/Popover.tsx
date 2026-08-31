import React from 'react';
import { Popover, PopoverTrigger, PopoverContent, Button } from 'cardora';

export const FilterPopover = () => (
  <div style={{ padding: 48, display: 'flex', justifyContent: 'center' }}>
    <Popover defaultOpen>
      <PopoverTrigger asChild>
        <Button variant="outline">Filter by category</Button>
      </PopoverTrigger>
      <PopoverContent style={{ width: 220 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Categories</div>
          {['Groceries', 'Food & Dining', 'Transport', 'Entertainment', 'Shopping'].map(cat => (
            <label key={cat} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, cursor: 'pointer' }}>
              <input type="checkbox" defaultChecked={cat === 'Groceries'} style={{ accentColor: 'var(--primary)' }} />
              {cat}
            </label>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  </div>
);
