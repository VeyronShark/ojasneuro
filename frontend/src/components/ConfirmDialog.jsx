/**
 * ConfirmDialog component - Confirmation dialog for delete operations
 * Requirements: 4.3 - Confirm deletion before sending DELETE request
 */
import Modal from './Modal';

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
          <div style={styles.warningIcon}>⚠️</div>
        )}
        <p style={styles.message}>{message}</p>
      </div>
    </Modal>
  );
}

const styles = {
  content: {
    textAlign: 'center'
  },
  warningIcon: {
    fontSize: '3rem',
    marginBottom: '1rem'
  },
  message: {
    color: '#495057',
    fontSize: '1rem',
    margin: 0,
    lineHeight: 1.5
  },
  button: {
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    fontSize: '0.875rem',
    fontWeight: '500',
    cursor: 'pointer',
    border: 'none',
    transition: 'background-color 0.2s'
  },
  cancelButton: {
    background: '#f1f3f5',
    color: '#495057'
  },
  confirmButton: {
    color: 'white'
  },
  dangerButton: {
    background: '#dc3545'
  },
  primaryButton: {
    background: '#3498db'
  }
};
