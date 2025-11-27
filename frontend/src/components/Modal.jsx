/**
 * Modal component - Reusable modal wrapper
 * Requirements: 2.1, 3.2 - Forms for adding classrooms and students
 */
import { useEffect, useCallback } from 'react';

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
            ×
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
    background: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '1rem'
  },
  modal: {
    background: 'white',
    borderRadius: '8px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'auto',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 1.5rem',
    borderBottom: '1px solid #e1e4e8'
  },
  title: {
    margin: 0,
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#2c3e50'
  },
  closeButton: {
    background: 'transparent',
    border: 'none',
    fontSize: '1.5rem',
    cursor: 'pointer',
    color: '#6c757d',
    padding: '0.25rem',
    lineHeight: 1
  },
  content: {
    padding: '1.5rem'
  },
  actions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '0.75rem',
    padding: '1rem 1.5rem',
    borderTop: '1px solid #e1e4e8',
    background: '#f8f9fa'
  }
};
