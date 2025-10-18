/**
 * TranslateCloud - Authentication Module
 *
 * Enterprise-grade JWT authentication manager
 * Handles user authentication, token management, and session persistence
 *
 * @version 1.0.0
 * @author TranslateCloud
 */

const Auth = (() => {
  // ============================================
  // CONFIGURATION
  // ============================================

  const CONFIG = {
    API_BASE_URL: 'https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod',
    TOKEN_KEY: 'translatecloud_token',
    USER_KEY: 'translatecloud_user',
    TOKEN_EXPIRY_KEY: 'translatecloud_token_expiry',
    REFRESH_THRESHOLD: 5 * 60 * 1000, // Refresh if expires in < 5 minutes
  };

  // ============================================
  // TOKEN MANAGEMENT
  // ============================================

  /**
   * Store JWT token securely in localStorage
   * @param {string} token - JWT token from backend
   * @param {number} expiresIn - Token lifetime in seconds (default 24h)
   */
  const setToken = (token, expiresIn = 86400) => {
    try {
      localStorage.setItem(CONFIG.TOKEN_KEY, token);
      const expiryTime = Date.now() + (expiresIn * 1000);
      localStorage.setItem(CONFIG.TOKEN_EXPIRY_KEY, expiryTime.toString());
    } catch (error) {
      console.error('[Auth] Failed to store token:', error);
      throw new Error('Unable to save authentication session');
    }
  };

  /**
   * Retrieve stored JWT token
   * @returns {string|null} JWT token or null if not found
   */
  const getToken = () => {
    try {
      return localStorage.getItem(CONFIG.TOKEN_KEY);
    } catch (error) {
      console.error('[Auth] Failed to retrieve token:', error);
      return null;
    }
  };

  /**
   * Remove JWT token from storage
   */
  const clearToken = () => {
    try {
      localStorage.removeItem(CONFIG.TOKEN_KEY);
      localStorage.removeItem(CONFIG.TOKEN_EXPIRY_KEY);
      localStorage.removeItem(CONFIG.USER_KEY);
    } catch (error) {
      console.error('[Auth] Failed to clear token:', error);
    }
  };

  /**
   * Check if token exists and is not expired
   * @returns {boolean} True if authenticated
   */
  const isAuthenticated = () => {
    const token = getToken();
    if (!token) return false;

    const expiryTime = localStorage.getItem(CONFIG.TOKEN_EXPIRY_KEY);
    if (!expiryTime) return false;

    const isExpired = Date.now() >= parseInt(expiryTime);
    if (isExpired) {
      clearToken();
      return false;
    }

    return true;
  };

  /**
   * Check if token needs refresh (expires in < 5 minutes)
   * @returns {boolean} True if refresh needed
   */
  const needsRefresh = () => {
    const expiryTime = localStorage.getItem(CONFIG.TOKEN_EXPIRY_KEY);
    if (!expiryTime) return false;

    const timeUntilExpiry = parseInt(expiryTime) - Date.now();
    return timeUntilExpiry < CONFIG.REFRESH_THRESHOLD && timeUntilExpiry > 0;
  };

  // ============================================
  // USER MANAGEMENT
  // ============================================

  /**
   * Store user profile data
   * @param {Object} user - User profile object
   */
  const setUser = (user) => {
    try {
      localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
    } catch (error) {
      console.error('[Auth] Failed to store user data:', error);
    }
  };

  /**
   * Retrieve stored user profile
   * @returns {Object|null} User profile or null
   */
  const getUser = () => {
    try {
      const userData = localStorage.getItem(CONFIG.USER_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('[Auth] Failed to retrieve user data:', error);
      return null;
    }
  };

  // ============================================
  // AUTHENTICATION ACTIONS
  // ============================================

  /**
   * User login
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} User data and token
   */
  const login = async (email, password) => {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/api/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();

      // Store token and user data
      setToken(data.access_token, data.expires_in || 86400);
      setUser(data.user);

      return data;
    } catch (error) {
      console.error('[Auth] Login error:', error);
      throw error;
    }
  };

  /**
   * User signup
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} Created user data
   */
  const signup = async (userData) => {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/api/users/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
      }

      const data = await response.json();

      // Auto-login after signup
      if (data.access_token) {
        setToken(data.access_token, data.expires_in || 86400);
        setUser(data.user);
      }

      return data;
    } catch (error) {
      console.error('[Auth] Signup error:', error);
      throw error;
    }
  };

  /**
   * User logout
   */
  const logout = () => {
    clearToken();

    // Redirect to home page
    window.location.href = '/en/index.html';
  };

  /**
   * Get current user profile from API
   * @returns {Promise<Object>} User profile
   */
  const getCurrentUser = async () => {
    try {
      const token = getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${CONFIG.API_BASE_URL}/api/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          clearToken();
          throw new Error('Session expired');
        }
        throw new Error('Failed to fetch user profile');
      }

      const userData = await response.json();
      setUser(userData);

      return userData;
    } catch (error) {
      console.error('[Auth] Get current user error:', error);
      throw error;
    }
  };

  /**
   * Delete user account (GDPR compliance)
   * @returns {Promise<void>}
   */
  const deleteAccount = async () => {
    try {
      const token = getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${CONFIG.API_BASE_URL}/api/users/me`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete account');
      }

      clearToken();
      window.location.href = '/en/index.html';
    } catch (error) {
      console.error('[Auth] Delete account error:', error);
      throw error;
    }
  };

  /**
   * Export user data (GDPR compliance)
   * @returns {Promise<Blob>} User data as JSON file
   */
  const exportData = async () => {
    try {
      const token = getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${CONFIG.API_BASE_URL}/api/users/me/export`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to export data');
      }

      const data = await response.json();

      // Create downloadable JSON file
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json'
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `translatecloud-data-export-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      return blob;
    } catch (error) {
      console.error('[Auth] Export data error:', error);
      throw error;
    }
  };

  // ============================================
  // ROUTE PROTECTION
  // ============================================

  /**
   * Require authentication - redirect to login if not authenticated
   * @param {string} redirectUrl - URL to redirect after login (optional)
   */
  const requireAuth = (redirectUrl = null) => {
    if (!isAuthenticated()) {
      const loginUrl = '/en/login.html';
      if (redirectUrl) {
        window.location.href = `${loginUrl}?redirect=${encodeURIComponent(redirectUrl)}`;
      } else {
        window.location.href = loginUrl;
      }
    }
  };

  /**
   * Redirect if already authenticated
   * @param {string} redirectUrl - URL to redirect to (default: dashboard)
   */
  const requireGuest = (redirectUrl = '/en/dashboard.html') => {
    if (isAuthenticated()) {
      window.location.href = redirectUrl;
    }
  };

  /**
   * Get redirect URL from query params
   * @returns {string|null} Redirect URL or null
   */
  const getRedirectUrl = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('redirect');
  };

  // ============================================
  // PUBLIC API
  // ============================================

  return {
    // Token management
    setToken,
    getToken,
    clearToken,
    isAuthenticated,
    needsRefresh,

    // User management
    setUser,
    getUser,
    getCurrentUser,

    // Authentication
    login,
    signup,
    logout,

    // GDPR
    deleteAccount,
    exportData,

    // Route protection
    requireAuth,
    requireGuest,
    getRedirectUrl,

    // Config
    CONFIG,
  };
})();

// ============================================
// GLOBAL ERROR HANDLER
// ============================================

window.addEventListener('unhandledrejection', (event) => {
  // Handle 401 errors globally - session expired
  if (event.reason && event.reason.message === 'Session expired') {
    Auth.clearToken();
    window.location.href = '/en/login.html?expired=true';
  }
});

// Export for ES6 modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Auth;
}
