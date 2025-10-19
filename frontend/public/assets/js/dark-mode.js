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

  // Dark mode color palette (Notion/Excel professional style)
  const darkStyles = `
    .dark-mode {
      /* New professional color palette - Notion/Excel style */
      --bg-primary: #0d0d0d;
      --bg-secondary: #191919;
      --bg-tertiary: #202020;
      --bg-elevated: #2a2a2a;
      --text-primary: #e6e6e6;
      --text-secondary: #9b9b9b;
      --text-tertiary: #6b6b6b;
      --border-default: #333333;
      --border-hover: #404040;
      --accent: #00d4ff;
      --accent-hover: #00b8e6;
      --accent-bg: rgba(0, 212, 255, 0.08);

      /* Override default CSS variables for compatibility */
      --color-white: #0d0d0d;
      --color-gray-50: #191919;
      --color-gray-100: #202020;
      --color-gray-200: #2a2a2a;
      --color-gray-300: #333333;
      --color-gray-400: #6b6b6b;
      --color-gray-500: #9b9b9b;
      --color-gray-600: #e6e6e6;
      --color-gray-700: #e6e6e6;
      --color-gray-800: #e6e6e6;
      --color-gray-900: #ffffff;
      --color-primary: #ffffff;
      --color-accent: #00d4ff;
      --color-accent-hover: #00b8e6;

      background-color: #0d0d0d;
      color: #e6e6e6;
    }

    /* Base styles */
    .dark-mode body {
      background-color: #0d0d0d !important;
      color: #e6e6e6 !important;
    }

    /* Navbar - fondo #191919 con bordes sutiles */
    .dark-mode .header,
    .dark-mode .navbar,
    .dark-mode nav {
      background-color: #191919 !important;
      border-bottom: 1px solid #333333 !important;
    }

    /* Nav links - gris secundario con hover a texto primario */
    .dark-mode .nav-link {
      color: #9b9b9b !important;
    }

    .dark-mode .nav-link:hover {
      color: #e6e6e6 !important;
      background-color: rgba(255, 255, 255, 0.05) !important;
    }

    .dark-mode .nav-link.active {
      background-color: #00d4ff !important;
      color: #0d0d0d !important;
    }

    /* Sign In button - mantener cyan con texto oscuro */
    .dark-mode .btn-primary,
    .dark-mode .btn-login,
    .dark-mode .btn-signup {
      background-color: #00d4ff !important;
      color: #0d0d0d !important;
      border-color: #00d4ff !important;
    }

    .dark-mode .btn-primary:hover,
    .dark-mode .btn-login:hover:not(:disabled),
    .dark-mode .btn-signup:hover:not(:disabled) {
      background-color: #00b8e6 !important;
      border-color: #00b8e6 !important;
    }

    /* Secondary buttons */
    .dark-mode .btn-secondary,
    .dark-mode .btn-logout {
      background-color: #202020 !important;
      border-color: #333333 !important;
      color: #e6e6e6 !important;
    }

    .dark-mode .btn-secondary:hover {
      background-color: #2a2a2a !important;
      border-color: #404040 !important;
    }

    /* Cards, Sidebar, Forms */
    .dark-mode .login-brand,
    .dark-mode .signup-brand,
    .dark-mode .sidebar,
    .dark-mode .card,
    .dark-mode .container,
    .dark-mode .box {
      background-color: #202020 !important;
      border-color: #333333 !important;
    }

    .dark-mode .login-form,
    .dark-mode .signup-form,
    .dark-mode .section,
    .dark-mode .stat-card {
      background-color: #202020 !important;
      border-color: #333333 !important;
    }

    /* Hover states for cards */
    .dark-mode .card:hover,
    .dark-mode .box:hover {
      background-color: #2a2a2a !important;
      border-color: #404040 !important;
    }

    /* Form inputs */
    .dark-mode .form-input,
    .dark-mode input,
    .dark-mode select,
    .dark-mode textarea {
      background-color: #191919 !important;
      border-color: #333333 !important;
      color: #e6e6e6 !important;
    }

    .dark-mode .form-input:focus,
    .dark-mode input:focus,
    .dark-mode select:focus,
    .dark-mode textarea:focus {
      background-color: #191919 !important;
      border-color: #00d4ff !important;
      box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.08) !important;
      color: #ffffff !important;
    }

    .dark-mode .form-input::placeholder,
    .dark-mode input::placeholder,
    .dark-mode textarea::placeholder {
      color: #6b6b6b !important;
    }

    /* Labels */
    .dark-mode label,
    .dark-mode .form-label {
      color: #e6e6e6 !important;
    }

    /* Alerts */
    .dark-mode .alert-error,
    .dark-mode .error {
      background-color: #7F1D1D !important;
      border-color: #991B1B !important;
      color: #FEE2E2 !important;
    }

    .dark-mode .alert-success {
      background-color: #065F46 !important;
      border-color: #059669 !important;
      color: #D1FAE5 !important;
    }

    /* Typography - headings always white */
    .dark-mode h1,
    .dark-mode h2,
    .dark-mode h3,
    .dark-mode h4,
    .dark-mode h5,
    .dark-mode h6,
    .dark-mode .hero-title,
    .dark-mode .section-title {
      color: #ffffff !important;
    }

    /* Text - primary gray */
    .dark-mode p,
    .dark-mode li,
    .dark-mode td,
    .dark-mode th,
    .dark-mode span,
    .dark-mode div {
      color: #e6e6e6 !important;
    }

    /* Secondary text (descriptions, captions) */
    .dark-mode .text-secondary,
    .dark-mode .description,
    .dark-mode .caption,
    .dark-mode small {
      color: #9b9b9b !important;
    }

    /* Links - cyan accent */
    .dark-mode a {
      color: #00d4ff !important;
    }

    .dark-mode a:hover {
      color: #00b8e6 !important;
    }

    /* Content containers */
    .dark-mode .content,
    .dark-mode .content-container,
    .dark-mode .main-content,
    .dark-mode .policy-content,
    .dark-mode article {
      background-color: #202020 !important;
      color: #e6e6e6 !important;
    }

    /* Header already defined above with navbar */

    /* Footer */
    .dark-mode .footer {
      background-color: #191919 !important;
      border-top: 1px solid #333333 !important;
    }

    /* Strong/bold text - slightly lighter */
    .dark-mode strong,
    .dark-mode b {
      color: #ffffff !important;
    }

    /* Tables */
    .dark-mode table {
      border-color: #333333 !important;
      background-color: #202020 !important;
    }

    .dark-mode thead,
    .dark-mode th {
      background-color: #191919 !important;
      color: #e6e6e6 !important;
      border-color: #333333 !important;
    }

    .dark-mode tbody tr {
      border-bottom: 1px solid #333333 !important;
    }

    .dark-mode tbody tr:hover {
      background-color: rgba(255, 255, 255, 0.05) !important;
    }

    /* Code blocks */
    .dark-mode code,
    .dark-mode pre {
      background-color: #191919 !important;
      color: #00d4ff !important;
      border: 1px solid #333333 !important;
    }

    /* CHECKOUT PAGE */
    .dark-mode .checkout-container {
      background-color: #0d0d0d !important;
    }

    .dark-mode .plan-details {
      background-color: #202020 !important;
      border-color: #333333 !important;
    }

    .dark-mode .plan-name {
      color: #ffffff !important;
    }

    .dark-mode .plan-price {
      color: #00d4ff !important;
    }

    .dark-mode .plan-billing {
      color: #9b9b9b !important;
    }

    .dark-mode .loading {
      color: #e6e6e6 !important;
    }

    /* DISABLED STATES */
    .dark-mode .btn:disabled,
    .dark-mode button:disabled {
      background-color: #2a2a2a !important;
      color: #6b6b6b !important;
      border-color: #333333 !important;
      cursor: not-allowed !important;
    }

    /* LANGUAGE SWITCHER BUTTONS */
    .dark-mode .lang-btn,
    .dark-mode .language-btn {
      background-color: #202020 !important;
      color: #9b9b9b !important;
      border-color: #333333 !important;
    }

    .dark-mode .lang-btn:hover,
    .dark-mode .language-btn:hover {
      background-color: #2a2a2a !important;
      color: #e6e6e6 !important;
      border-color: #404040 !important;
    }

    .dark-mode .lang-btn.active,
    .dark-mode .language-btn.active {
      background-color: #00d4ff !important;
      color: #0d0d0d !important;
      border-color: #00d4ff !important;
    }

    /* LOGO TEXT */
    .dark-mode .logo {
      color: #ffffff !important;
    }

    /* HERO SECTIONS */
    .dark-mode .hero,
    .dark-mode .hero-section {
      background-color: #0d0d0d !important;
    }

    .dark-mode .hero-description,
    .dark-mode .hero-subtitle {
      color: #9b9b9b !important;
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
