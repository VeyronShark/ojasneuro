import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { DUMMY_DATA } from '../data/dummyData'

export default function Login({ setUser }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleLogin = (e) => {
    e.preventDefault()
    setError('')

    const users = Object.values(DUMMY_DATA.users)
    const user = users.find(u => u.email === email && u.password === password)

    if (user) {
      setUser(user)
      navigate(user.role === 'admin' ? '/admin' : '/teacher')
    } else {
      setError('Invalid credentials')
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <span style={styles.logo}>{DUMMY_DATA.school.logo}</span>
          <h1 style={styles.title}>{DUMMY_DATA.school.name}</h1>
        </div>

        <form onSubmit={handleLogin} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              placeholder="Enter your email"
              required
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              placeholder="Enter your password"
              required
            />
          </div>

          {error && <div style={styles.error}>{error}</div>}

          <button type="submit" style={styles.button}>
            Login
          </button>
        </form>

        <div style={styles.demo}>
          <p style={styles.demoTitle}>Demo Credentials:</p>
          <p style={styles.demoText}>Admin: admin@school.com / admin123</p>
          <p style={styles.demoText}>Teacher: teacher@school.com / teacher123</p>
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#f8f9fa'
  },
  card: {
    background: 'white',
    borderRadius: '8px',
    padding: '2rem',
    width: '100%',
    maxWidth: '400px',
    border: '1px solid #e1e4e8'
  },
  header: {
    textAlign: 'center',
    marginBottom: '2rem'
  },
  logo: {
    fontSize: '3rem',
    display: 'block',
    marginBottom: '0.5rem'
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#2c3e50'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem'
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem'
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#495057'
  },
  input: {
    padding: '0.75rem',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '1rem'
  },
  button: {
    padding: '0.75rem',
    background: '#4a90e2',
    color: 'white',
    borderRadius: '4px',
    fontSize: '1rem',
    fontWeight: '500',
    marginTop: '0.5rem'
  },
  error: {
    color: '#dc3545',
    fontSize: '0.875rem',
    padding: '0.5rem',
    background: '#f8d7da',
    borderRadius: '4px'
  },
  demo: {
    marginTop: '2rem',
    padding: '1rem',
    background: '#f8f9fa',
    borderRadius: '4px'
  },
  demoTitle: {
    fontSize: '0.875rem',
    fontWeight: '600',
    marginBottom: '0.5rem',
    color: '#495057'
  },
  demoText: {
    fontSize: '0.75rem',
    color: '#6c757d',
    margin: '0.25rem 0'
  }
}
