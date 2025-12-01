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
    color: 'var(--text-muted)'
  },
  icon: {
    fontSize: '3rem',
    marginBottom: '1rem',
    opacity: 0.8
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'var(--text-primary)',
    marginBottom: '0.5rem',
    letterSpacing: '-0.01em'
  },
  message: {
    fontSize: '0.9375rem',
    lineHeight: '1.6',
    maxWidth: '400px',
    margin: '0 auto 1.5rem',
    color: 'var(--text-secondary)'
  },
  actions: {
    display: 'flex',
    gap: '0.75rem',
    justifyContent: 'center',
    flexWrap: 'wrap'
  },
  primaryButton: {
    padding: '0.75rem 1.5rem',
    background: 'var(--primary)',
    color: 'white',
    border: 'none',
    borderRadius: 'var(--radius-md)',
    cursor: 'pointer',
    fontSize: '0.9375rem',
    fontWeight: '500',
    boxShadow: 'var(--shadow-sm)',
    transition: 'all 0.2s ease'
  },
  secondaryButton: {
    padding: '0.75rem 1.5rem',
    background: 'var(--bg-tertiary)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    cursor: 'pointer',
    fontSize: '0.9375rem',
    fontWeight: '500',
    transition: 'all 0.2s ease'
  }
}
