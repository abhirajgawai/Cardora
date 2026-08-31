import React from 'react';
import { TimeRangeSelector } from 'cardora';

export const Default = () => (
  <div style={{ padding: 24 }}>
    <TimeRangeSelector value="last_3_months" onChange={() => {}} />
  </div>
);

export const AllOptions = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: 24 }}>
    <TimeRangeSelector value="last_month" onChange={() => {}} />
    <TimeRangeSelector value="last_3_months" onChange={() => {}} />
    <TimeRangeSelector value="last_6_months" onChange={() => {}} />
    <TimeRangeSelector value="this_year" onChange={() => {}} />
    <TimeRangeSelector value="all_time" onChange={() => {}} />
  </div>
);
