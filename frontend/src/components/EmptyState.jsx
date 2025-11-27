/**
 * EmptyState - Reusable component for displaying empty state messages
 * Requirements: 10.4 - Display helpful messages when no data exists
 */

export default function EmptyState({ 
  icon = '📭', 
  title, 
  message, 
  actionLabel, 
  onAction,
  secondaryActionLabel,
  onSecondaryAction
}) {
  return (
    <div style={styles.container}>
      <div style={styles.icon}>{icon}</div>
      {title && <h3 style={styles.title}>{title}</h3>}
      {message && <p style={styles.message}>{message}</p>}
      <div style={styles.actions}>
        {actionLabel && onAction && (
          <button onClick={onAction} style={styles.primaryButton}>
            {actionLabel}
          </button>
        )}
        {secondaryActionLabel && onSecondaryAction && (
          <button onClick={onSecondaryAction} style={styles.secondaryButton}>
            {secondaryActionLabel}
          </button>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    textAlign: 'center',
    padding: '3rem 2rem',
    color: '#6c757d'
  },
  icon: {
    fontSize: '3rem',
    marginBottom: '1rem'
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: '0.5rem'
  },
  message: {
    fontSize: '0.9375rem',
    lineHeight: '1.6',
    maxWidth: '400px',
    margin: '0 auto 1.5rem'
  },
  actions: {
    display: 'flex',
    gap: '0.75rem',
    justifyContent: 'center',
    flexWrap: 'wrap'
  },
  primaryButton: {
    padding: '0.75rem 1.5rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.9375rem',
    fontWeight: '500'
  },
  secondaryButton: {
    padding: '0.75rem 1.5rem',
    background: '#f8f9fa',
    color: '#495057',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.9375rem',
    fontWeight: '500'
  }
}
