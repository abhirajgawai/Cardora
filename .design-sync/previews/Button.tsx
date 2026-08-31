import React from 'react';
import { Button } from 'cardora';

export const Variants = () => (
  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, padding: 24 }}>
    <Button>Pay Now</Button>
    <Button variant="secondary">Save Draft</Button>
    <Button variant="outline">Export CSV</Button>
    <Button variant="destructive">Delete Card</Button>
    <Button variant="ghost">View Details</Button>
    <Button variant="link">Learn more</Button>
  </div>
);

export const Sizes = () => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 24 }}>
    <Button size="sm">Small</Button>
    <Button size="default">Default</Button>
    <Button size="lg">Large</Button>
  </div>
);

export const States = () => (
  <div style={{ display: 'flex', gap: 12, padding: 24 }}>
    <Button>Active</Button>
    <Button disabled>Disabled</Button>
  </div>
);
