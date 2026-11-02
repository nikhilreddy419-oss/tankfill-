/**
 * TankFill Theme Management Script
 * Handles Dark/Light Mode switching, persistence in localStorage,
 * and notifies active components (such as Chart.js) of theme shifts.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'tankfill_theme_preference';
  const rootElement = document.documentElement;

  /**
   * Determine preferred initial theme.
   * Priority: localStorage -> system preference -> default 'light'
   */
  function getPreferredTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') {
      return saved;
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Apply specified theme to the document.
   * @param {string} theme - 'dark' or 'light'
   */
  function applyTheme(theme) {
    rootElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);

    // Update button ARIA attributes
    const toggleBtn = document.getElementById('themeToggleBtn');
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
      toggleBtn.setAttribute('title', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }

    // Dispatch custom event for Chart.js and other dynamic visualizers
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
  }

  /**
   * Toggle between dark and light modes.
   */
  function toggleTheme() {
    const current = rootElement.getAttribute('data-theme') || 'light';
    const nextTheme = current === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  }

  // Initialize theme immediately on script execution to prevent FOUC (flash of unstyled content)
  const initialTheme = getPreferredTheme();
  applyTheme(initialTheme);

  // Attach event listener once DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('themeToggleBtn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', toggleTheme);
    }

    // Listen for OS color scheme alterations if user hasn't explicitly set preference
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem(STORAGE_KEY)) {
          applyTheme(e.matches ? 'dark' : 'light');
        }
      });
    }
  });

  // Expose helper globally
  window.TankFillTheme = {
    getTheme: () => rootElement.getAttribute('data-theme') || 'light',
    applyTheme,
    toggleTheme,
  };
})();
