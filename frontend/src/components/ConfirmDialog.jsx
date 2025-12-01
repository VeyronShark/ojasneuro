import Modal from './Modal'
import { AlertTriangle } from 'lucide-react'

/**
 * ConfirmDialog component - Confirmation dialog for delete operations
 * Requirements: 4.3 - Confirm deletion before sending DELETE request
 */
export default function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger'
}) {
  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  const confirmButtonStyle = {
    ...styles.button,
    ...styles.confirmButton,
    ...(variant === 'danger' ? styles.dangerButton : styles.primaryButton)
  };

  const actions = (
    <>
      <button onClick={onClose} style={{ ...styles.button, ...styles.cancelButton }}>
        {cancelText}
      </button>
      <button onClick={handleConfirm} style={confirmButtonStyle}>
        {confirmText}
      </button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      actions={actions}
      size="small"
    >
      <div style={styles.content}>
        {variant === 'danger' && (
          <div style={styles.warningIcon}>
            <AlertTriangle size={48} color="var(--error)" />
          </div>
        )}
        <p style={styles.message}>{message}</p>
      </div>
    </Modal>
  );
}

const styles = {
  content: {
    textAlign: 'center',
    padding: '1rem 0'
  },
  warningIcon: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '1rem'
  },
  message: {
    color: 'var(--text-secondary)',
    fontSize: '1rem',
    margin: 0,
    lineHeight: 1.6
  },
  button: {
    padding: '0.625rem 1.25rem',
    borderRadius: 'var(--radius-md)',
    fontSize: '0.875rem',
    fontWeight: '500',
    cursor: 'pointer',
    border: 'none',
    transition: 'all 0.2s ease'
  },
  cancelButton: {
    background: 'var(--bg-tertiary)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border)'
  },
  confirmButton: {
    color: 'white'
  },
  dangerButton: {
    background: 'var(--error)'
  },
  primaryButton: {
    background: 'var(--primary)'
  }
};
