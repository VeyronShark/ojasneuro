import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Card from '../components/Card'
import { DUMMY_DATA } from '../data/dummyData'

export default function TeacherDashboard({ user }) {
  const navigate = useNavigate()
  const userClassIds = user.classIds || []
  const classes = userClassIds.length > 0 
    ? DUMMY_DATA.classes.filter(c => userClassIds.includes(c.id))
    : DUMMY_DATA.classes // Show all classes if no classIds (new user)
  const students = userClassIds.length > 0
    ? DUMMY_DATA.students.filter(s => userClassIds.includes(s.classId))
    : DUMMY_DATA.students // Show all students if no classIds (new user)
  
  const activeThisWeek = students.filter(s => {
    const lastActive = new Date(s.lastActive)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return lastActive >= weekAgo
  }).length

  const avgPuzzles = (students.reduce((sum, s) => sum + s.avgSessionsPerDay, 0) / students.length).toFixed(1)
  
  const skillCounts = {}
  students.forEach(s => {
    Object.entries(s.skills).forEach(([skill, level]) => {
      if (level === 'high') {
        skillCounts[skill] = (skillCounts[skill] || 0) + 1
      }
    })
  })
  const topSkill = Object.entries(skillCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'sensory'

  return (
    <Layout user={user} title="Teacher Overview">
      <div style={styles.alerts}>
        {DUMMY_DATA.teacherAlerts.map((alert, i) => (
          <div key={i} style={styles.alert}>
            ⚠️ {alert}
          </div>
        ))}
      </div>

      <div style={styles.grid}>
        <Card title="Class Usage This Week">
          <div style={styles.statValue}>{Math.round((activeThisWeek / students.length) * 100)}%</div>
          <div style={styles.statLabel}>
            {activeThisWeek} of {students.length} children used the app
          </div>
        </Card>

        <Card title="Avg. Puzzles Per Day">
          <div style={styles.statValue}>{avgPuzzles}</div>
          <div style={styles.statLabel}>Across your classes</div>
        </Card>

        <Card title="Dominant Skill Theme">
          <div style={styles.skillBadge}>{topSkill.replace(/([A-Z])/g, ' $1').trim()}</div>
          <div style={styles.statLabel}>Most reinforced in puzzles</div>
        </Card>
      </div>

      <Card title="Your Classes" style={{ marginTop: '1.5rem' }}>
        <div style={styles.classList}>
          {classes.map(cls => (
            <button
              key={cls.id}
              onClick={() => navigate(`/class/${cls.id}`)}
              style={styles.classCard}
            >
              <div style={styles.className}>{cls.name}</div>
              <div style={styles.classInfo}>{cls.studentCount} students</div>
            </button>
          ))}
        </div>
      </Card>
    </Layout>
  )
}

const styles = {
  alerts: {
    marginBottom: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  },
  alert: {
    padding: '1rem',
    background: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: '4px',
    fontSize: '0.875rem',
    color: '#856404'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1.5rem'
  },
  statValue: {
    fontSize: '2.5rem',
    fontWeight: '600',
    color: '#4a90e2',
    marginBottom: '0.5rem'
  },
  statLabel: {
    fontSize: '0.875rem',
    color: '#6c757d'
  },
  skillBadge: {
    display: 'inline-block',
    padding: '0.5rem 1rem',
    background: '#e7f3ff',
    color: '#4a90e2',
    borderRadius: '20px',
    fontSize: '1rem',
    fontWeight: '500',
    textTransform: 'capitalize',
    marginBottom: '0.5rem'
  },
  classList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '1rem'
  },
  classCard: {
    padding: '1.5rem',
    background: '#f8f9fa',
    border: '1px solid #e1e4e8',
    borderRadius: '8px',
    textAlign: 'left'
  },
  className: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: '0.5rem'
  },
  classInfo: {
    fontSize: '0.875rem',
    color: '#6c757d'
  }
}
