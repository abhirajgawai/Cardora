"use client";

import { useTheme } from "@/shared/contexts/ThemeContext";
import { Moon, Sun } from "lucide-react";
import { motion } from "framer-motion";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative w-14 h-14 rounded-xl bg-muted hover:bg-muted/80 dark:bg-sidebar-accent dark:hover:bg-sidebar-accent/80 flex items-center justify-center transition-all duration-200 group overflow-hidden"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      {/* Background glow effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
      />

      {/* Icons container */}
      <div className="relative z-10 w-6 h-6">
        {/* Sun Icon - Show in dark mode */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          initial={false}
          animate={{
            scale: theme === "dark" ? 1 : 0,
            opacity: theme === "dark" ? 1 : 0,
            rotate: theme === "dark" ? 0 : 180,
          }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <Sun className="w-6 h-6 text-amber-500 dark:text-amber-400" />
        </motion.div>

        {/* Moon Icon - Show in light mode */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          initial={false}
          animate={{
            scale: theme === "light" ? 1 : 0,
            opacity: theme === "light" ? 1 : 0,
            rotate: theme === "light" ? 0 : -180,
          }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <Moon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
        </motion.div>
      </div>

      {/* Tooltip */}
      <motion.div
        className="absolute -bottom-10 left-1/2 -translate-x-1/2 px-3 py-1 bg-foreground text-background text-xs font-medium rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 z-20"
        initial={{ opacity: 0, y: -5 }}
        whileHover={{ opacity: 1, y: 0 }}
      >
        {theme === "light" ? "Dark mode" : "Light mode"}
        <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-foreground rotate-45" />
      </motion.div>
    </motion.button>
  );
}
