import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../api/config'
import { School, Mail, Lock, User, Building2, Copy, Check } from 'lucide-react'

const DUMMY_ACCOUNTS = [
  { email: "admin@sunshine.edu", password: "password123", name: "Sarah Johnson", role: "Admin" },
  { email: "teacher@sunshine.edu", password: "password123", name: "Maria Garcia", role: "Teacher" },
]

function DummyAccounts({ onSelectAccount }) {
  return (
    <div style={demoStyles.container}>
      <div style={demoStyles.header}>
        <p style={demoStyles.title}>🎭 Demo Accounts</p>
        <p style={demoStyles.subtitle}>Click to auto-fill</p>
      </div>
      
      <div style={demoStyles.accountsList}>
        {DUMMY_ACCOUNTS.map((account, index) => (
          <button
            key={index}
            onClick={() => onSelectAccount(account.email, account.password)}
            style={demoStyles.accountCard}
          >
            <div style={demoStyles.accountHeader}>
              <span style={demoStyles.accountName}>{account.name}</span>
              <span style={{
                ...demoStyles.roleBadge,
                ...(account.role === 'Admin' ? demoStyles.adminBadge : demoStyles.teacherBadge)
              }}>
                {account.role}
              </span>
            </div>
            <div style={demoStyles.credentials}>
              <div style={demoStyles.credentialText}>{account.email}</div>
              <div style={demoStyles.credentialText}>password123</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

const demoStyles = {
  container: {
    background: 'var(--bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    padding: '2rem',
    border: '1px solid var(--border-light)',
    boxShadow: 'var(--shadow-lg)',
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  header: {
    marginBottom: '1.5rem',
    textAlign: 'center'
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    margin: '0 0 0.5rem 0',
    color: 'var(--text-primary)'
  },
  subtitle: {
    fontSize: '0.875rem',
    margin: 0,
    color: 'var(--text-secondary)'
  },
  accountsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    flex: 1
  },
  accountCard: {
    background: 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)',
    borderRadius: 'var(--radius-lg)',
    padding: '1.5rem',
    color: 'white',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    textAlign: 'left',
    width: '100%',
    boxShadow: 'var(--shadow-md)'
  },
  accountHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem'
  },
  accountName: {
    fontSize: '1.125rem',
    fontWeight: '600'
  },
  roleBadge: {
    fontSize: '0.75rem',
    padding: '0.375rem 0.75rem',
    borderRadius: 'var(--radius-lg)',
    fontWeight: '600'
  },
  adminBadge: {
    background: 'rgba(255, 255, 255, 0.25)',
    color: 'white'
  },
  teacherBadge: {
    background: 'rgba(255, 255, 255, 0.25)',
    color: 'white'
  },
  credentials: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem'
  },
  credentialText: {
    fontSize: '0.875rem',
    fontFamily: 'monospace',
    opacity: 0.95,
    background: 'rgba(255, 255, 255, 0.15)',
    padding: '0.5rem 0.75rem',
    borderRadius: 'var(--radius-sm)'
  }
}

export default function Login() {
  const { login, isAuthenticated, user } = useAuth()
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

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(user.role === 'admin' ? '/admin' : '/teacher', { replace: true })
    }
  }, [isAuthenticated, user, navigate])

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
      const userData = await login(email, password)
      navigate(userData.role === 'admin' ? '/admin' : '/teacher')
    } catch (err) {
      setError(err.message || 'Invalid credentials. Please check your email and password.')
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
      // After signup, trigger a session restore to update auth context
      window.location.href = response.user.role === 'admin' ? '/admin' : '/teacher'
    } catch (err) {
      setError(err.message || 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.contentWrapper}>
        {!isSignup && (
          <div style={styles.demoPanel}>
            <DummyAccounts onSelectAccount={(email, password) => {
              setEmail(email)
              setPassword(password)
            }} />
          </div>
        )}
        
        <div style={styles.card}>
          <div style={styles.header}>
            <div style={styles.logo}>
              <School size={48} />
            </div>
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
                      Teacher
                    </button>
                    <button
                      type="button"
                      style={{ ...styles.roleButton, ...(role === 'admin' ? styles.roleButtonActive : {}) }}
                      onClick={() => setRole('admin')}
                    >
                      Admin
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
    background: 'linear-gradient(135deg, var(--primary-light) 0%, var(--bg-primary) 100%)',
    padding: '2rem'
  },
  contentWrapper: {
    display: 'flex',
    gap: '2rem',
    alignItems: 'stretch',
    maxWidth: '900px',
    width: '100%'
  },
  demoPanel: {
    flex: '0 0 320px',
    display: 'flex'
  },
  card: {
    background: 'var(--bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    padding: '2.5rem',
    flex: 1,
    border: '1px solid var(--border-light)',
    boxShadow: 'var(--shadow-lg)'
  },
  header: {
    textAlign: 'center',
    marginBottom: '2rem'
  },
  logo: {
    color: 'var(--primary)',
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '1rem'
  },
  title: {
    fontSize: '1.75rem',
    fontWeight: '600',
    color: 'var(--text-primary)',
    margin: 0,
    letterSpacing: '-0.02em'
  },
  tabs: {
    display: 'flex',
    marginBottom: '2rem',
    borderRadius: 'var(--radius-lg)',
    overflow: 'hidden',
    border: '1px solid var(--border-light)',
    background: 'var(--bg-tertiary)'
  },
  tab: {
    flex: 1,
    padding: '0.875rem',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
    fontSize: '0.9375rem',
    fontWeight: '500',
    color: 'var(--text-secondary)',
    transition: 'all 0.2s ease'
  },
  tabActive: {
    background: 'var(--primary)',
    color: 'white'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.25rem'
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem'
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: 'var(--text-primary)'
  },
  input: {
    padding: '0.875rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    fontSize: '1rem',
    transition: 'all 0.2s ease'
  },
  roleButtons: {
    display: 'flex',
    gap: '0.75rem'
  },
  roleButton: {
    flex: 1,
    padding: '0.875rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--bg-secondary)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    transition: 'all 0.2s ease',
    color: 'var(--text-secondary)'
  },
  roleButtonActive: {
    background: 'var(--primary)',
    color: 'white',
    borderColor: 'var(--primary)'
  },
  button: {
    padding: '0.875rem',
    background: 'var(--primary)',
    color: 'white',
    border: 'none',
    borderRadius: 'var(--radius-md)',
    fontSize: '1rem',
    fontWeight: '500',
    cursor: 'pointer',
    marginTop: '0.5rem',
    boxShadow: 'var(--shadow-sm)',
    transition: 'all 0.2s ease'
  },
  error: {
    color: '#C62828',
    fontSize: '0.875rem',
    padding: '0.75rem',
    background: 'var(--error-light)',
    borderRadius: 'var(--radius-md)',
    border: '1px solid var(--error)'
  },
  hint: {
    fontSize: '0.8125rem',
    color: 'var(--text-muted)',
    margin: '0.25rem 0 0 0'
  },
  toggle: {
    marginTop: '2rem',
    textAlign: 'center'
  },
  toggleText: {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)'
  },
  toggleLink: {
    background: 'none',
    border: 'none',
    color: 'var(--primary)',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '600',
    padding: 0
  },
  demo: {
    marginTop: '1.5rem',
    padding: '1rem',
    background: 'var(--bg-tertiary)',
    borderRadius: 'var(--radius-md)'
  },
  demoTitle: {
    fontSize: '0.875rem',
    fontWeight: '600',
    marginBottom: '0.5rem',
    color: 'var(--text-primary)'
  },
  demoText: {
    fontSize: '0.8125rem',
    color: 'var(--text-secondary)',
    margin: '0.25rem 0'
  }
}
