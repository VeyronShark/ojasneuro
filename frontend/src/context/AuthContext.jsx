import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI, authEvents } from '../api/config';

const AuthContext = createContext(null);

const TOKEN_KEY = 'token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Handle 401 unauthorized events from API
  const handleUnauthorized = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setError('Session expired. Please log in again.');
  }, []);

  // Subscribe to auth events (401 handling)
  useEffect(() => {
    const unsubscribe = authEvents.subscribe((event) => {
      if (event.type === 'unauthorized') {
        handleUnauthorized();
      }
    });
    return unsubscribe;
  }, [handleUnauthorized]);

  // Restore session on app load
  const restoreSession = useCallback(async () => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    if (!storedToken) {
      setLoading(false);
      return false;
    }

    try {
      const profile = await authAPI.getProfile();
      setUser(profile.user || profile);
      setToken(storedToken);
      setError(null);
      return true;
    } catch (err) {
      // Token is invalid or expired - clear it
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUser(null);
      setError(null);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Restore session on mount
  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.login(email, password);
      const newToken = response.token;
      const userData = response.user;

      localStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
      setUser(userData);
      return userData;
    } catch (err) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      // Ignore logout API errors - still clear local state
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUser(null);
      setError(null);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated: !!user && !!token,
    login,
    logout,
    restoreSession,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
