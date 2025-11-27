/**
 * LoadingSpinner component
 * Displays a centered spinner with optional message
 * Requirements: 10.1 - Loading indicators during data fetching
 */
export default function LoadingSpinner({ message = 'Loading...', size = 'medium' }) {
  const spinnerSize = sizes[size] || sizes.medium;
  
  return (
    <div style={styles.container} role="status" aria-live="polite">
      <div style={{ ...styles.spinner, ...spinnerSize }} />
      {message && <p style={styles.message}>{message}</p>}
    </div>
  );
}

const sizes = {
  small: { width: '20px', height: '20px', borderWidth: '2px' },
  medium: { width: '40px', height: '40px', borderWidth: '3px' },
  large: { width: '60px', height: '60px', borderWidth: '4px' }
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
    border: '3px solid #e1e4e8',
    borderTop: '3px solid #3498db',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  message: {
    color: '#6c757d',
    fontSize: '0.875rem',
    margin: 0
  }
};

// Inject keyframes for spinner animation
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;
  if (!document.querySelector('[data-loading-spinner-styles]')) {
    styleSheet.setAttribute('data-loading-spinner-styles', 'true');
    document.head.appendChild(styleSheet);
  }
}
