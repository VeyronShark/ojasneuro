import { useParams } from 'react-router-dom'
import Layout from '../components/Layout'
import Card from '../components/Card'
import { DUMMY_DATA } from '../data/dummyData'

export default function ChildProfile({ user }) {
  const { childId } = useParams()
  const child = DUMMY_DATA.students.find(s => s.id === parseInt(childId))
  const classData = DUMMY_DATA.classes.find(c => c.id === child.classId)

  if (!child) return <Layout user={user}><div>Child not found</div></Layout>

  const getTrendIcon = (trend) => {
    if (trend === 'up') return '↗️'
    if (trend === 'down') return '↘️'
    return '→'
  }

  const getSkillLevel = (level) => {
    const colors = {
      high: '#28a745',
      medium: '#ffc107',
      low: '#dc3545'
    }
    return colors[level] || '#6c757d'
  }

  const getInsight = () => {
    const lowSkills = Object.entries(child.skills)
      .filter(([_, level]) => level === 'low')
      .map(([skill]) => skill)

    if (lowSkills.includes('patience')) {
      return "This child tends to complete sensory puzzles but often quits patience tasks early. You might try slow, repetitive classroom activities like pouring grains or using a sand timer."
    }
    if (child.engagement === 'low') {
      return "This child shows lower engagement with the app. Consider checking in with parents about app usage and exploring what activities might interest the child more."
    }
    return "This child shows good engagement across activities. Continue encouraging balanced skill development through varied Montessori exercises."
  }

  return (
    <Layout user={user}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.name}>{child.name}</h1>
          <div style={styles.meta}>
            {classData.name} • Age {child.age}
          </div>
        </div>
      </div>

      <div style={styles.grid}>
        <Card title="App Engagement">
          <div style={styles.statValue}>{child.avgSessionsPerDay}</div>
          <div style={styles.statLabel}>Avg. sessions per day</div>
          <div style={styles.trend}>
            Trend: {getTrendIcon(child.trend)} {child.trend}
          </div>
        </Card>

        <Card title="Skill Profile" style={{ gridColumn: 'span 2' }}>
          <div style={styles.skillGrid}>
            {Object.entries(child.skills).map(([skill, level]) => (
              <div key={skill} style={styles.skillRow}>
                <div style={styles.skillName}>
                  {skill.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div style={styles.skillBar}>
                  <div
                    style={{
                      ...styles.skillFill,
                      width: level === 'high' ? '100%' : level === 'medium' ? '60%' : '30%',
                      background: getSkillLevel(level)
                    }}
                  />
                </div>
                <div style={styles.skillLevel}>{level}</div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Classroom Insight" style={{ gridColumn: 'span 3' }}>
          <p style={styles.insight}>{getInsight()}</p>
        </Card>

        <Card title="Weekly Activity" style={{ gridColumn: 'span 3' }}>
          <div style={styles.weeklyChart}>
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
              <div key={i} style={styles.dayColumn}>
                <div style={styles.barContainer}>
                  <div
                    style={{
                      ...styles.bar,
                      height: `${child.weeklyActivity[i] * 30}px`,
                      background: child.weeklyActivity[i] === 0 ? '#e9ecef' : '#4a90e2'
                    }}
                  />
                </div>
                <div style={styles.dayLabel}>{day}</div>
                <div style={styles.sessionCount}>{child.weeklyActivity[i]}</div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <button style={styles.downloadBtn}>
        📄 Download Summary for PTM (PDF)
      </button>
    </Layout>
  )
}

const styles = {
  header: {
    marginBottom: '2rem'
  },
  name: {
    fontSize: '2rem',
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: '0.5rem'
  },
  meta: {
    fontSize: '1rem',
    color: '#6c757d'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1.5rem',
    marginBottom: '1.5rem'
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
  trend: {
    marginTop: '0.75rem',
    fontSize: '0.875rem',
    color: '#495057'
  },
  skillGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem'
  },
  skillRow: {
    display: 'grid',
    gridTemplateColumns: '150px 1fr 80px',
    alignItems: 'center',
    gap: '1rem'
  },
  skillName: {
    fontSize: '0.875rem',
    fontWeight: '500',
    textTransform: 'capitalize'
  },
  skillBar: {
    height: '8px',
    background: '#f1f3f5',
    borderRadius: '4px',
    overflow: 'hidden'
  },
  skillFill: {
    height: '100%',
    borderRadius: '4px'
  },
  skillLevel: {
    fontSize: '0.75rem',
    color: '#6c757d',
    textTransform: 'capitalize',
    textAlign: 'right'
  },
  insight: {
    fontSize: '0.9375rem',
    lineHeight: '1.6',
    color: '#495057'
  },
  weeklyChart: {
    display: 'flex',
    gap: '1.5rem',
    justifyContent: 'center',
    padding: '1rem 0'
  },
  dayColumn: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '0.5rem'
  },
  barContainer: {
    height: '100px',
    display: 'flex',
    alignItems: 'flex-end'
  },
  bar: {
    width: '40px',
    borderRadius: '4px 4px 0 0',
    minHeight: '4px'
  },
  dayLabel: {
    fontSize: '0.75rem',
    color: '#6c757d',
    fontWeight: '500'
  },
  sessionCount: {
    fontSize: '0.875rem',
    color: '#495057'
  },
  downloadBtn: {
    padding: '0.75rem 1.5rem',
    background: '#4a90e2',
    color: 'white',
    borderRadius: '4px',
    fontSize: '0.9375rem',
    fontWeight: '500'
  }
}
