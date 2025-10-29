'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { CalendarIcon, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

export interface MonthYearValue {
  month: number;
  year: number;
}

interface MonthYearPickerProps {
  value: MonthYearValue | null;
  onChange: (value: MonthYearValue | null) => void;
  availableMonths?: MonthYearValue[];
}

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function MonthYearPicker({ value, onChange, availableMonths }: MonthYearPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  const handleMonthYearSelect = (month: number, year: number) => {
    onChange({ month, year });
    setIsOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(null);
  };

  const isMonthAvailable = (month: number, year: number) => {
    if (!availableMonths || availableMonths.length === 0) return true;
    return availableMonths.some(m => m.month === month && m.year === year);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "justify-start text-left font-normal h-10 transition-all",
            !value && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {value ? `${MONTH_NAMES[value.month - 1]} ${value.year}` : 'Select Month'}
          {value && (
            <X
              className="ml-auto h-4 w-4 opacity-50 hover:opacity-100 transition-opacity"
              onClick={handleClear}
            />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent
        className="w-[320px] p-0"
        align="center"
        side="bottom"
        sideOffset={8}
        collisionPadding={16}
      >
        <div className="p-3">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-sm text-foreground">Select Month & Year</h4>
            {value && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  onChange(null);
                  setIsOpen(false);
                }}
                className="h-7 text-xs px-2"
              >
                Clear
              </Button>
            )}
          </div>
          <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
            {years.map(year => (
              <div key={year}>
                <div className="px-1 py-1 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  {year}
                </div>
                <div className="grid grid-cols-3 gap-1.5">
                  {Array.from({ length: 12 }, (_, i) => i + 1).map(month => {
                    const available = isMonthAvailable(month, year);
                    const selected = value?.month === month && value?.year === year;

                    return (
                      <Button
                        key={month}
                        onClick={() => available && handleMonthYearSelect(month, year)}
                        disabled={!available}
                        variant={selected ? "default" : "outline"}
                        size="sm"
                        className={cn(
                          "h-8 text-xs transition-all",
                          !available && "opacity-40 cursor-not-allowed",
                          selected && "bg-primary text-primary-foreground font-semibold",
                          !selected && available && "hover:bg-accent hover:text-accent-foreground"
                        )}
                      >
                        {MONTHS[month - 1]}
                      </Button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
