'use client';

import { useState, useRef, useEffect } from 'react';

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
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function MonthYearPicker({ value, onChange, availableMonths }: MonthYearPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  const handleMonthYearSelect = (month: number, year: number) => {
    onChange({ month, year });
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange(null);
    setIsOpen(false);
  };

  const isMonthAvailable = (month: number, year: number) => {
    if (!availableMonths || availableMonths.length === 0) return true;
    return availableMonths.some(m => m.month === month && m.year === year);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2.5 bg-card border border-border rounded-lg text-sm font-medium text-foreground hover:bg-muted/50 transition-colors flex items-center gap-2"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        {value ? `${MONTHS[value.month - 1]} ${value.year}` : 'Select Month'}
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 right-0 bg-card border border-border rounded-lg shadow-lg z-50 overflow-hidden min-w-[320px]">
          <div className="p-3 border-b border-border flex items-center justify-between">
            <span className="text-sm font-semibold text-foreground">Select Month & Year</span>
            {value && (
              <button
                onClick={handleClear}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                Clear
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto p-2">
            {years.map(year => (
              <div key={year} className="mb-4 last:mb-0">
                <div className="px-2 py-1 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  {year}
                </div>
                <div className="grid grid-cols-3 gap-1">
                  {Array.from({ length: 12 }, (_, i) => i + 1).map(month => {
                    const available = isMonthAvailable(month, year);
                    const selected = value?.month === month && value?.year === year;

                    return (
                      <button
                        key={month}
                        onClick={() => available && handleMonthYearSelect(month, year)}
                        disabled={!available}
                        className={`
                          px-3 py-2 text-sm rounded-lg transition-all
                          ${selected
                            ? 'bg-primary text-white font-semibold'
                            : available
                              ? 'bg-muted/30 text-foreground hover:bg-muted/60'
                              : 'bg-muted/10 text-muted-foreground/40 cursor-not-allowed'
                          }
                        `}
                      >
                        {MONTHS[month - 1].slice(0, 3)}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
