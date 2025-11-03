'use client';

import { CalendarIcon, Clock } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/components/ui/select';

export type TimeRange = 'last_month' | 'last_3_months' | 'last_6_months' | 'this_year' | 'all_time';

interface TimeRangeOption {
  value: TimeRange;
  label: string;
  description: string;
  icon?: string;
}

interface TimeRangeSelectorProps {
  value: TimeRange;
  onChange: (range: TimeRange) => void;
}

const timeRangeOptions: TimeRangeOption[] = [
  {
    value: 'last_month',
    label: 'Last Month',
    description: 'Current month data',
    icon: '📅',
  },
  {
    value: 'last_3_months',
    label: 'Last 3 Months',
    description: 'Quarterly view',
    icon: '📊',
  },
  {
    value: 'last_6_months',
    label: 'Last 6 Months',
    description: 'Half-year view',
    icon: '📈',
  },
  {
    value: 'this_year',
    label: 'This Year',
    description: 'Year-to-date',
    icon: '🗓️',
  },
  {
    value: 'all_time',
    label: 'All Time',
    description: 'Complete history',
    icon: '🌐',
  },
];

export default function TimeRangeSelector({ value, onChange }: TimeRangeSelectorProps) {
  const selectedOption = timeRangeOptions.find((opt) => opt.value === value);

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[200px] h-10">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          <SelectValue>
            {selectedOption?.label}
          </SelectValue>
        </div>
      </SelectTrigger>
      <SelectContent>
        {timeRangeOptions.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            <div className="flex items-start gap-3 py-1">
              <span className="text-lg leading-none mt-0.5">{option.icon}</span>
              <div className="flex flex-col gap-0.5">
                <span className="font-medium">{option.label}</span>
                <span className="text-xs text-muted-foreground">{option.description}</span>
              </div>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
