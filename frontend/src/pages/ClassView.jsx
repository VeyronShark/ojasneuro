import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Card from '../components/Card'
import { DUMMY_DATA } from '../data/dummyData'

export default function ClassView({ user }) {
  const { classId } = useParams()
  const navigate = useNavigate()
  const [filter, setFilter] = useState('all')

  const classData = DUMMY_DATA.classes.find(c => c.id === parseInt(classId))
  let students = DUMMY_DATA.students.filter(s => s.classId === parseInt(classId))

  if (filter === 'low') {
    students = students.filter(s => s.engagement === 'low')
  } else if (filter === 'struggling') {
    students = students.filter(s => 
      Object.values(s.skills).some(level => level === 'low')
    )
  }

  const getEngagementColor = (level) => {
    if (level === 'high') return '#28a745'
    if (level === 'medium') return '#ffc107'
    return '#dc3545'
  }

  const getTrendIcon = (trend) => {
    if (trend === 'up') return '↗️'
    if (trend === 'down') return '↘️'
    return '→'
  }

  return (
    <Layout user={user} title={classData?.name}>
      <div style={styles.filters}>
        <button
          onClick={() => setFilter('all')}
          style={filter === 'all' ? styles.filterActive : styles.filterBtn}
        >
          All Students
        </button>
        <button
          onClick={() => setFilter('low')}
          style={filter === 'low' ? styles.filterActive : styles.filterBtn}
        >
          Low Engagement
        </button>
        <button
          onClick={() => setFilter('struggling')}
          style={filter === 'struggling' ? styles.filterActive : styles.filterBtn}
        >
          Struggling with Skills
        </button>
      </div>

      <Card>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Child Name</th>
              <th style={styles.th}>Engagement</th>
              <th style={styles.th}>Avg. Sessions/Day</th>
              <th style={styles.th}>Trend</th>
              <th style={styles.th}>Last Active</th>
              <th style={styles.th}>Weekly Activity</th>
            </tr>
          </thead>
          <tbody>
            {students.map(student => (
              <tr
                key={student.id}
                onClick={() => navigate(`/child/${student.id}`)}
                style={styles.row}
              >
                <td style={styles.td}>{student.name}</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    background: getEngagementColor(student.engagement) + '20',
                    color: getEngagementColor(student.engagement)
                  }}>
                    {student.engagement}
                  </span>
                </td>
                <td style={styles.td}>{student.avgSessionsPerDay}</td>
                <td style={styles.td}>{getTrendIcon(student.trend)}</td>
                <td style={styles.td}>{student.lastActive}</td>
                <td style={styles.td}>
                  <div style={styles.heatmap}>
                    {student.weeklyActivity.map((count, i) => (
                      <div
                        key={i}
                        style={{
                          ...styles.heatCell,
                          background: count === 0 ? '#f1f3f5' : 
                                     count <= 2 ? '#a8dadc' : '#4a90e2'
                        }}
                        title={`${count} sessions`}
                      />
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </Layout>
  )
}

const styles = {
  filters: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '1.5rem'
  },
  filterBtn: {
    padding: '0.5rem 1rem',
    background: 'white',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    fontSize: '0.875rem',
    color: '#495057'
  },
  filterActive: {
    padding: '0.5rem 1rem',
    background: '#4a90e2',
    border: '1px solid #4a90e2',
    borderRadius: '4px',
    fontSize: '0.875rem',
    color: 'white'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse'
  },
  th: {
    textAlign: 'left',
    padding: '0.75rem',
    borderBottom: '2px solid #e1e4e8',
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#495057'
  },
  row: {
    cursor: 'pointer',
    borderBottom: '1px solid #f1f3f5'
  },
  td: {
    padding: '1rem 0.75rem',
    fontSize: '0.875rem'
  },
  badge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '500',
    textTransform: 'capitalize'
  },
  heatmap: {
    display: 'flex',
    gap: '2px'
  },
  heatCell: {
    width: '20px',
    height: '20px',
    borderRadius: '2px'
  }
}
