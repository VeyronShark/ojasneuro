/**
 * useApi - Generic API call hook with loading, error, and data states
 * Requirements: 1.1, 10.1 - Data fetching with loading indicators
 */
import { useState, useCallback } from 'react';

/**
 * Custom hook for managing API calls with loading, error, and data states
 * @param {Function} apiFunction - The API function to call
 * @param {Object} options - Configuration options
 * @param {boolean} options.immediate - Whether to execute immediately on mount
 * @returns {Object} - { data, loading, error, execute, reset }
 */
export function useApi(apiFunction, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunction(...args);
      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err.message || 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunction]);

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset,
  };
}

export default useApi;
