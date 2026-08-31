import React from 'react';
import { Progress } from 'cardora';

export const Values = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 16, padding: 24, width: 320 }}>
    <div>
      <div style={{ fontSize: 12, color: '#64748B', marginBottom: 6 }}>25% — Low spend</div>
      <Progress value={25} />
    </div>
    <div>
      <div style={{ fontSize: 12, color: '#64748B', marginBottom: 6 }}>60% — Moderate spend</div>
      <Progress value={60} />
    </div>
    <div>
      <div style={{ fontSize: 12, color: '#64748B', marginBottom: 6 }}>85% — Near limit</div>
      <Progress value={85} />
    </div>
    <div>
      <div style={{ fontSize: 12, color: '#64748B', marginBottom: 6 }}>100% — Limit reached</div>
      <Progress value={100} />
    </div>
  </div>
);

export const Empty = () => (
  <div style={{ padding: 24, width: 320 }}>
    <Progress value={0} />
  </div>
);
