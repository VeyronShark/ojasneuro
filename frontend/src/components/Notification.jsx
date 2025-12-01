import { useNotification } from '../context/NotificationContext'
import { CheckCircle2, XCircle, Info, X } from 'lucide-react'

/**
 * Notification component - Toast notifications display
 * Requirements: 10.2, 10.3 - Success and error notifications
 */
export default function Notification() {
  const { notifications, removeNotification } = useNotification();

  if (notifications.length === 0) {
    return null;
  }

  const icons = {
    success: <CheckCircle2 size={20} />,
    error: <XCircle size={20} />,
    info: <Info size={20} />
  };

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
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}

const typeStyles = {
  success: {
    background: 'var(--success-light)',
    borderColor: 'var(--success)',
    color: '#2E7D32'
  },
  error: {
    background: 'var(--error-light)',
    borderColor: 'var(--error)',
    color: '#C62828'
  },
  info: {
    background: 'var(--primary-light)',
    borderColor: 'var(--primary)',
    color: 'var(--primary-dark)'
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
    gap: '0.75rem',
    maxWidth: '400px'
  },
  notification: {
    display: 'flex',
    alignItems: 'center',
    padding: '1rem 1.25rem',
    borderRadius: 'var(--radius-lg)',
    border: '1px solid',
    boxShadow: 'var(--shadow-md)',
    animation: 'slideIn 0.3s ease-out',
    background: 'var(--bg-secondary)'
  },
  icon: {
    marginRight: '0.75rem',
    display: 'flex',
    alignItems: 'center',
    flexShrink: 0
  },
  message: {
    flex: 1,
    fontSize: '0.875rem',
    fontWeight: '500',
    lineHeight: 1.5
  },
  closeButton: {
    marginLeft: '0.75rem',
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    opacity: 0.6,
    padding: '0.25rem',
    display: 'flex',
    alignItems: 'center',
    borderRadius: 'var(--radius-sm)',
    transition: 'opacity 0.2s ease'
  }
};
