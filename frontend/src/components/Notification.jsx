/**
 * Notification component - Toast notifications display
 * Requirements: 10.2, 10.3 - Success and error notifications
 */
import { useNotification } from '../context/NotificationContext';

export default function Notification() {
  const { notifications, removeNotification } = useNotification();

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div style={styles.container} aria-live="polite">
      {notifications.map(notification => (
        <div
          key={notification.id}
          style={{
            ...styles.notification,
            ...typeStyles[notification.type]
          }}
          role="alert"
        >
          <span style={styles.icon}>{icons[notification.type]}</span>
          <span style={styles.message}>{notification.message}</span>
          <button
            onClick={() => removeNotification(notification.id)}
            style={styles.closeButton}
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

const icons = {
  success: '✓',
  error: '✕',
  info: 'ℹ'
};

const typeStyles = {
  success: {
    background: '#d4edda',
    borderColor: '#c3e6cb',
    color: '#155724'
  },
  error: {
    background: '#f8d7da',
    borderColor: '#f5c6cb',
    color: '#721c24'
  },
  info: {
    background: '#d1ecf1',
    borderColor: '#bee5eb',
    color: '#0c5460'
  }
};

const styles = {
  container: {
    position: 'fixed',
    top: '1rem',
    right: '1rem',
    zIndex: 1000,
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
    maxWidth: '400px'
  },
  notification: {
    display: 'flex',
    alignItems: 'center',
    padding: '0.75rem 1rem',
    borderRadius: '4px',
    border: '1px solid',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
    animation: 'slideIn 0.3s ease-out'
  },
  icon: {
    marginRight: '0.75rem',
    fontWeight: 'bold',
    fontSize: '1rem'
  },
  message: {
    flex: 1,
    fontSize: '0.875rem'
  },
  closeButton: {
    marginLeft: '0.75rem',
    background: 'transparent',
    border: 'none',
    fontSize: '1.25rem',
    cursor: 'pointer',
    opacity: 0.7,
    padding: '0 0.25rem',
    lineHeight: 1
  }
};

// Inject keyframes for notification animation
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `;
  if (!document.querySelector('[data-notification-styles]')) {
    styleSheet.setAttribute('data-notification-styles', 'true');
    document.head.appendChild(styleSheet);
  }
}
