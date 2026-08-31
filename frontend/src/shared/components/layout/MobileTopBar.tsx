"use client";

import Link from "next/link";
import { Menu, Moon, Sun } from "lucide-react";
import { useTheme } from "@/shared/contexts/ThemeContext";

interface MobileTopBarProps {
  onMenuClick: () => void;
}

const MobileTopBar = ({ onMenuClick }: MobileTopBarProps) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="lg:hidden fixed top-0 left-0 right-0 z-20 bg-card border-b border-border h-14 flex items-center justify-between px-4">
      <button
        onClick={onMenuClick}
        className="p-2 rounded-lg hover:bg-muted transition-colors"
        aria-label="Open navigation menu"
      >
        <Menu className="w-6 h-6 text-foreground" />
      </button>

      <Link href="/dashboard" className="text-lg font-bold text-primary tracking-tight">
        CARDORA
      </Link>

      <button
        onClick={toggleTheme}
        className="p-2 rounded-lg hover:bg-muted transition-colors"
        aria-label="Toggle theme"
      >
        {theme === "dark"
          ? <Sun className="w-5 h-5 text-amber-500" />
          : <Moon className="w-5 h-5 text-indigo-600" />
        }
      </button>
    </header>
  );
};

export default MobileTopBar;
