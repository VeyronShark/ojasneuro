import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useNotification } from '../context/NotificationContext'
import Layout from '../components/Layout'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import { useStudents } from '../hooks/useStudents'
import { classesAPI, analyticsAPI } from '../api/config'
import { Plus, Edit2, Trash2, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { buttonStyles, formStyles, tableStyles } from '../styles/commonStyles'

export default function ClassView() {
  const { classId } = useParams()
  const navigate = useNavigate()
  const { showSuccess, showError } = useNotification()
  const [filter, setFilter] = useState('all')
  
  // Fetch class data
  const [classData, setClassData] = useState(null)
  const [classLoading, setClassLoading] = useState(true)
  const [classError, setClassError] = useState(null)
  
  // Fetch class metrics
  const [metrics, setMetrics] = useState(null)
  const [metricsLoading, setMetricsLoading] = useState(false)
  
  // Use the useStudents hook for student management
  const { 
    students, 
    loading: studentsLoading, 
    error: studentsError, 
    addStudent, 
    updateStudent, 
    deleteStudent, 
    refresh: refreshStudents 
  } = useStudents(classId)
  
  // Modal states
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState(null)
  
  // Form states
  const [newStudentName, setNewStudentName] = useState('')
  const [newStudentAge, setNewStudentAge] = useState('')
  const [editStudentName, setEditStudentName] = useState('')
  const [editStudentAge, setEditStudentAge] = useState('')
  const [submitting, setSubmitting] = useState(false)
  
  // Fetch class data on mount
  useEffect(() => {
    async function fetchClassData() {
      setClassLoading(true)
      setClassError(null)
      try {
        const data = await classesAPI.getById(classId)
        setClassData(data)
      } catch (err) {
        setClassError(err.message || 'Failed to load class')
      } finally {
        setClassLoading(false)
      }
    }
    
    if (classId) {
      fetchClassData()
    }
  }, [classId])
  
  // Fetch class metrics
  useEffect(() => {
    async function fetchMetrics() {
      setMetricsLoading(true)
      try {
        const data = await analyticsAPI.getClassMetrics(classId)
        setMetrics(data)
      } catch (err) {
        // Metrics are optional, don't show error
        console.warn('Failed to fetch class metrics:', err.message)
      } finally {
        setMetricsLoading(false)
      }
    }
    
    if (classId && !classLoading) {
      fetchMetrics()
    }
  }, [classId, classLoading])

  // Filter students based on engagement/skills
  let filteredStudents = [...students]
  if (filter === 'low') {
    filteredStudents = filteredStudents.filter(s => 
      s.engagement === 'low' || s.metrics?.engagement === 'low'
    )
  } else if (filter === 'struggling') {
    filteredStudents = filteredStudents.filter(s => {
      const skills = s.skills || s.skill_scores || s.metrics?.skill_scores || {}
      return Object.values(skills).some(level => 
        level === 'low' || (typeof level === 'number' && level < 30)
      )
    })
  }

  const getEngagementColor = (level) => {
    if (level === 'high') return '#28a745'
    if (level === 'medium') return '#ffc107'
    return '#dc3545'
  }

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <TrendingUp size={18} color="var(--success)" />
    if (trend === 'down') return <TrendingDown size={18} color="var(--error)" />
    return <Minus size={18} color="var(--text-muted)" />
  }
  
  // Handle adding a new student
  const handleAddStudent = async (e) => {
    e.preventDefault()
    
    if (!newStudentName.trim()) {
      showError('Please enter a student name')
      return
    }
    
    setSubmitting(true)
    try {
      await addStudent({
        display_name: newStudentName.trim(),
        age: newStudentAge ? parseInt(newStudentAge) : null
      })
      showSuccess(`Student "${newStudentName}" added successfully!`)
      setShowAddModal(false)
      setNewStudentName('')
      setNewStudentAge('')
    } catch (err) {
      showError(err.message || 'Failed to add student')
    } finally {
      setSubmitting(false)
    }
  }
  
  // Handle editing a student
  const handleEditStudent = async (e) => {
    e.preventDefault()
    
    if (!editStudentName.trim()) {
      showError('Please enter a student name')
      return
    }
    
    setSubmitting(true)
    try {
      await updateStudent(selectedStudent.id, {
        display_name: editStudentName.trim(),
        age: editStudentAge ? parseInt(editStudentAge) : null
      })
      showSuccess(`Student "${editStudentName}" updated successfully!`)
      setShowEditModal(false)
      setSelectedStudent(null)
    } catch (err) {
      showError(err.message || 'Failed to update student')
    } finally {
      setSubmitting(false)
    }
  }
  
  // Handle deleting a student
  const handleDeleteStudent = async () => {
    setSubmitting(true)
    try {
      await deleteStudent(selectedStudent.id)
      showSuccess(`Student "${selectedStudent.display_name || selectedStudent.name}" deleted successfully!`)
      setShowDeleteDialog(false)
      setSelectedStudent(null)
    } catch (err) {
      showError(err.message || 'Failed to delete student')
    } finally {
      setSubmitting(false)
    }
  }
  
  // Open edit modal with student data
  const openEditModal = (student, e) => {
    e.stopPropagation()
    setSelectedStudent(student)
    setEditStudentName(student.display_name || student.name || '')
    setEditStudentAge(student.age?.toString() || '')
    setShowEditModal(true)
  }
  
  // Open delete dialog
  const openDeleteDialog = (student, e) => {
    e.stopPropagation()
    setSelectedStudent(student)
    setShowDeleteDialog(true)
  }
  
  // Show loading state
  if (classLoading) {
    return (
      <Layout title="Loading...">
        <LoadingSpinner message="Loading class data..." />
      </Layout>
    )
  }
  
  // Show error state
  if (classError) {
    return (
      <Layout title="Error">
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>Failed to load class: {classError}</p>
          <button onClick={() => window.location.reload()} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title={classData?.name || 'Class View'}>
      {/* Class Metrics Header */}
      {metricsLoading ? (
        <div style={styles.metricsGrid}>
          <Card><LoadingSpinner size="small" message="" /></Card>
          <Card><LoadingSpinner size="small" message="" /></Card>
          <Card><LoadingSpinner size="small" message="" /></Card>
        </div>
      ) : metrics && (
        <div style={styles.metricsGrid}>
          <Card title="Total Students">
            <div style={styles.metricValue}>{metrics.total_students || students.length}</div>
          </Card>
          <Card title="Active This Week">
            <div style={styles.metricValue}>{metrics.active_this_week || 0}</div>
          </Card>
          <Card title="Avg Sessions/Day">
            <div style={styles.metricValue}>{metrics.avg_sessions_per_day?.toFixed(1) || '0'}</div>
          </Card>
        </div>
      )}
      
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
        
        <button
          onClick={() => setShowAddModal(true)}
          style={buttonStyles.success}
        >
          <Plus size={18} />
          <span>Add Student</span>
        </button>
      </div>

      <Card>
        {studentsLoading && students.length === 0 ? (
          <LoadingSpinner message="Loading students..." />
        ) : studentsError ? (
          <div style={styles.errorContainer}>
            <p style={styles.errorText}>{studentsError}</p>
            <button onClick={refreshStudents} style={styles.retryButton}>
              Try Again
            </button>
          </div>
        ) : filteredStudents.length === 0 && students.length === 0 ? (
          <EmptyState
            icon="👦"
            title="No Students Yet"
            message="This class doesn't have any students enrolled. Add your first student to start tracking their progress and engagement."
            actionLabel="+ Add Your First Student"
            onAction={() => setShowAddModal(true)}
          />
        ) : filteredStudents.length === 0 ? (
          <EmptyState
            icon="🔍"
            title="No Matching Students"
            message={`No students match the current filter. Try a different filter or view all students.`}
            actionLabel="View All Students"
            onAction={() => setFilter('all')}
          />
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Child Name</th>
                <th style={styles.th}>Age</th>
                <th style={styles.th}>Engagement</th>
                <th style={styles.th}>Avg. Sessions/Day</th>
                <th style={styles.th}>Trend</th>
                <th style={styles.th}>Weekly Activity</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map(student => {
                const studentMetrics = student.metrics || {}
                const engagement = student.engagement || studentMetrics.engagement || 'medium'
                const avgSessions = student.avgSessionsPerDay || studentMetrics.avg_sessions_per_day || studentMetrics.avg_duration || 0
                const trend = student.trend || studentMetrics.trend || 'stable'
                const weeklyActivity = student.weeklyActivity || studentMetrics.weekly_activity || [0, 0, 0, 0, 0, 0, 0]
                
                return (
                  <tr
                    key={student.id}
                    onClick={() => navigate(`/child/${student.id}`)}
                    style={styles.row}
                  >
                    <td style={styles.td}>{student.display_name || student.name}</td>
                    <td style={styles.td}>{student.age || '-'}</td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.badge,
                        background: getEngagementColor(engagement) + '20',
                        color: getEngagementColor(engagement)
                      }}>
                        {engagement}
                      </span>
                    </td>
                    <td style={styles.td}>{typeof avgSessions === 'number' ? avgSessions.toFixed(1) : avgSessions}</td>
                    <td style={styles.td}>{getTrendIcon(trend)}</td>
                    <td style={styles.td}>
                      <div style={styles.heatmap}>
                        {weeklyActivity.map((count, i) => (
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
                    <td style={styles.td}>
                      <div style={styles.actions}>
                        <button
                          onClick={(e) => openEditModal(student, e)}
                          style={buttonStyles.ghost}
                          title="Edit student"
                        >
                          <Edit2 size={16} />
                        </button>
                        <button
                          onClick={(e) => openDeleteDialog(student, e)}
                          style={buttonStyles.ghost}
                          title="Delete student"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </Card>
      
      {/* Add Student Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add New Student"
        actions={
          <>
            <button 
              onClick={() => setShowAddModal(false)} 
              style={styles.cancelButton}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              onClick={handleAddStudent} 
              style={styles.submitButton}
              disabled={submitting || !newStudentName.trim()}
            >
              {submitting ? 'Adding...' : 'Add Student'}
            </button>
          </>
        }
      >
        <form onSubmit={handleAddStudent}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Student Name *</label>
            <input
              type="text"
              value={newStudentName}
              onChange={(e) => setNewStudentName(e.target.value)}
              placeholder="e.g., Emma Wilson"
              style={styles.input}
              autoFocus
            />
          </div>
          <div style={styles.formGroup}>
            <label style={styles.label}>Age</label>
            <input
              type="number"
              value={newStudentAge}
              onChange={(e) => setNewStudentAge(e.target.value)}
              placeholder="e.g., 4"
              style={styles.input}
              min="1"
              max="18"
            />
          </div>
        </form>
      </Modal>
      
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
              disabled={submitting || !editStudentName.trim()}
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
              value={editStudentName}
              onChange={(e) => setEditStudentName(e.target.value)}
              placeholder="e.g., Emma Wilson"
              style={styles.input}
              autoFocus
            />
          </div>
          <div style={styles.formGroup}>
            <label style={styles.label}>Age</label>
            <input
              type="number"
              value={editStudentAge}
              onChange={(e) => setEditStudentAge(e.target.value)}
              placeholder="e.g., 4"
              style={styles.input}
              min="1"
              max="18"
            />
          </div>
        </form>
      </Modal>
      
      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={handleDeleteStudent}
        title="Delete Student"
        message={`Are you sure you want to delete "${selectedStudent?.display_name || selectedStudent?.name}"? This action cannot be undone.`}
        confirmText={submitting ? 'Deleting...' : 'Delete'}
        variant="danger"
      />
    </Layout>
  )
}

const styles = {
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1.25rem',
    marginBottom: '2rem'
  },
  metricValue: {
    fontSize: '2rem',
    fontWeight: '600',
    color: 'var(--primary)'
  },
  filters: {
    display: 'flex',
    gap: '0.75rem',
    marginBottom: '1.5rem',
    flexWrap: 'wrap',
    alignItems: 'center'
  },
  filterBtn: {
    padding: '0.625rem 1.25rem',
    background: 'var(--bg-secondary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    fontSize: '0.875rem',
    color: 'var(--text-secondary)',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s ease'
  },
  filterActive: {
    padding: '0.625rem 1.25rem',
    background: 'var(--primary)',
    border: '1px solid var(--primary)',
    borderRadius: 'var(--radius-md)',
    fontSize: '0.875rem',
    color: 'white',
    cursor: 'pointer',
    fontWeight: '500',
    boxShadow: 'var(--shadow-sm)'
  },
  table: tableStyles.table,
  th: tableStyles.th,
  row: tableStyles.row,
  td: tableStyles.td,
  badge: {
    padding: '0.375rem 0.875rem',
    borderRadius: 'var(--radius-lg)',
    fontSize: '0.75rem',
    fontWeight: '500',
    textTransform: 'capitalize'
  },
  heatmap: {
    display: 'flex',
    gap: '3px'
  },
  heatCell: {
    width: '22px',
    height: '22px',
    borderRadius: 'var(--radius-sm)'
  },
  actions: {
    display: 'flex',
    gap: '0.5rem'
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
  retryButton: buttonStyles.primary,
  formGroup: formStyles.formGroup,
  label: formStyles.label,
  input: formStyles.input,
  cancelButton: buttonStyles.secondary,
  submitButton: buttonStyles.primary
}
