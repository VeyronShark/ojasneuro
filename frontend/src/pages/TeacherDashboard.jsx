import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useNotification } from '../context/NotificationContext'
import Layout from '../components/Layout'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import Modal from '../components/Modal'
import EmptyState from '../components/EmptyState'
import { useClasses } from '../hooks/useClasses'
import { analyticsAPI } from '../api/config'
import { Plus } from 'lucide-react'
import { buttonStyles, formStyles } from '../styles/commonStyles'

export default function TeacherDashboard() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showSuccess, showError } = useNotification()
  
  // Get school ID from user
  const schoolId = user?.school_id || user?.schoolId
  
  // Fetch classes from API using the useClasses hook
  const { classes, loading: classesLoading, error: classesError, addClass, refresh } = useClasses(schoolId)
  
  // State for class metrics
  const [metrics, setMetrics] = useState(null)
  const [metricsLoading, setMetricsLoading] = useState(false)
  
  // State for Add Classroom modal
  const [showAddModal, setShowAddModal] = useState(false)
  const [newClassName, setNewClassName] = useState('')
  const [newGradeLevel, setNewGradeLevel] = useState('')
  const [addingClass, setAddingClass] = useState(false)
  
  // Filter classes by user's assigned class IDs if available
  const userClassIds = user?.classIds || user?.class_ids || []
  const filteredClasses = userClassIds.length > 0 
    ? classes.filter(c => userClassIds.includes(c.id))
    : classes // Show all classes if no classIds (new user or admin)
  
  // Fetch metrics for all classes and aggregate
  useEffect(() => {
    async function fetchMetrics() {
      if (filteredClasses.length === 0) return
      
      setMetricsLoading(true)
      try {
        // Fetch metrics for all classes
        const metricsPromises = filteredClasses.map(cls => 
          analyticsAPI.getClassMetrics(cls.id).catch(err => {
            console.warn(`Failed to fetch metrics for class ${cls.id}:`, err.message)
            return null
          })
        )
        
        const allMetrics = await Promise.all(metricsPromises)
        const validMetrics = allMetrics.filter(m => m !== null)
        
        // Aggregate metrics across all classes
        if (validMetrics.length > 0) {
          const aggregated = {
            total_children: validMetrics.reduce((sum, m) => sum + (m.total_children || 0), 0),
            active_children: validMetrics.reduce((sum, m) => sum + (m.active_children || 0), 0),
            total_sessions: validMetrics.reduce((sum, m) => sum + (m.total_sessions || 0), 0),
            avg_skill_scores: {}
          }
          
          // Calculate average skill scores across all classes
          const skillTotals = {}
          const skillCounts = {}
          validMetrics.forEach(m => {
            if (m.avg_skill_scores) {
              Object.entries(m.avg_skill_scores).forEach(([skill, score]) => {
                if (score !== null && score !== undefined) {
                  skillTotals[skill] = (skillTotals[skill] || 0) + score
                  skillCounts[skill] = (skillCounts[skill] || 0) + 1
                }
              })
            }
          })
          
          Object.keys(skillTotals).forEach(skill => {
            aggregated.avg_skill_scores[skill] = skillTotals[skill] / skillCounts[skill]
          })
          
          setMetrics(aggregated)
        }
      } catch (err) {
        console.warn('Failed to fetch class metrics:', err.message)
      } finally {
        setMetricsLoading(false)
      }
    }
    
    if (!classesLoading && filteredClasses.length > 0) {
      fetchMetrics()
    }
  }, [filteredClasses, classesLoading])
  
  // Calculate statistics from aggregated metrics
  const totalStudents = filteredClasses.reduce((sum, c) => sum + (c.student_count || c.studentCount || 0), 0)
  const activeThisWeek = metrics?.active_children || 0
  const usagePercent = totalStudents > 0 ? Math.round((activeThisWeek / totalStudents) * 100) : 0
  
  // Calculate avg sessions per day from total sessions and date range (default 7 days)
  const avgSessionsPerDay = metrics?.total_sessions ? (metrics.total_sessions / 7).toFixed(1) : '0'
  
  // Get top skill from avg_skill_scores
  const skillScores = metrics?.avg_skill_scores || {}
  const topSkillEntry = Object.entries(skillScores).sort((a, b) => b[1] - a[1])[0]
  const topSkill = topSkillEntry?.[0] || 'sensory'
  
  // Handle adding a new classroom
  const handleAddClass = async (e) => {
    e.preventDefault()
    
    if (!newClassName.trim()) {
      showError('Please enter a class name')
      return
    }
    
    setAddingClass(true)
    try {
      await addClass({
        name: newClassName.trim(),
        grade_level: newGradeLevel.trim() || null,
        primary_teacher_id: user?.id
      })
      showSuccess(`Classroom "${newClassName}" created successfully!`)
      setShowAddModal(false)
      setNewClassName('')
      setNewGradeLevel('')
    } catch (err) {
      showError(err.message || 'Failed to create classroom')
    } finally {
      setAddingClass(false)
    }
  }
  
  // Show loading state
  if (classesLoading && classes.length === 0) {
    return (
      <Layout title="Teacher Overview">
        <LoadingSpinner message="Loading your classes..." />
      </Layout>
    )
  }
  
  // Show error state
  if (classesError) {
    return (
      <Layout title="Teacher Overview">
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>Failed to load classes: {classesError}</p>
          <button onClick={refresh} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Teacher Overview">
      <div style={styles.grid}>
        <Card title="Class Usage This Week">
          {metricsLoading ? (
            <LoadingSpinner size="small" message="" />
          ) : (
            <>
              <div style={styles.statValue}>{usagePercent}%</div>
              <div style={styles.statLabel}>
                {activeThisWeek} of {totalStudents} children used the app
              </div>
            </>
          )}
        </Card>

        <Card title="Avg. Sessions Per Day">
          {metricsLoading ? (
            <LoadingSpinner size="small" message="" />
          ) : (
            <>
              <div style={styles.statValue}>{avgSessionsPerDay}</div>
              <div style={styles.statLabel}>Across your classes</div>
            </>
          )}
        </Card>

        <Card title="Dominant Skill Theme">
          {metricsLoading ? (
            <LoadingSpinner size="small" message="" />
          ) : (
            <>
              <div style={styles.skillBadge}>
                {topSkill
                  .replace(/([A-Z])/g, ' $1')
                  .replace(/_/g, ' ')
                  .trim()
                  .toLowerCase()
                  .replace(/^\w/, c => c.toUpperCase())}
              </div>
              <div style={styles.statLabel}>Highest average skill score</div>
            </>
          )}
        </Card>
      </div>

      <Card title="Your Classes" style={{ marginTop: '1.5rem' }}>
        <div style={styles.classHeader}>
          <button 
            onClick={() => setShowAddModal(true)} 
            style={buttonStyles.primary}
          >
            <Plus size={18} />
            <span>Add Classroom</span>
          </button>
        </div>
        
        {filteredClasses.length === 0 ? (
          <EmptyState
            icon="📚"
            title="No Classes Yet"
            message="Get started by creating your first classroom. You can add students and track their progress once you have a class set up."
            actionLabel="+ Add Your First Classroom"
            onAction={() => setShowAddModal(true)}
          />
        ) : (
          <div style={styles.classList}>
            {filteredClasses.map(cls => (
              <button
                key={cls.id}
                onClick={() => navigate(`/class/${cls.id}`)}
                style={styles.classCard}
              >
                <div style={styles.className}>{cls.name}</div>
                <div style={styles.classInfo}>
                  {cls.student_count || cls.studentCount || 0} students
                  {cls.grade_level && ` • ${cls.grade_level}`}
                </div>
              </button>
            ))}
          </div>
        )}
      </Card>
      
      {/* Add Classroom Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add New Classroom"
        actions={
          <>
            <button 
              onClick={() => setShowAddModal(false)} 
              style={styles.cancelButton}
              disabled={addingClass}
            >
              Cancel
            </button>
            <button 
              onClick={handleAddClass} 
              style={styles.submitButton}
              disabled={addingClass || !newClassName.trim()}
            >
              {addingClass ? 'Creating...' : 'Create Classroom'}
            </button>
          </>
        }
      >
        <form onSubmit={handleAddClass}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Class Name *</label>
            <input
              type="text"
              value={newClassName}
              onChange={(e) => setNewClassName(e.target.value)}
              placeholder="e.g., Nursery A, KG-B"
              style={styles.input}
              autoFocus
            />
          </div>
          <div style={styles.formGroup}>
            <label style={styles.label}>Grade Level</label>
            <input
              type="text"
              value={newGradeLevel}
              onChange={(e) => setNewGradeLevel(e.target.value)}
              placeholder="e.g., Pre-K, Kindergarten"
              style={styles.input}
            />
          </div>
        </form>
      </Modal>
    </Layout>
  )
}

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1.5rem'
  },
  statValue: {
    fontSize: '2.5rem',
    fontWeight: '600',
    color: 'var(--primary)',
    marginBottom: '0.5rem'
  },
  statLabel: {
    fontSize: '0.875rem',
    color: 'var(--text-muted)',
    lineHeight: 1.5
  },
  skillBadge: {
    display: 'inline-block',
    padding: '0.625rem 1.25rem',
    background: 'var(--primary-light)',
    color: 'var(--primary-dark)',
    borderRadius: 'var(--radius-xl)',
    fontSize: '1rem',
    fontWeight: '500',
    textTransform: 'capitalize',
    marginBottom: '0.5rem'
  },
  classHeader: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '1.5rem'
  },
  classList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
    gap: '1.25rem'
  },
  classCard: {
    padding: '1.5rem',
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border-light)',
    borderRadius: 'var(--radius-lg)',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: 'var(--shadow-sm)'
  },
  className: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: 'var(--text-primary)',
    marginBottom: '0.5rem',
    letterSpacing: '-0.01em'
  },
  classInfo: {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)'
  },
  errorContainer: {
    textAlign: 'center',
    padding: '3rem 2rem'
  },
  errorText: {
    color: 'var(--error)',
    marginBottom: '1rem',
    fontSize: '1rem'
  },
  retryButton: {
    ...buttonStyles.primary
  },
  formGroup: formStyles.formGroup,
  label: formStyles.label,
  input: formStyles.input,
  cancelButton: buttonStyles.secondary,
  submitButton: buttonStyles.primary
}
