/**
 * TranslateCloud - API Client Module
 *
 * Enterprise-grade HTTP client for backend API communication
 * Handles authentication, error handling, request/response interceptors
 *
 * @version 1.0.0
 * @author TranslateCloud
 */

const API = (() => {
  // ============================================
  // CONFIGURATION
  // ============================================

  const CONFIG = {
    BASE_URL: 'https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod',
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 second
  };

  // ============================================
  // REQUEST BUILDER
  // ============================================

  /**
   * Build request options with authentication and headers
   * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
   * @param {Object|null} body - Request body (will be JSON stringified)
   * @param {Object} customHeaders - Additional headers
   * @returns {Object} Fetch options
   */
  const buildRequestOptions = (method, body = null, customHeaders = {}) => {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...customHeaders,
      },
    };

    // Add authentication token if available
    const token = Auth.getToken();
    if (token) {
      options.headers['Authorization'] = `Bearer ${token}`;
    }

    // Add body for non-GET requests
    if (body && method !== 'GET') {
      options.body = JSON.stringify(body);
    }

    return options;
  };

  /**
   * Build full URL with query parameters
   * @param {string} endpoint - API endpoint path
   * @param {Object} params - Query parameters
   * @returns {string} Full URL
   */
  const buildUrl = (endpoint, params = {}) => {
    const url = new URL(`${CONFIG.BASE_URL}${endpoint}`);

    // Add query parameters
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined) {
        url.searchParams.append(key, params[key]);
      }
    });

    return url.toString();
  };

  // ============================================
  // ERROR HANDLING
  // ============================================

  /**
   * Parse and format API error response
   * @param {Response} response - Fetch response object
   * @returns {Promise<Error>} Formatted error
   */
  const handleErrorResponse = async (response) => {
    let errorMessage = 'An unexpected error occurred';
    let errorDetails = null;

    try {
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
        errorDetails = errorData;
      } else {
        const text = await response.text();
        errorMessage = text || `HTTP ${response.status}: ${response.statusText}`;
      }
    } catch (parseError) {
      console.error('[API] Failed to parse error response:', parseError);
      errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    }

    const error = new Error(errorMessage);
    error.status = response.status;
    error.statusText = response.statusText;
    error.details = errorDetails;

    return error;
  };

  /**
   * Check if error is retryable (network issues, 5xx errors)
   * @param {Error} error - Error object
   * @returns {boolean} True if retryable
   */
  const isRetryableError = (error) => {
    // Network errors (no status code)
    if (!error.status) return true;

    // Server errors (5xx)
    if (error.status >= 500 && error.status < 600) return true;

    // Rate limiting (429)
    if (error.status === 429) return true;

    return false;
  };

  /**
   * Sleep utility for retry delays
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise<void>}
   */
  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  // ============================================
  // CORE HTTP CLIENT
  // ============================================

  /**
   * Make HTTP request with retry logic and error handling
   * @param {string} endpoint - API endpoint path
   * @param {Object} options - Request options
   * @param {number} attempt - Current retry attempt
   * @returns {Promise<any>} Response data
   */
  const request = async (endpoint, options = {}, attempt = 1) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);

    try {
      const response = await fetch(endpoint, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle successful responses (2xx)
      if (response.ok) {
        const contentType = response.headers.get('content-type');

        // Return JSON if available
        if (contentType && contentType.includes('application/json')) {
          return await response.json();
        }

        // Return text for non-JSON responses
        return await response.text();
      }

      // Handle error responses
      const error = await handleErrorResponse(response);

      // Handle authentication errors (401)
      if (response.status === 401) {
        Auth.clearToken();
        window.location.href = '/en/login.html?expired=true';
        throw error;
      }

      // Retry logic for retryable errors
      if (isRetryableError(error) && attempt < CONFIG.RETRY_ATTEMPTS) {
        const delay = CONFIG.RETRY_DELAY * attempt;
        console.warn(`[API] Retrying request (attempt ${attempt + 1}/${CONFIG.RETRY_ATTEMPTS}) after ${delay}ms`);
        await sleep(delay);
        return request(endpoint, options, attempt + 1);
      }

      throw error;

    } catch (error) {
      clearTimeout(timeoutId);

      // Handle timeout errors
      if (error.name === 'AbortError') {
        const timeoutError = new Error('Request timeout - please try again');
        timeoutError.status = 408;
        throw timeoutError;
      }

      // Handle network errors
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        const networkError = new Error('Network error - please check your connection');
        networkError.status = 0;
        throw networkError;
      }

      throw error;
    }
  };

  // ============================================
  // HTTP METHODS
  // ============================================

  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Query parameters
   * @param {Object} headers - Custom headers
   * @returns {Promise<any>} Response data
   */
  const get = async (endpoint, params = {}, headers = {}) => {
    const url = buildUrl(endpoint, params);
    const options = buildRequestOptions('GET', null, headers);
    return request(url, options);
  };

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {Object} body - Request body
   * @param {Object} headers - Custom headers
   * @returns {Promise<any>} Response data
   */
  const post = async (endpoint, body = {}, headers = {}) => {
    const url = buildUrl(endpoint);
    const options = buildRequestOptions('POST', body, headers);
    return request(url, options);
  };

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {Object} body - Request body
   * @param {Object} headers - Custom headers
   * @returns {Promise<any>} Response data
   */
  const put = async (endpoint, body = {}, headers = {}) => {
    const url = buildUrl(endpoint);
    const options = buildRequestOptions('PUT', body, headers);
    return request(url, options);
  };

  /**
   * PATCH request
   * @param {string} endpoint - API endpoint
   * @param {Object} body - Request body
   * @param {Object} headers - Custom headers
   * @returns {Promise<any>} Response data
   */
  const patch = async (endpoint, body = {}, headers = {}) => {
    const url = buildUrl(endpoint);
    const options = buildRequestOptions('PATCH', body, headers);
    return request(url, options);
  };

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Query parameters
   * @param {Object} headers - Custom headers
   * @returns {Promise<any>} Response data
   */
  const del = async (endpoint, params = {}, headers = {}) => {
    const url = buildUrl(endpoint, params);
    const options = buildRequestOptions('DELETE', null, headers);
    return request(url, options);
  };

  // ============================================
  // DOMAIN-SPECIFIC API METHODS
  // ============================================

  // --------------- USERS ---------------

  const users = {
    /**
     * Get current user profile
     * @returns {Promise<Object>} User data
     */
    getCurrentUser: () => get('/api/users/me'),

    /**
     * Update user profile
     * @param {Object} userData - Updated user data
     * @returns {Promise<Object>} Updated user
     */
    updateProfile: (userData) => put('/api/users/me', userData),

    /**
     * Delete user account
     * @returns {Promise<void>}
     */
    deleteAccount: () => del('/api/users/me'),

    /**
     * Export user data (GDPR)
     * @returns {Promise<Object>} User data export
     */
    exportData: () => get('/api/users/me/export'),
  };

  // --------------- PROJECTS ---------------

  const projects = {
    /**
     * List all user projects
     * @param {Object} params - Query parameters (page, limit, etc.)
     * @returns {Promise<Array>} Projects list
     */
    list: (params = {}) => get('/api/projects', params),

    /**
     * Get single project by ID
     * @param {string} projectId - Project UUID
     * @returns {Promise<Object>} Project data
     */
    get: (projectId) => get(`/api/projects/${projectId}`),

    /**
     * Create new project
     * @param {Object} projectData - Project creation data
     * @returns {Promise<Object>} Created project
     */
    create: (projectData) => post('/api/projects', projectData),

    /**
     * Update project
     * @param {string} projectId - Project UUID
     * @param {Object} projectData - Updated project data
     * @returns {Promise<Object>} Updated project
     */
    update: (projectId, projectData) => put(`/api/projects/${projectId}`, projectData),

    /**
     * Delete project
     * @param {string} projectId - Project UUID
     * @returns {Promise<void>}
     */
    delete: (projectId) => del(`/api/projects/${projectId}`),
  };

  // --------------- TRANSLATIONS ---------------

  const translations = {
    /**
     * List all translations
     * @param {Object} params - Query parameters (project_id, status, etc.)
     * @returns {Promise<Array>} Translations list
     */
    list: (params = {}) => get('/api/translations', params),

    /**
     * Get single translation by ID
     * @param {string} translationId - Translation UUID
     * @returns {Promise<Object>} Translation data
     */
    get: (translationId) => get(`/api/translations/${translationId}`),

    /**
     * Create new translation
     * @param {Object} translationData - Translation request data
     * @returns {Promise<Object>} Created translation
     */
    create: (translationData) => post('/api/translations', translationData),

    /**
     * Get translation status
     * @param {string} translationId - Translation UUID
     * @returns {Promise<Object>} Translation status
     */
    getStatus: (translationId) => get(`/api/translations/${translationId}/status`),
  };

  // --------------- PAYMENTS ---------------

  const payments = {
    /**
     * Create Stripe payment intent
     * @param {Object} paymentData - Payment details (amount, currency, etc.)
     * @returns {Promise<Object>} Payment intent
     */
    createIntent: (paymentData) => post('/api/payments/create-intent', paymentData),

    /**
     * Get payment history
     * @param {Object} params - Query parameters (page, limit, etc.)
     * @returns {Promise<Array>} Payment history
     */
    getHistory: (params = {}) => get('/api/payments', params),
  };

  // --------------- HEALTH CHECK ---------------

  /**
   * Check API health status
   * @returns {Promise<Object>} Health status
   */
  const healthCheck = () => get('/health');

  // ============================================
  // PUBLIC API
  // ============================================

  return {
    // HTTP methods
    get,
    post,
    put,
    patch,
    delete: del,

    // Domain APIs
    users,
    projects,
    translations,
    payments,

    // Utilities
    healthCheck,

    // Config
    CONFIG,
  };
})();

// Export for ES6 modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API;
}
