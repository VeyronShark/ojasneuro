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
    background: 'white',
    borderRadius: '8px',
    padding: '1.5rem',
    border: '1px solid #e1e4e8'
  },
  title: {
    fontSize: '1rem',
    fontWeight: '600',
    marginBottom: '1rem',
    color: '#2c3e50'
  }
}
