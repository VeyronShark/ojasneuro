import { useNavigate } from 'react-router-dom'
import { DUMMY_DATA } from '../data/dummyData'

export default function Layout({ children, user, title }) {
  const navigate = useNavigate()
  const school = DUMMY_DATA.school

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.branding}>
            <span style={styles.logo}>{school.logo}</span>
            <span style={styles.schoolName}>{school.name}</span>
          </div>
          <div style={styles.userInfo}>
            <span style={styles.userName}>{user.name}</span>
            <span style={styles.role}>({user.role})</span>
            <button onClick={() => navigate('/login')} style={styles.logoutBtn}>
              Logout
            </button>
          </div>
        </div>
      </header>

      <nav style={styles.nav}>
        <button onClick={() => navigate(user.role === 'admin' ? '/admin' : '/teacher')} style={styles.navBtn}>
          Home
        </button>
        {user.role === 'teacher' && (
          <>
            <button onClick={() => navigate('/skills')} style={styles.navBtn}>
              Skill Suggestions
            </button>
          </>
        )}
        <button onClick={() => navigate('/communication')} style={styles.navBtn}>
          Parent Communication
        </button>
      </nav>

      <main style={styles.main}>
        {title && <h1 style={styles.title}>{title}</h1>}
        {children}
      </main>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    background: '#f8f9fa'
  },
  header: {
    background: 'white',
    borderBottom: '1px solid #e1e4e8',
    padding: '1rem 2rem'
  },
  headerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  branding: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem'
  },
  logo: {
    fontSize: '1.5rem'
  },
  schoolName: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: '#2c3e50'
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  },
  userName: {
    fontWeight: '500'
  },
  role: {
    color: '#6c757d',
    fontSize: '0.875rem'
  },
  logoutBtn: {
    marginLeft: '1rem',
    padding: '0.5rem 1rem',
    background: '#f1f3f5',
    borderRadius: '4px',
    fontSize: '0.875rem',
    color: '#495057'
  },
  nav: {
    background: 'white',
    borderBottom: '1px solid #e1e4e8',
    padding: '0 2rem',
    display: 'flex',
    gap: '0.5rem'
  },
  navBtn: {
    padding: '0.75rem 1rem',
    color: '#495057',
    fontSize: '0.875rem',
    borderBottom: '2px solid transparent'
  },
  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem'
  },
  title: {
    fontSize: '1.75rem',
    fontWeight: '600',
    marginBottom: '1.5rem',
    color: '#2c3e50'
  }
}
