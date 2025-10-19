/**
 * TranslateCloud - Dark Mode Toggle
 *
 * Professional dark mode system for developers
 * - Toggle button in header
 * - Persists preference in localStorage
 * - Smooth transitions
 * - Enterprise-grade dark theme
 *
 * @version 1.0.0
 * @author TranslateCloud
 */

const DarkMode = (() => {
  const STORAGE_KEY = 'translatecloud_dark_mode';
  const DARK_CLASS = 'dark-mode';

  // Dark mode color palette (enterprise-grade)
  const darkStyles = `
    .dark-mode {
      --color-white: #0F172A;
      --color-gray-50: #1E293B;
      --color-gray-100: #334155;
      --color-gray-200: #475569;
      --color-gray-300: #64748B;
      --color-gray-400: #94A3B8;
      --color-gray-500: #CBD5E1;
      --color-gray-600: #E2E8F0;
      --color-gray-700: #F1F5F9;
      --color-gray-800: #F8FAFC;
      --color-gray-900: #FFFFFF;
      --color-primary: #FFFFFF;
      --color-accent: #38BDF8;
      --color-accent-hover: #0EA5E9;

      background-color: #0F172A;
      color: #FFFFFF;
    }

    .dark-mode .login-brand,
    .dark-mode .signup-brand,
    .dark-mode .sidebar {
      background-color: #1E293B;
      border-color: #334155;
    }

    .dark-mode .login-form,
    .dark-mode .signup-form,
    .dark-mode .section,
    .dark-mode .stat-card {
      background-color: #1E293B;
      border-color: #334155;
    }

    .dark-mode .form-input,
    .dark-mode select,
    .dark-mode textarea {
      background-color: #0F172A;
      border-color: #475569;
      color: #FFFFFF;
    }

    .dark-mode .form-input:focus {
      border-color: #38BDF8;
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1);
    }

    .dark-mode .btn-primary,
    .dark-mode .btn-login,
    .dark-mode .btn-signup {
      background-color: #38BDF8;
      color: #0F172A;
    }

    .dark-mode .btn-primary:hover,
    .dark-mode .btn-login:hover:not(:disabled),
    .dark-mode .btn-signup:hover:not(:disabled) {
      background-color: #0EA5E9;
    }

    .dark-mode .btn-secondary,
    .dark-mode .btn-logout {
      background-color: #1E293B;
      border-color: #475569;
      color: #F1F5F9;
    }

    .dark-mode .alert-error {
      background-color: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.3);
    }

    .dark-mode .alert-success {
      background-color: rgba(16, 185, 129, 0.1);
      border-color: rgba(16, 185, 129, 0.3);
    }

    .dark-mode .nav-link:hover {
      background-color: #334155;
    }

    .dark-mode .nav-link.active {
      background-color: #38BDF8;
      color: #0F172A;
    }

    /* Fix policy pages and content pages */
    .dark-mode body {
      background-color: #0F172A;
      color: #E2E8F0;
    }

    .dark-mode h1,
    .dark-mode h2,
    .dark-mode h3,
    .dark-mode h4,
    .dark-mode h5,
    .dark-mode h6 {
      color: #FFFFFF;
    }

    .dark-mode p,
    .dark-mode li,
    .dark-mode td,
    .dark-mode th,
    .dark-mode span,
    .dark-mode div {
      color: #CBD5E1;
    }

    .dark-mode a {
      color: #38BDF8;
    }

    .dark-mode a:hover {
      color: #0EA5E9;
    }

    .dark-mode .content,
    .dark-mode .content-container,
    .dark-mode .main-content,
    .dark-mode .policy-content,
    .dark-mode article {
      background-color: #1E293B;
      color: #E2E8F0;
    }

    .dark-mode .header {
      background-color: #1E293B;
      border-bottom-color: #334155;
    }

    .dark-mode .footer {
      background-color: #1E293B;
      border-top-color: #334155;
    }

    .dark-mode strong,
    .dark-mode b {
      color: #F1F5F9;
    }

    .dark-mode table {
      border-color: #475569;
    }

    .dark-mode thead {
      background-color: #334155;
    }

    .dark-mode tbody tr {
      border-bottom-color: #475569;
    }

    .dark-mode code,
    .dark-mode pre {
      background-color: #0F172A;
      color: #38BDF8;
      border-color: #475569;
    }

    /* CHECKOUT PAGE FIXES */
    .dark-mode .checkout-container {
      background-color: #0F172A !important;
    }

    .dark-mode .plan-details {
      background-color: #1E293B !important;
      border-color: #334155 !important;
    }

    .dark-mode .plan-name {
      color: #FFFFFF !important;
    }

    .dark-mode .plan-price {
      color: #38BDF8 !important;
    }

    .dark-mode .plan-billing {
      color: #94A3B8 !important;
    }

    .dark-mode .loading {
      color: #E2E8F0 !important;
    }

    /* ERROR/ALERT STATES - CRITICAL FIX */
    .dark-mode .error,
    .dark-mode .alert-error {
      background-color: #7F1D1D !important;
      border-color: #991B1B !important;
      color: #FEE2E2 !important;
    }

    .dark-mode .alert-success {
      background-color: #065F46 !important;
      border-color: #059669 !important;
      color: #D1FAE5 !important;
    }

    /* DISABLED STATES */
    .dark-mode .btn:disabled,
    .dark-mode button:disabled {
      background-color: #475569 !important;
      color: #94A3B8 !important;
      cursor: not-allowed !important;
    }

    /* INPUTS AND FORMS */
    .dark-mode input,
    .dark-mode select,
    .dark-mode textarea {
      background-color: #0F172A !important;
      border-color: #475569 !important;
      color: #E2E8F0 !important;
    }

    .dark-mode input::placeholder,
    .dark-mode textarea::placeholder {
      color: #64748B !important;
    }

    .dark-mode label {
      color: #E2E8F0 !important;
    }

    /* CARDS AND CONTAINERS */
    .dark-mode .card,
    .dark-mode .container,
    .dark-mode .box {
      background-color: #1E293B !important;
      border-color: #334155 !important;
    }

    * {
      transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }
  `;

  /**
   * Initialize dark mode
   */
  function init() {
    // Inject styles
    injectStyles();

    // Check saved preference
    const savedMode = localStorage.getItem(STORAGE_KEY);
    if (savedMode === 'dark') {
      enable();
    }

    // Create toggle button
    createToggleButton();
  }

  /**
   * Inject dark mode styles into document
   */
  function injectStyles() {
    const styleElement = document.createElement('style');
    styleElement.id = 'dark-mode-styles';
    styleElement.textContent = darkStyles;
    document.head.appendChild(styleElement);
  }

  /**
   * Create floating toggle button
   */
  function createToggleButton() {
    const button = document.createElement('button');
    button.id = 'dark-mode-toggle';
    button.setAttribute('aria-label', 'Toggle dark mode');
    button.setAttribute('title', 'Toggle dark mode (for developers)');
    button.innerHTML = `
      <svg class="sun-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      </svg>
      <svg class="moon-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none;">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
      </svg>
    `;

    // Styles for toggle button
    button.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background-color: #111827;
      color: #FFFFFF;
      border: 1px solid #E5E7EB;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      z-index: 9999;
      font-family: inherit;
    `;

    // Hover effect
    button.addEventListener('mouseenter', () => {
      button.style.transform = 'scale(1.1)';
      button.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
    });

    button.addEventListener('mouseleave', () => {
      button.style.transform = 'scale(1)';
      button.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
    });

    // Click handler
    button.addEventListener('click', toggle);

    // Add to document
    document.body.appendChild(button);

    // Update icon based on current mode
    updateToggleIcon();
  }

  /**
   * Enable dark mode
   */
  function enable() {
    document.documentElement.classList.add(DARK_CLASS);
    localStorage.setItem(STORAGE_KEY, 'dark');
    updateToggleIcon();
    updateToggleButtonStyle();
  }

  /**
   * Disable dark mode
   */
  function disable() {
    document.documentElement.classList.remove(DARK_CLASS);
    localStorage.setItem(STORAGE_KEY, 'light');
    updateToggleIcon();
    updateToggleButtonStyle();
  }

  /**
   * Toggle dark mode
   */
  function toggle() {
    if (isEnabled()) {
      disable();
    } else {
      enable();
    }
  }

  /**
   * Check if dark mode is enabled
   * @returns {boolean}
   */
  function isEnabled() {
    return document.documentElement.classList.contains(DARK_CLASS);
  }

  /**
   * Update toggle button icon
   */
  function updateToggleIcon() {
    const button = document.getElementById('dark-mode-toggle');
    if (!button) return;

    const sunIcon = button.querySelector('.sun-icon');
    const moonIcon = button.querySelector('.moon-icon');

    if (isEnabled()) {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
    } else {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
    }
  }

  /**
   * Update toggle button background color
   */
  function updateToggleButtonStyle() {
    const button = document.getElementById('dark-mode-toggle');
    if (!button) return;

    if (isEnabled()) {
      button.style.backgroundColor = '#38BDF8';
      button.style.color = '#0F172A';
      button.style.borderColor = '#0EA5E9';
    } else {
      button.style.backgroundColor = '#111827';
      button.style.color = '#FFFFFF';
      button.style.borderColor = '#E5E7EB';
    }
  }

  /**
   * Get current mode
   * @returns {string} 'dark' or 'light'
   */
  function getMode() {
    return isEnabled() ? 'dark' : 'light';
  }

  // Public API
  return {
    init,
    enable,
    disable,
    toggle,
    isEnabled,
    getMode,
  };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', DarkMode.init);
} else {
  DarkMode.init();
}

// Export for ES6 modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DarkMode;
}
