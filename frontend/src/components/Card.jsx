export default function Card({ title, children, style }) {
  return (
    <div style={{ ...styles.card, ...style }}>
      {title && <h3 style={styles.title}>{title}</h3>}
      {children}
    </div>
  )
}

const styles = {
  card: {
    background: 'var(--bg-secondary)',
    borderRadius: 'var(--radius-lg)',
    padding: '1.5rem',
    border: '1px solid var(--border-light)',
    boxShadow: 'var(--shadow-sm)',
    transition: 'box-shadow 0.2s ease'
  },
  title: {
    fontSize: '1.0625rem',
    fontWeight: '600',
    marginBottom: '1rem',
    color: 'var(--text-primary)',
    letterSpacing: '-0.01em'
  }
}
