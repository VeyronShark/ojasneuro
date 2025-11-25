import Layout from '../components/Layout'
import Card from '../components/Card'
import { DUMMY_DATA } from '../data/dummyData'

export default function AdminDashboard({ user }) {
  const stats = DUMMY_DATA.adminStats
  const school = DUMMY_DATA.school

  return (
    <Layout user={user} title="School Overview">
      <div style={styles.grid}>
        <Card title="App Installation">
          <div style={styles.statValue}>{stats.appInstallRate}%</div>
          <div style={styles.statLabel}>
            {school.appInstalls} of {school.enrolledFamilies} families installed the app
          </div>
        </Card>

        <Card title="Daily Engagement">
          <div style={styles.statValue}>{stats.avgDailySessionsPerChild}</div>
          <div style={styles.statLabel}>Avg. micro-sessions per child (last 7 days)</div>
        </Card>

        <Card title="Top Skills Reinforced">
          <div style={styles.skillList}>
            {stats.topSkills.map((skill, i) => (
              <div key={i} style={styles.skillItem}>
                <span style={styles.skillRank}>{i + 1}</span>
                <span>{skill}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Engagement Trend" style={{ gridColumn: 'span 2' }}>
          <div style={styles.chart}>
            {stats.weeklyEngagement.map((value, i) => (
              <div key={i} style={styles.chartBar}>
                <div style={{ ...styles.bar, height: `${value * 50}px` }}></div>
                <div style={styles.chartLabel}>Week {i + 1}</div>
              </div>
            ))}
          </div>
          <div style={styles.chartNote}>Last 4 weeks engagement trend</div>
        </Card>
      </div>
    </Layout>
  )
}

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
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
  skillList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  },
  skillItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    fontSize: '0.9375rem'
  },
  skillRank: {
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    background: '#e9ecef',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.75rem',
    fontWeight: '600',
    color: '#495057'
  },
  chart: {
    display: 'flex',
    gap: '2rem',
    alignItems: 'flex-end',
    padding: '1rem 0',
    justifyContent: 'center'
  },
  chartBar: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '0.5rem'
  },
  bar: {
    width: '60px',
    background: '#4a90e2',
    borderRadius: '4px 4px 0 0'
  },
  chartLabel: {
    fontSize: '0.75rem',
    color: '#6c757d'
  },
  chartNote: {
    fontSize: '0.75rem',
    color: '#6c757d',
    textAlign: 'center',
    marginTop: '1rem'
  }
}
