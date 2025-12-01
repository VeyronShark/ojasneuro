import { Loader2 } from 'lucide-react'

/**
 * LoadingSpinner component
 * Displays a centered spinner with optional message
 * Requirements: 10.1 - Loading indicators during data fetching
 */
export default function LoadingSpinner({ message = 'Loading...', size = 'medium' }) {
  const iconSize = sizes[size] || sizes.medium;
  
  return (
    <div style={styles.container} role="status" aria-live="polite">
      <Loader2 size={iconSize} style={styles.spinner} />
      {message && <p style={styles.message}>{message}</p>}
    </div>
  );
}

const sizes = {
  small: 20,
  medium: 40,
  large: 60
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
    gap: '1rem'
  },
  spinner: {
    color: 'var(--primary)',
    animation: 'spin 1s linear infinite'
  },
  message: {
    color: 'var(--text-muted)',
    fontSize: '0.875rem',
    margin: 0
  }
}
