/**
 * ThemeContext.jsx
 * ──────────────────────────────────────────────────────────────
 * Provides dark/light theme state + toggle to the whole app.
 * - Defaults to dark mode (or respects localStorage)
 * - Applies 'light' class to <html> for CSS var switching
 * - Exports useTheme() hook
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const ThemeContext = createContext({ isDark: true, toggleTheme: () => {} });

export function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(() => {
    // 1. Respect user's saved preference
    const saved = localStorage.getItem('bu3d-theme');
    if (saved) return saved === 'dark';
    // 2. Respect OS preference — but default to dark for this brand
    return true;
  });

  // Apply / remove 'light' class on <html>
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.remove('light');
    } else {
      root.classList.add('light');
    }
    localStorage.setItem('bu3d-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = useCallback(() => setIsDark((v) => !v), []);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
