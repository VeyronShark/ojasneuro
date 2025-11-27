/**
 * ChildProfile - Student profile page with real API data
 * Requirements: 1.3 - Fetch and display student metrics and skill profile from Backend API
 * Requirements: 4.2, 4.4 - Edit student details
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useNotification } from '../context/NotificationContext'
import Layout from '../components/Layout'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import Modal from '../components/Modal'
import { studentsAPI, classesAPI, insightsAPI, analyticsAPI } from '../api/config'

export default function ChildProfile() {
  const { childId } = useParams()
  const navigate = useNavigate()
  const { showSuccess, showError } = useNotification()
  
  // Student data state
  const [child, setChild] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Class data state
  const [classData, setClassData] = useState(null)
  
  // Metrics state
  const [metrics, setMetrics] = useState(null)
  const [metricsLoading, setMetricsLoading] = useState(false)
  
  // Skill profile state
  const [skillProfile, setSkillProfile] = useState(null)
  const [skillsLoading, setSkillsLoading] = useState(false)
  
  // Insights state
  const [insights, setInsights] = useState([])
  const [insightsLoading, setInsightsLoading] = useState(false)
  
  // Edit modal state
  const [showEditModal, setShowEditModal] = useState(false)
  const [editName, setEditName] = useState('')
  const [editAge, setEditAge] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Fetch student details
  useEffect(() => {
    async function fetchStudentData() {
      setLoading(true)
      setError(null)
      
      try {
        const studentData = await studentsAPI.getById(childId)
        setChild(studentData)
        
        // Fetch class data if student has a class_id
        if (studentData.class_id) {
          try {
            const classInfo = await classesAPI.getById(studentData.class_id)
            setClassData(classInfo)
          } catch (err) {
            console.warn('Failed to fetch class data:', err.message)
          }
        }
      } catch (err) {
        setError(err.message || 'Failed to load student')
      } finally {
        setLoading(false)
      }
    }
    
    if (childId) {
      fetchStudentData()
    }
  }, [childId])
  
  // Fetch metrics
  useEffect(() => {
    async function fetchMetrics() {
      setMetricsLoading(true)
      try {
        const data = await analyticsAPI.getChildMetrics(childId)
        setMetrics(data)
      } catch (err) {
        console.warn('Failed to fetch metrics:', err.message)
      } finally {
        setMetricsLoading(false)
      }
    }
    
    if (childId && !loading) {
      fetchMetrics()
    }
  }, [childId, loading])
  
  // Fetch skill profile
  useEffect(() => {
    async function fetchSkillProfile() {
      setSkillsLoading(true)
      try {
        const data = await studentsAPI.getSkillProfile(childId)
        setSkillProfile(data)
      } catch (err) {
        console.warn('Failed to fetch skill profile:', err.message)
      } finally {
        setSkillsLoading(false)
      }
    }
    
    if (childId && !loading) {
      fetchSkillProfile()
    }
  }, [childId, loading])
  
  // Fetch insights
  useEffect(() => {
    async function fetchInsights() {
      setInsightsLoading(true)
      try {
        const data = await insightsAPI.getByChild(childId)
        setInsights(data.insights || data || [])
      } catch (err) {
        console.warn('Failed to fetch insights:', err.message)
      } finally {
        setInsightsLoading(false)
      }
    }
    
    if (childId && !loading) {
      fetchInsights()
    }
  }, [childId, loading])

  // Handle edit student
  const handleEditStudent = async (e) => {
    e.preventDefault()
    
    if (!editName.trim()) {
      showError('Please enter a student name')
      return
    }
    
    setSubmitting(true)
    try {
      const updatedStudent = await studentsAPI.update(childId, {
        display_name: editName.trim(),
        age: editAge ? parseInt(editAge) : null
      })
      setChild(updatedStudent)
      showSuccess(`Student "${editName}" updated successfully!`)
      setShowEditModal(false)
    } catch (err) {
      showError(err.message || 'Failed to update student')
    } finally {
      setSubmitting(false)
    }
  }
  
  // Open edit modal
  const openEditModal = () => {
    setEditName(child?.display_name || child?.name || '')
    setEditAge(child?.age?.toString() || '')
    setShowEditModal(true)
  }

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
  
  // Convert numeric skill score to level
  const getSkillLevelFromScore = (score) => {
    if (typeof score === 'string') return score
    if (score >= 70) return 'high'
    if (score >= 40) return 'medium'
    return 'low'
  }
  
  // Get skill width percentage
  const getSkillWidth = (level) => {
    if (typeof level === 'number') {
      return `${Math.min(100, Math.max(0, level))}%`
    }
    if (level === 'high') return '100%'
    if (level === 'medium') return '60%'
    return '30%'
  }

  // Generate insight text from insights array or fallback
  const getInsightText = () => {
    if (insights && insights.length > 0) {
      // Return the first insight's text
      const firstInsight = insights[0]
      return firstInsight.text || firstInsight.message || firstInsight.content || JSON.stringify(firstInsight)
    }
    
    // Fallback insight based on skills
    const skills = skillProfile?.skills || skillProfile?.skill_scores || metrics?.skill_scores || {}
    const lowSkills = Object.entries(skills)
      .filter(([_, level]) => {
        if (typeof level === 'number') return level < 40
        return level === 'low'
      })
      .map(([skill]) => skill)

    if (lowSkills.includes('patience')) {
      return "This child tends to complete sensory puzzles but often quits patience tasks early. You might try slow, repetitive classroom activities like pouring grains or using a sand timer."
    }
    
    const engagement = metrics?.engagement || child?.engagement
    if (engagement === 'low') {
      return "This child shows lower engagement with the app. Consider checking in with parents about app usage and exploring what activities might interest the child more."
    }
    
    return "This child shows good engagement across activities. Continue encouraging balanced skill development through varied Montessori exercises."
  }
  
  // Show loading state
  if (loading) {
    return (
      <Layout>
        <LoadingSpinner message="Loading student profile..." />
      </Layout>
    )
  }
  
  // Show error state
  if (error) {
    return (
      <Layout>
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>Failed to load student: {error}</p>
          <button onClick={() => window.location.reload()} style={styles.retryButton}>
            Try Again
          </button>
          <button onClick={() => navigate(-1)} style={styles.backButton}>
            Go Back
          </button>
        </div>
      </Layout>
    )
  }

  if (!child) {
    return (
      <Layout>
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>Student not found</p>
          <button onClick={() => navigate(-1)} style={styles.backButton}>
            Go Back
          </button>
        </div>
      </Layout>
    )
  }
  
  // Get display values from API data
  const displayName = child.display_name || child.name || 'Unknown'
  const displayAge = child.age || '-'
  const className = classData?.name || 'Unknown Class'
  
  // Get metrics values
  const avgSessionsPerDay = metrics?.avg_sessions_per_day || metrics?.sessions_count || child.avgSessionsPerDay || 0
  const trend = metrics?.trend || child.trend || 'stable'
  const weeklyActivity = metrics?.weekly_activity || child.weeklyActivity || [0, 0, 0, 0, 0, 0, 0]
  
  // Get skills from skill profile or metrics
  const skills = skillProfile?.skills || skillProfile?.skill_scores || metrics?.skill_scores || child.skills || {}

  return (
    <Layout>
      <div style={styles.header}>
        <div>
          <h1 style={styles.name}>{displayName}</h1>
          <div style={styles.meta}>
            {className} • Age {displayAge}
          </div>
        </div>
        <button onClick={openEditModal} style={styles.editButton}>
          ✏️ Edit Student
        </button>
      </div>

      <div style={styles.grid}>
        <Card title="App Engagement">
          {metricsLoading ? (
            <LoadingSpinner size="small" message="" />
          ) : (
            <>
              <div style={styles.statValue}>
                {typeof avgSessionsPerDay === 'number' ? avgSessionsPerDay.toFixed(1) : avgSessionsPerDay}
              </div>
              <div style={styles.statLabel}>Avg. sessions per day</div>
              <div style={styles.trend}>
                Trend: {getTrendIcon(trend)} {trend}
              </div>
            </>
          )}
        </Card>

        <Card title="Skill Profile" style={{ gridColumn: 'span 2' }}>
          {skillsLoading ? (
            <LoadingSpinner size="small" message="Loading skills..." />
          ) : Object.keys(skills).length > 0 ? (
            <div style={styles.skillGrid}>
              {Object.entries(skills).map(([skill, level]) => {
                const skillLevel = getSkillLevelFromScore(level)
                return (
                  <div key={skill} style={styles.skillRow}>
                    <div style={styles.skillName}>
                      {skill.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').trim()}
                    </div>
                    <div style={styles.skillBar}>
                      <div
                        style={{
                          ...styles.skillFill,
                          width: getSkillWidth(level),
                          background: getSkillLevel(skillLevel)
                        }}
                      />
                    </div>
                    <div style={styles.skillLevel}>
                      {typeof level === 'number' ? `${level}%` : level}
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p style={styles.emptyText}>No skill data available yet</p>
          )}
        </Card>

        <Card title="Classroom Insight" style={{ gridColumn: 'span 3' }}>
          {insightsLoading ? (
            <LoadingSpinner size="small" message="Loading insights..." />
          ) : (
            <p style={styles.insight}>{getInsightText()}</p>
          )}
        </Card>

        <Card title="Weekly Activity" style={{ gridColumn: 'span 3' }}>
          {metricsLoading ? (
            <LoadingSpinner size="small" message="Loading activity..." />
          ) : (
            <div style={styles.weeklyChart}>
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
                <div key={i} style={styles.dayColumn}>
                  <div style={styles.barContainer}>
                    <div
                      style={{
                        ...styles.bar,
                        height: `${(weeklyActivity[i] || 0) * 30}px`,
                        background: (weeklyActivity[i] || 0) === 0 ? '#e9ecef' : '#4a90e2'
                      }}
                    />
                  </div>
                  <div style={styles.dayLabel}>{day}</div>
                  <div style={styles.sessionCount}>{weeklyActivity[i] || 0}</div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <button style={styles.downloadBtn}>
        📄 Download Summary for PTM (PDF)
      </button>
      
      {/* Edit Student Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Edit Student"
        actions={
          <>
            <button 
              onClick={() => setShowEditModal(false)} 
              style={styles.cancelButton}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              onClick={handleEditStudent} 
              style={styles.submitButton}
              disabled={submitting || !editName.trim()}
            >
              {submitting ? 'Saving...' : 'Save Changes'}
            </button>
          </>
        }
      >
        <form onSubmit={handleEditStudent}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Student Name *</label>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="e.g., Emma Wilson"
              style={styles.input}
              autoFocus
            />
          </div>
          <div style={styles.formGroup}>
            <label style={styles.label}>Age</label>
            <input
              type="number"
              value={editAge}
              onChange={(e) => setEditAge(e.target.value)}
              placeholder="e.g., 4"
              style={styles.input}
              min="1"
              max="18"
            />
          </div>
        </form>
      </Modal>
    </Layout>
  )
}

const styles = {
  header: {
    marginBottom: '2rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start'
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
  editButton: {
    padding: '0.5rem 1rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500'
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
  emptyText: {
    color: '#6c757d',
    fontStyle: 'italic'
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
    fontWeight: '500',
    border: 'none',
    cursor: 'pointer'
  },
  errorContainer: {
    textAlign: 'center',
    padding: '2rem'
  },
  errorText: {
    color: '#dc3545',
    marginBottom: '1rem'
  },
  retryButton: {
    padding: '0.5rem 1rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginRight: '0.5rem'
  },
  backButton: {
    padding: '0.5rem 1rem',
    background: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  formGroup: {
    marginBottom: '1rem'
  },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: '500',
    color: '#2c3e50'
  },
  input: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    fontSize: '1rem',
    boxSizing: 'border-box'
  },
  cancelButton: {
    padding: '0.5rem 1rem',
    background: '#f8f9fa',
    color: '#6c757d',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  submitButton: {
    padding: '0.5rem 1rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  }
}
