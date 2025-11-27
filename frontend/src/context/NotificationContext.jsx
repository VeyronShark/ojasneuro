/**
 * NotificationContext - Global notification state management
 * Requirements: 10.2, 10.3 - Success and error notifications
 */
import { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext(null);

// Default auto-dismiss timeout in milliseconds
const DEFAULT_TIMEOUT = 5000;

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((type, message, options = {}) => {
    const id = Date.now() + Math.random();
    const timeout = options.timeout ?? DEFAULT_TIMEOUT;
    
    const notification = {
      id,
      type, // 'success', 'error', 'info'
      message,
      timeout
    };

    setNotifications(prev => [...prev, notification]);

    // Auto-dismiss after timeout
    if (timeout > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, timeout);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const showSuccess = useCallback((message, options) => {
    return addNotification('success', message, options);
  }, [addNotification]);

  const showError = useCallback((message, options) => {
    return addNotification('error', message, options);
  }, [addNotification]);

  const showInfo = useCallback((message, options) => {
    return addNotification('info', message, options);
  }, [addNotification]);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const value = {
    notifications,
    addNotification,
    removeNotification,
    showSuccess,
    showError,
    showInfo,
    clearAll
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
}

export default NotificationContext;
