import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { 
  Home, 
  Users, 
  BookOpen, 
  GraduationCap, 
  MessageCircle, 
  Lightbulb, 
  LogOut,
  School
} from 'lucide-react'

export default function Layout({ children, title }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  
  // School info from user context or defaults
  const school = {
    name: user?.school_name || 'Montessori School',
    logo: <School size={24} />
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  // Check if a path is active (exact match or starts with for nested routes)
  const isActive = (path) => {
    if (path === '/admin' || path === '/teacher') {
      return location.pathname === path
    }
    return location.pathname.startsWith(path)
  }

  // Get nav button style with active state
  const getNavBtnStyle = (path) => ({
    ...styles.navBtn,
    ...(isActive(path) ? styles.navBtnActive : {})
  })

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.branding}>
            <span style={styles.logo}>{school.logo}</span>
            <span style={styles.schoolName}>{school.name}</span>
          </div>
          <div style={styles.userInfo}>
            <div style={styles.userDetails}>
              <span style={styles.userName}>{user?.name || 'User'}</span>
              <span style={styles.role}>{user?.role || 'guest'}</span>
            </div>
            <button onClick={handleLogout} style={styles.logoutBtn}>
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <nav style={styles.nav}>
        <button 
          onClick={() => navigate(user?.role === 'admin' ? '/admin' : '/teacher')} 
          style={getNavBtnStyle(user?.role === 'admin' ? '/admin' : '/teacher')}
        >
          <Home size={18} />
          <span>Home</span>
        </button>
        {user?.role === 'admin' && (
          <>
            <button onClick={() => navigate('/admin/teachers')} style={getNavBtnStyle('/admin/teachers')}>
              <Users size={18} />
              <span>Teachers</span>
            </button>
            <button onClick={() => navigate('/admin/classes')} style={getNavBtnStyle('/admin/classes')}>
              <BookOpen size={18} />
              <span>Classes</span>
            </button>
            <button onClick={() => navigate('/admin/students')} style={getNavBtnStyle('/admin/students')}>
              <GraduationCap size={18} />
              <span>Students</span>
            </button>
          </>
        )}
        {user?.role === 'teacher' && (
          <>
            <button onClick={() => navigate('/skills')} style={getNavBtnStyle('/skills')}>
              <Lightbulb size={18} />
              <span>Skill Suggestions</span>
            </button>
          </>
        )}
        <button onClick={() => navigate('/communication')} style={getNavBtnStyle('/communication')}>
          <MessageCircle size={18} />
          <span>Communication</span>
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
    background: 'var(--bg-primary)'
  },
  header: {
    background: 'var(--bg-secondary)',
    borderBottom: '1px solid var(--border-light)',
    padding: '1rem 2rem',
    boxShadow: 'var(--shadow-sm)'
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
    color: 'var(--primary)',
    display: 'flex',
    alignItems: 'center'
  },
  schoolName: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: 'var(--text-primary)'
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem'
  },
  userDetails: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end'
  },
  userName: {
    fontWeight: '500',
    fontSize: '0.9375rem',
    color: 'var(--text-primary)'
  },
  role: {
    color: 'var(--text-muted)',
    fontSize: '0.8125rem',
    textTransform: 'capitalize'
  },
  logoutBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.5rem 1rem',
    background: 'var(--bg-tertiary)',
    borderRadius: 'var(--radius-md)',
    fontSize: '0.875rem',
    color: 'var(--text-secondary)',
    fontWeight: '500',
    border: '1px solid var(--border-light)'
  },
  nav: {
    background: 'var(--bg-secondary)',
    borderBottom: '1px solid var(--border-light)',
    padding: '0 2rem',
    display: 'flex',
    gap: '0.25rem'
  },
  navBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.875rem 1.25rem',
    color: 'var(--text-secondary)',
    fontSize: '0.875rem',
    borderBottom: '3px solid transparent',
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s ease'
  },
  navBtnActive: {
    color: 'var(--primary)',
    borderBottom: '3px solid var(--primary)',
    background: 'var(--primary-light)',
    fontWeight: '600'
  },
  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem'
  },
  title: {
    fontSize: '1.875rem',
    fontWeight: '600',
    marginBottom: '1.5rem',
    color: 'var(--text-primary)',
    letterSpacing: '-0.02em'
  }
}
