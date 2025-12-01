import { useEffect, useCallback } from 'react'
import { X } from 'lucide-react'

/**
 * Modal component - Reusable modal wrapper
 * Requirements: 2.1, 3.2 - Forms for adding classrooms and students
 */
export default function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  actions,
  size = 'medium' 
}) {
  // Handle escape key press
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape') {
      onClose();
    }
  }, [onClose]);

  // Handle backdrop click
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Add/remove event listener for escape key
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) {
    return null;
  }

  const modalWidth = sizeStyles[size] || sizeStyles.medium;

  return (
    <div 
      style={styles.backdrop} 
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div style={{ ...styles.modal, ...modalWidth }}>
        <div style={styles.header}>
          <h2 id="modal-title" style={styles.title}>{title}</h2>
          <button 
            onClick={onClose} 
            style={styles.closeButton}
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>
        
        <div style={styles.content}>
          {children}
        </div>
        
        {actions && (
          <div style={styles.actions}>
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

const sizeStyles = {
  small: { maxWidth: '400px' },
  medium: { maxWidth: '500px' },
  large: { maxWidth: '700px' }
};

const styles = {
  backdrop: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(44, 62, 80, 0.6)',
    backdropFilter: 'blur(4px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '1rem',
    animation: 'fadeIn 0.2s ease'
  },
  modal: {
    background: 'var(--bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'auto',
    boxShadow: 'var(--shadow-lg)',
    animation: 'fadeIn 0.3s ease'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.25rem 1.5rem',
    borderBottom: '1px solid var(--border-light)'
  },
  title: {
    margin: 0,
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'var(--text-primary)',
    letterSpacing: '-0.01em'
  },
  closeButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    color: 'var(--text-muted)',
    padding: '0.5rem',
    borderRadius: 'var(--radius-sm)',
    transition: 'all 0.2s ease'
  },
  content: {
    padding: '1.5rem'
  },
  actions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '0.75rem',
    padding: '1rem 1.5rem',
    borderTop: '1px solid var(--border-light)',
    background: 'var(--bg-primary)'
  }
};
