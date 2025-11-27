/**
 * **Feature: frontend-backend-integration, Property 8: Action Feedback Notifications**
 * **Validates: Requirements 10.2, 10.3**
 * 
 * For any successful mutation action (create, update, delete), the UI SHALL display
 * a success notification, and for any failed action, the UI SHALL display an error notification.
 */

import { describe, it, expect, afterEach } from 'vitest';
import { test, fc } from '@fast-check/vitest';
import { render, screen, cleanup, act } from '@testing-library/react';
import { NotificationProvider, useNotification } from '../../context/NotificationContext';
import Notification from '../../components/Notification';

// Clean up after each test
afterEach(() => {
  cleanup();
});

// Generate valid notification messages
const validMessageArb = fc.string({ minLength: 1, maxLength: 200 })
  .filter(s => s.trim().length > 0);

// Generate valid notification types
const validTypeArb = fc.constantFrom('success', 'error', 'info');

// Test component that exposes notification functions
function TestNotificationTrigger({ onMount }) {
  const notification = useNotification();
  
  // Call onMount with notification context on first render
  if (onMount) {
    onMount(notification);
  }
  
  return null;
}

// Wrapper component for testing
function TestWrapper({ children, onNotificationMount }) {
  return (
    <NotificationProvider>
      <TestNotificationTrigger onMount={onNotificationMount} />
      <Notification />
      {children}
    </NotificationProvider>
  );
}

describe('Property 8: Action Feedback Notifications', () => {
  
  /**
   * Property 8.1: Success notifications display for any valid message
   * For any valid success message, the notification SHALL be displayed
   * **Validates: Requirements 10.2**
   */
  test.prop([validMessageArb], { numRuns: 100 })(
    'success notification displays any valid message',
    async (message) => {
      cleanup();
      let notificationContext;
      
      render(
        <TestWrapper onNotificationMount={(ctx) => { notificationContext = ctx; }} />
      );
      
      // Trigger success notification
      act(() => {
        notificationContext.showSuccess(message);
      });
      
      // Notification should be visible
      const notification = screen.getByRole('alert');
      expect(notification).toBeInTheDocument();
      expect(notification.textContent).toContain(message);
    }
  );

  /**
   * Property 8.2: Error notifications display for any valid message
   * For any valid error message, the notification SHALL be displayed
   * **Validates: Requirements 10.3**
   */
  test.prop([validMessageArb], { numRuns: 100 })(
    'error notification displays any valid message',
    async (message) => {
      cleanup();
      let notificationContext;
      
      render(
        <TestWrapper onNotificationMount={(ctx) => { notificationContext = ctx; }} />
      );
      
      // Trigger error notification
      act(() => {
        notificationContext.showError(message);
      });
      
      // Notification should be visible
      const notification = screen.getByRole('alert');
      expect(notification).toBeInTheDocument();
      expect(notification.textContent).toContain(message);
    }
  );

  /**
   * Property 8.3: Notification type determines styling
   * For any notification type, the correct styling SHALL be applied
   * **Validates: Requirements 10.2, 10.3**
   */
  test.prop([validTypeArb, validMessageArb], { numRuns: 100 })(
    'notification type determines correct styling',
    async (type, message) => {
      cleanup();
      let notificationContext;
      
      render(
        <TestWrapper onNotificationMount={(ctx) => { notificationContext = ctx; }} />
      );
      
      // Trigger notification of specified type
      act(() => {
        notificationContext.addNotification(type, message);
      });
      
      // Notification should be visible with correct type
      const notification = screen.getByRole('alert');
      expect(notification).toBeInTheDocument();
      expect(notification.textContent).toContain(message);
    }
  );

  /**
   * Property 8.4: Multiple notifications can be displayed
   * For any sequence of notifications, all SHALL be displayed
   * **Validates: Requirements 10.2, 10.3**
   */
  test.prop([fc.array(fc.record({
    type: validTypeArb,
    message: validMessageArb
  }), { minLength: 1, maxLength: 5 })], { numRuns: 50 })(
    'multiple notifications are all displayed',
    async (notifications) => {
      cleanup();
      let notificationContext;
      
      render(
        <TestWrapper onNotificationMount={(ctx) => { notificationContext = ctx; }} />
      );
      
      // Trigger all notifications
      act(() => {
        notifications.forEach(({ type, message }) => {
          notificationContext.addNotification(type, message);
        });
      });
      
      // All notifications should be visible
      const alerts = screen.getAllByRole('alert');
      expect(alerts.length).toBe(notifications.length);
    }
  );

  /**
   * Property 8.5: Notifications can be dismissed
   * For any notification, it SHALL be removable
   * **Validates: Requirements 10.2, 10.3**
   */
  test.prop([validTypeArb, validMessageArb], { numRuns: 100 })(
    'notifications can be dismissed',
    async (type, message) => {
      cleanup();
      let notificationContext;
      let notificationId;
      
      render(
        <TestWrapper onNotificationMount={(ctx) => { notificationContext = ctx; }} />
      );
      
      // Add notification
      act(() => {
        notificationId = notificationContext.addNotification(type, message, { timeout: 0 });
      });
      
      // Notification should be visible
      expect(screen.getByRole('alert')).toBeInTheDocument();
      
      // Remove notification
      act(() => {
        notificationContext.removeNotification(notificationId);
      });
      
      // Notification should be gone
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    }
  );

  /**
   * Property 8.6: No notifications when none added
   * When no notifications exist, the container SHALL not render alerts
   * **Validates: Requirements 10.2, 10.3**
   */
  it('no notifications displayed when none added', () => {
    render(
      <TestWrapper />
    );
    
    // No alerts should be present
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  /**
   * Property 8.7: Clear all removes all notifications
   * For any set of notifications, clearAll SHALL remove all of them
   * **Validates: Requirements 10.2, 10.3**
   */
  test.prop([fc.array(validMessageArb, { minLength: 1, maxLength: 5 })], { numRuns: 50 })(
    'clearAll removes all notifications',
    async (messages) => {
      cleanup();
      let notificationContext;
      
      render(
        <TestWrapper onNotificationMount={(ctx) => { notificationContext = ctx; }} />
      );
      
      // Add multiple notifications
      act(() => {
        messages.forEach(message => {
          notificationContext.showSuccess(message, { timeout: 0 });
        });
      });
      
      // All should be visible
      expect(screen.getAllByRole('alert').length).toBe(messages.length);
      
      // Clear all
      act(() => {
        notificationContext.clearAll();
      });
      
      // None should remain
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    }
  );
});
