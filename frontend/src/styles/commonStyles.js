// Common button styles for consistent UI across the application
export const buttonStyles = {
  primary: {
    padding: '0.625rem 1.25rem',
    background: 'var(--primary)',
    color: 'white',
    border: 'none',
    borderRadius: 'var(--radius-md)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    boxShadow: 'var(--shadow-sm)',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  },
  
  secondary: {
    padding: '0.625rem 1.25rem',
    background: 'var(--bg-tertiary)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  },
  
  success: {
    padding: '0.625rem 1.25rem',
    background: 'var(--success)',
    color: 'white',
    border: 'none',
    borderRadius: 'var(--radius-md)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    boxShadow: 'var(--shadow-sm)',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  },
  
  danger: {
    padding: '0.625rem 1.25rem',
    background: 'var(--error)',
    color: 'white',
    border: 'none',
    borderRadius: 'var(--radius-md)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    boxShadow: 'var(--shadow-sm)',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  },
  
  ghost: {
    padding: '0.5rem 0.75rem',
    background: 'transparent',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border-light)',
    borderRadius: 'var(--radius-sm)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '0.375rem'
  }
};

export const formStyles = {
  formGroup: {
    marginBottom: '1.25rem'
  },
  
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: '500',
    color: 'var(--text-primary)',
    fontSize: '0.875rem'
  },
  
  input: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    fontSize: '1rem',
    boxSizing: 'border-box',
    transition: 'all 0.2s ease'
  },
  
  select: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    fontSize: '1rem',
    boxSizing: 'border-box',
    background: 'var(--bg-secondary)',
    transition: 'all 0.2s ease'
  },
  
  textarea: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    fontSize: '1rem',
    boxSizing: 'border-box',
    minHeight: '100px',
    resize: 'vertical',
    fontFamily: 'inherit',
    transition: 'all 0.2s ease'
  }
};

export const tableStyles = {
  table: {
    width: '100%',
    borderCollapse: 'collapse'
  },
  
  th: {
    textAlign: 'left',
    padding: '0.875rem 0.75rem',
    borderBottom: '2px solid var(--border-light)',
    fontSize: '0.8125rem',
    fontWeight: '600',
    color: 'var(--text-secondary)',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
  },
  
  row: {
    cursor: 'pointer',
    borderBottom: '1px solid var(--border-light)',
    transition: 'background 0.2s ease'
  },
  
  td: {
    padding: '1rem 0.75rem',
    fontSize: '0.875rem',
    color: 'var(--text-primary)'
  }
};

export const badgeStyles = {
  default: {
    padding: '0.25rem 0.75rem',
    borderRadius: 'var(--radius-lg)',
    fontSize: '0.75rem',
    fontWeight: '500',
    display: 'inline-block'
  },
  
  primary: {
    background: 'var(--primary-light)',
    color: 'var(--primary-dark)'
  },
  
  success: {
    background: 'var(--success-light)',
    color: '#2E7D32'
  },
  
  warning: {
    background: 'var(--warning-light)',
    color: '#E65100'
  },
  
  error: {
    background: 'var(--error-light)',
    color: '#C62828'
  }
};
