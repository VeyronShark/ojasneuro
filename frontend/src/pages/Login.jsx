import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../api/config'

const DUMMY_ACCOUNTS = [
  { email: "sarah.johnson@sunshine.edu", password: "password123", name: "Sarah Johnson", role: "Admin", school: "Sunshine Montessori" },
  { email: "maria.garcia@sunshine.edu", password: "password123", name: "Maria Garcia", role: "Teacher", school: "Sunshine Montessori" },
  { email: "emily.chen@greenvalley.edu", password: "password123", name: "Emily Chen", role: "Admin", school: "Green Valley Montessori" },
  { email: "david.wilson@littlestars.edu", password: "password123", name: "David Wilson", role: "Teacher", school: "Little Stars Learning" },
  { email: "lisa.anderson@rainbow.edu", password: "password123", name: "Lisa Anderson", role: "Teacher", school: "Rainbow Bridge Academy" },
  { email: "michael.brown@brightminds.edu", password: "password123", name: "Michael Brown", role: "Admin", school: "Bright Minds Montessori" },
  { email: "jennifer.lee@peaceful.edu", password: "password123", name: "Jennifer Lee", role: "Teacher", school: "Peaceful Pathways" },
  { email: "robert.taylor@discovery.edu", password: "password123", name: "Robert Taylor", role: "Teacher", school: "Discovery Kids Academy" },
  { email: "amanda.white@harmony.edu", password: "password123", name: "Amanda White", role: "Admin", school: "Harmony House Learning" },
  { email: "james.martin@wisdom.edu", password: "password123", name: "James Martin", role: "Teacher", school: "Wisdom Tree Montessori" },
]

function DummyAccounts({ onSelectAccount }) {
  const [copiedIndex, setCopiedIndex] = useState(null)
  const [expanded, setExpanded] = useState(false)

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedIndex(index)
      setTimeout(() => setCopiedIndex(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const displayedAccounts = expanded ? DUMMY_ACCOUNTS : DUMMY_ACCOUNTS.slice(0, 3)

  return (
    <div style={demoStyles.container}>
      <div style={demoStyles.header}>
        <p style={demoStyles.title}>🎭 Demo Accounts</p>
        <p style={demoStyles.subtitle}>Click any account to auto-fill the login form</p>
      </div>
      
      <div style={demoStyles.accountsList}>
        {displayedAccounts.map((account, index) => (
          <div key={index} style={demoStyles.accountCard}>
            <div style={demoStyles.accountInfo}>
              <div style={demoStyles.accountHeader}>
                <span style={demoStyles.accountName}>{account.name}</span>
                <span style={{
                  ...demoStyles.roleBadge,
                  ...(account.role === 'Admin' ? demoStyles.adminBadge : demoStyles.teacherBadge)
                }}>
                  {account.role === 'Admin' ? '👔' : '👩‍🏫'} {account.role}
                </span>
              </div>
              <div style={demoStyles.accountSchool}>{account.school}</div>
              <div style={demoStyles.credentials}>
                <div style={demoStyles.credentialRow}>
                  <span style={demoStyles.credentialLabel}>Email:</span>
                  <code style={demoStyles.credentialValue}>{account.email}</code>
                  <button
                    onClick={() => copyToClipboard(account.email, `email-${index}`)}
                    style={demoStyles.copyButton}
                    title="Copy email"
                  >
                    {copiedIndex === `email-${index}` ? '✓' : '📋'}
                  </button>
                </div>
                <div style={demoStyles.credentialRow}>
                  <span style={demoStyles.credentialLabel}>Pass:</span>
                  <code style={demoStyles.credentialValue}>{account.password}</code>
                  <button
                    onClick={() => copyToClipboard(account.password, `pass-${index}`)}
                    style={demoStyles.copyButton}
                    title="Copy password"
                  >
                    {copiedIndex === `pass-${index}` ? '✓' : '📋'}
                  </button>
                </div>
              </div>
            </div>
            <button
              onClick={() => onSelectAccount(account.email, account.password)}
              style={demoStyles.useButton}
            >
              Use Account
            </button>
          </div>
        ))}
      </div>

      {DUMMY_ACCOUNTS.length > 3 && (
        <button
          onClick={() => setExpanded(!expanded)}
          style={demoStyles.expandButton}
        >
          {expanded ? '▲ Show Less' : `▼ Show All ${DUMMY_ACCOUNTS.length} Accounts`}
        </button>
      )}
    </div>
  )
}

const demoStyles = {
  container: {
    marginTop: '1.5rem',
    padding: '1rem',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    borderRadius: '8px',
    color: 'white'
  },
  header: {
    marginBottom: '1rem',
    textAlign: 'center'
  },
  title: {
    fontSize: '1rem',
    fontWeight: '600',
    margin: '0 0 0.25rem 0'
  },
  subtitle: {
    fontSize: '0.75rem',
    margin: 0,
    opacity: 0.9
  },
  accountsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  },
  accountCard: {
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '6px',
    padding: '0.75rem',
    color: '#2c3e50'
  },
  accountInfo: {
    marginBottom: '0.5rem'
  },
  accountHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.25rem'
  },
  accountName: {
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#2c3e50'
  },
  roleBadge: {
    fontSize: '0.7rem',
    padding: '0.15rem 0.5rem',
    borderRadius: '12px',
    fontWeight: '500'
  },
  adminBadge: {
    background: '#e3f2fd',
    color: '#1976d2'
  },
  teacherBadge: {
    background: '#f3e5f5',
    color: '#7b1fa2'
  },
  accountSchool: {
    fontSize: '0.7rem',
    color: '#6c757d',
    marginBottom: '0.5rem'
  },
  credentials: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem'
  },
  credentialRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    fontSize: '0.75rem'
  },
  credentialLabel: {
    fontWeight: '500',
    color: '#6c757d',
    minWidth: '35px'
  },
  credentialValue: {
    flex: 1,
    background: '#f8f9fa',
    padding: '0.25rem 0.5rem',
    borderRadius: '3px',
    fontSize: '0.7rem',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap'
  },
  copyButton: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '0.875rem',
    padding: '0.25rem',
    opacity: 0.7,
    transition: 'opacity 0.2s'
  },
  useButton: {
    width: '100%',
    padding: '0.5rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '0.8rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background 0.2s'
  },
  expandButton: {
    width: '100%',
    marginTop: '0.75rem',
    padding: '0.5rem',
    background: 'rgba(255, 255, 255, 0.2)',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '0.8rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background 0.2s'
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

        {!isSignup && <DummyAccounts onSelectAccount={(email, password) => {
          setEmail(email)
          setPassword(password)
        }} />}
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
