import React from 'react';
import {
  Select, SelectTrigger, SelectValue, SelectContent,
  SelectGroup, SelectLabel, SelectItem, SelectSeparator
} from 'cardora';

export const Default = () => (
  <div style={{ padding: 24 }}>
    <Select>
      <SelectTrigger style={{ width: 220 }}>
        <SelectValue placeholder="Select time range" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Quick ranges</SelectLabel>
          <SelectItem value="last_month">Last month</SelectItem>
          <SelectItem value="last_3">Last 3 months</SelectItem>
          <SelectItem value="last_6">Last 6 months</SelectItem>
          <SelectSeparator />
          <SelectItem value="ytd">Year to date</SelectItem>
          <SelectItem value="all">All time</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  </div>
);

export const WithValue = () => (
  <div style={{ padding: 24 }}>
    <Select defaultValue="last_3">
      <SelectTrigger style={{ width: 220 }}>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="last_month">Last month</SelectItem>
        <SelectItem value="last_3">Last 3 months</SelectItem>
        <SelectItem value="last_6">Last 6 months</SelectItem>
      </SelectContent>
    </Select>
  </div>
);
