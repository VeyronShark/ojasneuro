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
  
  // Fetch metrics for the first class (or aggregate)
  useEffect(() => {
    async function fetchMetrics() {
      if (filteredClasses.length === 0) return
      
      setMetricsLoading(true)
      try {
        // Fetch metrics for the first class as a sample
        const classMetrics = await analyticsAPI.getClassMetrics(filteredClasses[0].id)
        setMetrics(classMetrics)
      } catch (err) {
        // Metrics are optional, don't show error for this
        console.warn('Failed to fetch class metrics:', err.message)
      } finally {
        setMetricsLoading(false)
      }
    }
    
    if (!classesLoading && filteredClasses.length > 0) {
      fetchMetrics()
    }
  }, [filteredClasses, classesLoading])
  
  // Calculate statistics from metrics or use defaults
  const totalStudents = filteredClasses.reduce((sum, c) => sum + (c.student_count || c.studentCount || 0), 0)
  const activeThisWeek = metrics?.active_this_week || 0
  const usagePercent = totalStudents > 0 ? Math.round((activeThisWeek / totalStudents) * 100) : 0
  const avgPuzzles = metrics?.avg_sessions_per_day?.toFixed(1) || '0'
  
  // Get top skill from metrics
  const skillDistribution = metrics?.skill_distribution || {}
  const topSkillEntry = Object.entries(skillDistribution).sort((a, b) => b[1] - a[1])[0]
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

        <Card title="Avg. Puzzles Per Day">
          {metricsLoading ? (
            <LoadingSpinner size="small" message="" />
          ) : (
            <>
              <div style={styles.statValue}>{avgPuzzles}</div>
              <div style={styles.statLabel}>Across your classes</div>
            </>
          )}
        </Card>

        <Card title="Dominant Skill Theme">
          {metricsLoading ? (
            <LoadingSpinner size="small" message="" />
          ) : (
            <>
              <div style={styles.skillBadge}>{topSkill.replace(/([A-Z])/g, ' $1').trim()}</div>
              <div style={styles.statLabel}>Most reinforced in puzzles</div>
            </>
          )}
        </Card>
      </div>

      <Card title="Your Classes" style={{ marginTop: '1.5rem' }}>
        <div style={styles.classHeader}>
          <button 
            onClick={() => setShowAddModal(true)} 
            style={styles.addButton}
          >
            + Add Classroom
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
  classHeader: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '1rem'
  },
  addButton: {
    padding: '0.5rem 1rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500'
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
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'border-color 0.2s'
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
  },
  emptyState: {
    textAlign: 'center',
    padding: '2rem',
    color: '#6c757d'
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
