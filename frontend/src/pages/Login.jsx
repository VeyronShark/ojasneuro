import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../api/config'
import { DUMMY_DATA } from '../data/dummyData'

export default function Login({ setUser }) {
  const [isSignup, setIsSignup] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState('teacher')
  const [schoolId, setSchoolId] = useState('')
  const [schoolName, setSchoolName] = useState('')
  const [schools, setSchools] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (isSignup) {
      authAPI.getSchools()
        .then(res => setSchools(res.schools || []))
        .catch(() => setSchools([]))
    }
  }, [isSignup])

  const resetForm = () => {
    setEmail('')
    setPassword('')
    setConfirmPassword('')
    setName('')
    setRole('teacher')
    setSchoolId('')
    setSchoolName('')
    setError('')
  }

  const toggleMode = () => {
    resetForm()
    setIsSignup(!isSignup)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await authAPI.login(email, password)
      localStorage.setItem('token', response.token)
      setUser(response.user)
      navigate(response.user.role === 'admin' ? '/admin' : '/teacher')
    } catch (err) {
      // Fallback to dummy data for demo
      const users = Object.values(DUMMY_DATA.users)
      const user = users.find(u => u.email === email && u.password === password)
      if (user) {
        setUser(user)
        navigate(user.role === 'admin' ? '/admin' : '/teacher')
      } else {
        setError(err.message || 'Invalid credentials')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSignup = async (e) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    if (role === 'teacher' && !schoolId) {
      setError('Please select a school')
      return
    }
    if (role === 'admin' && !schoolName.trim()) {
      setError('Please enter your school name')
      return
    }

    setLoading(true)
    try {
      const response = await authAPI.signup({
        email,
        password,
        name,
        role,
        school_id: role === 'teacher' ? parseInt(schoolId) : null,
        school_name: role === 'admin' ? schoolName : null
      })
      localStorage.setItem('token', response.token)
      setUser(response.user)
      navigate(response.user.role === 'admin' ? '/admin' : '/teacher')
    } catch (err) {
      setError(err.message || 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <span style={styles.logo}>🏫</span>
          <h1 style={styles.title}>{isSignup ? 'Create Account' : 'Welcome Back'}</h1>
        </div>

        <div style={styles.tabs}>
          <button
            style={{ ...styles.tab, ...(isSignup ? {} : styles.tabActive) }}
            onClick={() => !loading && setIsSignup(false)}
          >
            Login
          </button>
          <button
            style={{ ...styles.tab, ...(isSignup ? styles.tabActive : {}) }}
            onClick={() => !loading && setIsSignup(true)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={isSignup ? handleSignup : handleLogin} style={styles.form}>
          {isSignup && (
            <div style={styles.field}>
              <label style={styles.label}>Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={styles.input}
                placeholder="Enter your full name"
                required
              />
            </div>
          )}

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
              placeholder={isSignup ? 'At least 6 characters' : 'Enter your password'}
              required
            />
          </div>

          {isSignup && (
            <>
              <div style={styles.field}>
                <label style={styles.label}>Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  style={styles.input}
                  placeholder="Confirm your password"
                  required
                />
              </div>

              <div style={styles.field}>
                <label style={styles.label}>I am a...</label>
                <div style={styles.roleButtons}>
                  <button
                    type="button"
                    style={{ ...styles.roleButton, ...(role === 'teacher' ? styles.roleButtonActive : {}) }}
                    onClick={() => setRole('teacher')}
                  >
                    👩‍🏫 Teacher
                  </button>
                  <button
                    type="button"
                    style={{ ...styles.roleButton, ...(role === 'admin' ? styles.roleButtonActive : {}) }}
                    onClick={() => setRole('admin')}
                  >
                    👔 Admin
                  </button>
                </div>
              </div>

              {role === 'teacher' && (
                <div style={styles.field}>
                  <label style={styles.label}>Select Your School</label>
                  {schools.length > 0 ? (
                    <select
                      value={schoolId}
                      onChange={(e) => setSchoolId(e.target.value)}
                      style={styles.input}
                      required
                    >
                      <option value="">-- Select a school --</option>
                      {schools.map(school => (
                        <option key={school.id} value={school.id}>{school.name}</option>
                      ))}
                    </select>
                  ) : (
                    <p style={styles.hint}>No schools yet. Sign up as admin to create one.</p>
                  )}
                </div>
              )}

              {role === 'admin' && (
                <div style={styles.field}>
                  <label style={styles.label}>School Name</label>
                  <input
                    type="text"
                    value={schoolName}
                    onChange={(e) => setSchoolName(e.target.value)}
                    style={styles.input}
                    placeholder="Enter your school name"
                    required
                  />
                  <p style={styles.hint}>This creates a new school with you as admin.</p>
                </div>
              )}
            </>
          )}

          {error && <div style={styles.error}>{error}</div>}

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? (isSignup ? 'Creating...' : 'Logging in...') : (isSignup ? 'Sign Up' : 'Login')}
          </button>
        </form>

        <div style={styles.toggle}>
          <span style={styles.toggleText}>
            {isSignup ? 'Already have an account? ' : "Don't have an account? "}
          </span>
          <button style={styles.toggleLink} onClick={toggleMode} disabled={loading}>
            {isSignup ? 'Login' : 'Sign Up'}
          </button>
        </div>

        {!isSignup && (
          <div style={styles.demo}>
            <p style={styles.demoTitle}>Demo Credentials:</p>
            <p style={styles.demoText}>Admin: admin@school.com / admin123</p>
            <p style={styles.demoText}>Teacher: teacher@school.com / teacher123</p>
          </div>
        )}
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
    background: '#f8f9fa',
    padding: '1rem'
  },
  card: {
    background: 'white',
    borderRadius: '8px',
    padding: '2rem',
    width: '100%',
    maxWidth: '420px',
    border: '1px solid #e1e4e8'
  },
  header: {
    textAlign: 'center',
    marginBottom: '1.5rem'
  },
  logo: {
    fontSize: '2.5rem',
    display: 'block',
    marginBottom: '0.5rem'
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#2c3e50',
    margin: 0
  },
  tabs: {
    display: 'flex',
    marginBottom: '1.5rem',
    borderRadius: '6px',
    overflow: 'hidden',
    border: '1px solid #e1e4e8'
  },
  tab: {
    flex: 1,
    padding: '0.75rem',
    border: 'none',
    background: '#f8f9fa',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#6c757d',
    transition: 'all 0.2s'
  },
  tabActive: {
    background: '#4a90e2',
    color: 'white'
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
  roleButtons: {
    display: 'flex',
    gap: '0.5rem'
  },
  roleButton: {
    flex: 1,
    padding: '0.75rem',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    background: 'white',
    cursor: 'pointer',
    fontSize: '0.875rem',
    transition: 'all 0.2s'
  },
  roleButtonActive: {
    background: '#4a90e2',
    color: 'white',
    borderColor: '#4a90e2'
  },
  button: {
    padding: '0.75rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '1rem',
    fontWeight: '500',
    cursor: 'pointer',
    marginTop: '0.5rem'
  },
  error: {
    color: '#dc3545',
    fontSize: '0.875rem',
    padding: '0.5rem',
    background: '#f8d7da',
    borderRadius: '4px'
  },
  hint: {
    fontSize: '0.75rem',
    color: '#6c757d',
    margin: '0.25rem 0 0 0'
  },
  toggle: {
    marginTop: '1.5rem',
    textAlign: 'center'
  },
  toggleText: {
    fontSize: '0.875rem',
    color: '#6c757d'
  },
  toggleLink: {
    background: 'none',
    border: 'none',
    color: '#4a90e2',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    padding: 0
  },
  demo: {
    marginTop: '1.5rem',
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
