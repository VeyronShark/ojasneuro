/**
 * AdminDashboard - Comprehensive admin management dashboard
 * Requirements: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3, 8.1, 8.2
 */
import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useNotification } from '../context/NotificationContext'
import Layout from '../components/Layout'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import { useClasses } from '../hooks/useClasses'
import { schoolsAPI, teachersAPI, analyticsAPI, classesAPI } from '../api/config'
import { Plus, Edit2, Trash2, Search, X } from 'lucide-react'
import { buttonStyles, formStyles, tableStyles, badgeStyles } from '../styles/commonStyles'

export default function AdminDashboard() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showSuccess, showError } = useNotification()
  
  // Get school ID from user
  const schoolId = user?.school_id || user?.schoolId
  
  // Active tab state
  const [activeTab, setActiveTab] = useState('overview')
  
  // School metrics state
  const [metrics, setMetrics] = useState(null)
  const [metricsLoading, setMetricsLoading] = useState(true)
  const [metricsError, setMetricsError] = useState(null)
  
  // Teachers state
  const [teachers, setTeachers] = useState([])
  const [teachersLoading, setTeachersLoading] = useState(false)
  const [teachersError, setTeachersError] = useState(null)
  
  // Students state
  const [students, setStudents] = useState([])
  const [studentsLoading, setStudentsLoading] = useState(false)
  const [studentsError, setStudentsError] = useState(null)
  const [studentSearch, setStudentSearch] = useState('')
  
  // Classes from hook
  const { 
    classes, 
    loading: classesLoading, 
    error: classesError, 
    addClass, 
    updateClass, 
    deleteClass, 
    refresh: refreshClasses 
  } = useClasses(schoolId)
  
  // Modal states
  const [showAddClassModal, setShowAddClassModal] = useState(false)
  const [showEditClassModal, setShowEditClassModal] = useState(false)
  const [showDeleteClassDialog, setShowDeleteClassDialog] = useState(false)
  const [selectedClass, setSelectedClass] = useState(null)
  
  // Form states
  const [newClassName, setNewClassName] = useState('')
  const [newGradeLevel, setNewGradeLevel] = useState('')
  const [editClassName, setEditClassName] = useState('')
  const [editGradeLevel, setEditGradeLevel] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Fetch school metrics
  useEffect(() => {
    async function fetchMetrics() {
      if (!schoolId) return
      
      setMetricsLoading(true)
      setMetricsError(null)
      try {
        const data = await analyticsAPI.getSchoolMetrics(schoolId)
        setMetrics(data)
      } catch (err) {
        setMetricsError(err.message || 'Failed to load school metrics')
        // Set default metrics on error
        setMetrics({
          app_install_rate: 0,
          avg_daily_sessions: 0,
          top_skills: [],
          weekly_engagement: [0, 0, 0, 0],
          total_teachers: 0,
          total_classes: 0,
          total_students: 0
        })
      } finally {
        setMetricsLoading(false)
      }
    }
    
    fetchMetrics()
  }, [schoolId])
  
  // Fetch teachers when tab is active
  useEffect(() => {
    async function fetchTeachers() {
      if (!schoolId || activeTab !== 'teachers') return
      
      setTeachersLoading(true)
      setTeachersError(null)
      try {
        const response = await teachersAPI.getAll(schoolId)
        setTeachers(response.teachers || response || [])
      } catch (err) {
        setTeachersError(err.message || 'Failed to load teachers')
      } finally {
        setTeachersLoading(false)
      }
    }
    
    fetchTeachers()
  }, [schoolId, activeTab])
  
  // Fetch all students when tab is active
  useEffect(() => {
    async function fetchStudents() {
      if (!schoolId || activeTab !== 'students') return
      
      setStudentsLoading(true)
      setStudentsError(null)
      try {
        const response = await schoolsAPI.getAllStudents(schoolId)
        setStudents(response.students || response.children || response || [])
      } catch (err) {
        setStudentsError(err.message || 'Failed to load students')
      } finally {
        setStudentsLoading(false)
      }
    }
    
    fetchStudents()
  }, [schoolId, activeTab])
  
  // Filter students by search query
  const filteredStudents = useMemo(() => {
    if (!studentSearch.trim()) return students
    const searchLower = studentSearch.toLowerCase()
    return students.filter(student => {
      const name = student.display_name || student.name || ''
      return name.toLowerCase().includes(searchLower)
    })
  }, [students, studentSearch])
  
  // Handle adding a new class
  const handleAddClass = async (e) => {
    e.preventDefault()
    
    if (!newClassName.trim()) {
      showError('Please enter a class name')
      return
    }
    
    setSubmitting(true)
    try {
      await addClass({
        name: newClassName.trim(),
        grade_level: newGradeLevel.trim() || null
      })
      showSuccess(`Classroom "${newClassName}" created successfully!`)
      setShowAddClassModal(false)
      setNewClassName('')
      setNewGradeLevel('')
    } catch (err) {
      showError(err.message || 'Failed to create classroom')
    } finally {
      setSubmitting(false)
    }
  }
  
  // Handle editing a class
  const handleEditClass = async (e) => {
    e.preventDefault()
    
    if (!editClassName.trim()) {
      showError('Please enter a class name')
      return
    }
    
    setSubmitting(true)
    try {
      await updateClass(selectedClass.id, {
        name: editClassName.trim(),
        grade_level: editGradeLevel.trim() || null
      })
      showSuccess(`Classroom "${editClassName}" updated successfully!`)
      setShowEditClassModal(false)
      setSelectedClass(null)
    } catch (err) {
      showError(err.message || 'Failed to update classroom')
    } finally {
      setSubmitting(false)
    }
  }
  
  // Handle deleting a class
  const handleDeleteClass = async () => {
    setSubmitting(true)
    try {
      await deleteClass(selectedClass.id)
      showSuccess(`Classroom "${selectedClass.name}" deleted successfully!`)
      setShowDeleteClassDialog(false)
      setSelectedClass(null)
    } catch (err) {
      showError(err.message || 'Failed to delete classroom')
    } finally {
      setSubmitting(false)
    }
  }
  
  // Open edit modal with class data
  const openEditClassModal = (cls, e) => {
    e.stopPropagation()
    setSelectedClass(cls)
    setEditClassName(cls.name || '')
    setEditGradeLevel(cls.grade_level || '')
    setShowEditClassModal(true)
  }
  
  // Open delete dialog
  const openDeleteClassDialog = (cls, e) => {
    e.stopPropagation()
    setSelectedClass(cls)
    setShowDeleteClassDialog(true)
  }

  // Render overview tab content
  const renderOverview = () => {
    if (metricsLoading) {
      return <LoadingSpinner message="Loading school metrics..." />
    }
    
    const stats = metrics || {}
    const appInstallRate = stats.app_install_rate || 0
    const avgDailySessions = stats.avg_daily_sessions || 0
    const topSkills = stats.top_skills || []
    const weeklyEngagement = stats.weekly_engagement || [0, 0, 0, 0]
    
    return (
      <>
        <div style={styles.grid}>
          <Card title="App Installation">
            <div style={styles.statValue}>{Math.round(appInstallRate)}%</div>
            <div style={styles.statLabel}>
              Families with app installed
            </div>
          </Card>

          <Card title="Daily Engagement">
            <div style={styles.statValue}>{avgDailySessions.toFixed(1)}</div>
            <div style={styles.statLabel}>Avg. micro-sessions per child (last 7 days)</div>
          </Card>

          <Card title="Top Skills Reinforced">
            <div style={styles.skillList}>
              {topSkills.length > 0 ? topSkills.slice(0, 5).map((skill, i) => (
                <div key={i} style={styles.skillItem}>
                  <span style={styles.skillRank}>{i + 1}</span>
                  <span>{skill}</span>
                </div>
              )) : (
                <div style={styles.emptyText}>No skill data available</div>
              )}
            </div>
          </Card>

          <Card title="Engagement Trend" style={{ gridColumn: 'span 2' }}>
            <div style={styles.chart}>
              {weeklyEngagement.map((value, i) => (
                <div key={i} style={styles.chartBar}>
                  <div style={{ ...styles.bar, height: `${Math.max(value * 50, 5)}px` }}></div>
                  <div style={styles.chartLabel}>Week {i + 1}</div>
                </div>
              ))}
            </div>
            <div style={styles.chartNote}>Last 4 weeks engagement trend</div>
          </Card>
        </div>
        
        {/* Quick Stats Summary */}
        <div style={styles.summaryGrid}>
          <Card>
            <div style={styles.summaryItem}>
              <div style={styles.summaryValue}>{stats.total_teachers || teachers.length || 0}</div>
              <div style={styles.summaryLabel}>Teachers</div>
            </div>
          </Card>
          <Card>
            <div style={styles.summaryItem}>
              <div style={styles.summaryValue}>{stats.total_classes || classes.length || 0}</div>
              <div style={styles.summaryLabel}>Classes</div>
            </div>
          </Card>
          <Card>
            <div style={styles.summaryItem}>
              <div style={styles.summaryValue}>{stats.total_students || 0}</div>
              <div style={styles.summaryLabel}>Students</div>
            </div>
          </Card>
        </div>
      </>
    )
  }
  
  // Render teachers tab content
  const renderTeachers = () => {
    if (teachersLoading) {
      return <LoadingSpinner message="Loading teachers..." />
    }
    
    if (teachersError) {
      return (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{teachersError}</p>
          <button onClick={() => setActiveTab('teachers')} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      )
    }
    
    if (teachers.length === 0) {
      return (
        <Card>
          <EmptyState
            icon="👩‍🏫"
            title="No Teachers Yet"
            message="Your school doesn't have any teachers registered. Teachers can sign up and join your school using the school selection during registration."
          />
        </Card>
      )
    }
    
    return (
      <Card title="All Teachers">
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Name</th>
              <th style={styles.th}>Email</th>
              <th style={styles.th}>Role</th>
              <th style={styles.th}>Assigned Classes</th>
            </tr>
          </thead>
          <tbody>
            {teachers.map(teacher => (
              <tr key={teacher.id} style={styles.row}>
                <td style={styles.td}>{teacher.name}</td>
                <td style={styles.td}>{teacher.email}</td>
                <td style={styles.td}>
                  <span style={styles.roleBadge}>{teacher.role || 'Teacher'}</span>
                </td>
                <td style={styles.td}>
                  {teacher.class_names?.join(', ') || teacher.classes?.map(c => c.name).join(', ') || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    )
  }

  // Render classes tab content
  const renderClasses = () => {
    if (classesLoading && classes.length === 0) {
      return <LoadingSpinner message="Loading classes..." />
    }
    
    if (classesError) {
      return (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{classesError}</p>
          <button onClick={refreshClasses} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      )
    }
    
    return (
      <Card title="All Classrooms">
        <div style={styles.cardHeader}>
          <button onClick={() => setShowAddClassModal(true)} style={buttonStyles.primary}>
            <Plus size={18} />
            <span>Add Classroom</span>
          </button>
        </div>
        
        {classes.length === 0 ? (
          <EmptyState
            icon="📚"
            title="No Classrooms Yet"
            message="Your school doesn't have any classrooms set up. Create your first classroom to start organizing students."
            actionLabel="+ Add Your First Classroom"
            onAction={() => setShowAddClassModal(true)}
          />
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Grade Level</th>
                <th style={styles.th}>Students</th>
                <th style={styles.th}>Teacher</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {classes.map(cls => (
                <tr 
                  key={cls.id} 
                  style={styles.row}
                  onClick={() => navigate(`/class/${cls.id}`)}
                >
                  <td style={styles.td}>{cls.name}</td>
                  <td style={styles.td}>{cls.grade_level || '-'}</td>
                  <td style={styles.td}>{cls.student_count || cls.studentCount || 0}</td>
                  <td style={styles.td}>{cls.teacher_name || cls.primary_teacher?.name || '-'}</td>
                  <td style={styles.td}>
                    <div style={styles.actions}>
                      <button
                        onClick={(e) => openEditClassModal(cls, e)}
                        style={buttonStyles.ghost}
                        title="Edit classroom"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={(e) => openDeleteClassDialog(cls, e)}
                        style={buttonStyles.ghost}
                        title="Delete classroom"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    )
  }
  
  // Render students tab content
  const renderStudents = () => {
    if (studentsLoading) {
      return <LoadingSpinner message="Loading students..." />
    }
    
    if (studentsError) {
      return (
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{studentsError}</p>
          <button onClick={() => setActiveTab('students')} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      )
    }
    
    return (
      <Card title="All Students">
        <div style={styles.cardHeader}>
          <div style={styles.searchContainer}>
            <Search size={18} style={styles.searchIcon} />
            <input
              type="text"
              value={studentSearch}
              onChange={(e) => setStudentSearch(e.target.value)}
              placeholder="Search by name..."
              style={styles.searchInput}
            />
            {studentSearch && (
              <button 
                onClick={() => setStudentSearch('')} 
                style={styles.clearSearchBtn}
                title="Clear search"
              >
                <X size={18} />
              </button>
            )}
          </div>
          <div style={styles.searchInfo}>
            {studentSearch && (
              <span>Showing {filteredStudents.length} of {students.length} students</span>
            )}
          </div>
        </div>
        
        {students.length === 0 ? (
          <EmptyState
            icon="👦"
            title="No Students Yet"
            message="Your school doesn't have any students enrolled. Students can be added to classrooms by teachers or administrators."
            actionLabel="Go to Classes"
            onAction={() => setActiveTab('classes')}
          />
        ) : filteredStudents.length === 0 ? (
          <EmptyState
            icon="🔍"
            title="No Matching Students"
            message={`No students match your search "${studentSearch}". Try a different search term.`}
            actionLabel="Clear Search"
            onAction={() => setStudentSearch('')}
          />
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Age</th>
                <th style={styles.th}>Class</th>
                <th style={styles.th}>Child Code</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map(student => (
                <tr 
                  key={student.id} 
                  style={styles.row}
                  onClick={() => navigate(`/child/${student.id}`)}
                >
                  <td style={styles.td}>{student.display_name || student.name}</td>
                  <td style={styles.td}>{student.age || '-'}</td>
                  <td style={styles.td}>{student.class_name || student.class?.name || '-'}</td>
                  <td style={styles.td}>
                    <code style={styles.code}>{student.child_code || '-'}</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    )
  }

  return (
    <Layout title="School Overview">
      {/* Tab Navigation */}
      <div style={styles.tabs}>
        <button
          onClick={() => setActiveTab('overview')}
          style={activeTab === 'overview' ? styles.tabActive : styles.tab}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('teachers')}
          style={activeTab === 'teachers' ? styles.tabActive : styles.tab}
        >
          Teachers
        </button>
        <button
          onClick={() => setActiveTab('classes')}
          style={activeTab === 'classes' ? styles.tabActive : styles.tab}
        >
          Classes
        </button>
        <button
          onClick={() => setActiveTab('students')}
          style={activeTab === 'students' ? styles.tabActive : styles.tab}
        >
          Students
        </button>
      </div>
      
      {/* Tab Content */}
      <div style={styles.tabContent}>
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'teachers' && renderTeachers()}
        {activeTab === 'classes' && renderClasses()}
        {activeTab === 'students' && renderStudents()}
      </div>
      
      {/* Add Classroom Modal */}
      <Modal
        isOpen={showAddClassModal}
        onClose={() => setShowAddClassModal(false)}
        title="Add New Classroom"
        actions={
          <>
            <button 
              onClick={() => setShowAddClassModal(false)} 
              style={styles.cancelButton}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              onClick={handleAddClass} 
              style={styles.submitButton}
              disabled={submitting || !newClassName.trim()}
            >
              {submitting ? 'Creating...' : 'Create Classroom'}
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
      
      {/* Edit Classroom Modal */}
      <Modal
        isOpen={showEditClassModal}
        onClose={() => setShowEditClassModal(false)}
        title="Edit Classroom"
        actions={
          <>
            <button 
              onClick={() => setShowEditClassModal(false)} 
              style={styles.cancelButton}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              onClick={handleEditClass} 
              style={styles.submitButton}
              disabled={submitting || !editClassName.trim()}
            >
              {submitting ? 'Saving...' : 'Save Changes'}
            </button>
          </>
        }
      >
        <form onSubmit={handleEditClass}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Class Name *</label>
            <input
              type="text"
              value={editClassName}
              onChange={(e) => setEditClassName(e.target.value)}
              placeholder="e.g., Nursery A, KG-B"
              style={styles.input}
              autoFocus
            />
          </div>
          <div style={styles.formGroup}>
            <label style={styles.label}>Grade Level</label>
            <input
              type="text"
              value={editGradeLevel}
              onChange={(e) => setEditGradeLevel(e.target.value)}
              placeholder="e.g., Pre-K, Kindergarten"
              style={styles.input}
            />
          </div>
        </form>
      </Modal>
      
      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteClassDialog}
        onClose={() => setShowDeleteClassDialog(false)}
        onConfirm={handleDeleteClass}
        title="Delete Classroom"
        message={`Are you sure you want to delete "${selectedClass?.name}"? This will also remove all students from this class. This action cannot be undone.`}
        confirmText={submitting ? 'Deleting...' : 'Delete'}
        variant="danger"
      />
    </Layout>
  )
}


const styles = {
  tabs: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '2rem',
    borderBottom: '2px solid var(--border-light)',
    paddingBottom: '0'
  },
  tab: {
    padding: '0.875rem 1.5rem',
    background: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    fontSize: '0.9375rem',
    color: 'var(--text-secondary)',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s ease'
  },
  tabActive: {
    padding: '0.875rem 1.5rem',
    background: 'var(--primary-light)',
    border: 'none',
    borderBottom: '3px solid var(--primary)',
    borderRadius: 'var(--radius-md) var(--radius-md) 0 0',
    fontSize: '0.9375rem',
    color: 'var(--primary-dark)',
    cursor: 'pointer',
    fontWeight: '600'
  },
  tabContent: {
    minHeight: '400px'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1.5rem',
    marginBottom: '1.5rem'
  },
  summaryGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1rem'
  },
  summaryItem: {
    textAlign: 'center',
    padding: '0.5rem'
  },
  summaryValue: {
    fontSize: '2rem',
    fontWeight: '600',
    color: 'var(--primary)'
  },
  summaryLabel: {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)'
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
    background: 'var(--primary)',
    borderRadius: 'var(--radius-sm) var(--radius-sm) 0 0'
  },
  chartLabel: {
    fontSize: '0.75rem',
    color: 'var(--text-muted)'
  },
  chartNote: {
    fontSize: '0.75rem',
    color: 'var(--text-muted)',
    textAlign: 'center',
    marginTop: '1rem'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
    flexWrap: 'wrap',
    gap: '1rem'
  },
  searchContainer: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center'
  },
  searchIcon: {
    position: 'absolute',
    left: '12px',
    color: 'var(--text-muted)',
    pointerEvents: 'none'
  },
  searchInput: {
    padding: '0.625rem 2.5rem 0.625rem 2.75rem',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    fontSize: '0.875rem',
    width: '280px',
    transition: 'all 0.2s ease'
  },
  clearSearchBtn: {
    position: 'absolute',
    right: '8px',
    background: 'transparent',
    border: 'none',
    color: 'var(--text-muted)',
    cursor: 'pointer',
    padding: '0.25rem',
    display: 'flex',
    alignItems: 'center',
    borderRadius: 'var(--radius-sm)',
    transition: 'all 0.2s ease'
  },
  searchInfo: {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)'
  },
  table: tableStyles.table,
  th: tableStyles.th,
  row: tableStyles.row,
  td: tableStyles.td,
  roleBadge: {
    ...badgeStyles.default,
    ...badgeStyles.primary
  },
  code: {
    padding: '0.375rem 0.625rem',
    background: 'var(--bg-tertiary)',
    borderRadius: 'var(--radius-sm)',
    fontSize: '0.8125rem',
    fontFamily: 'monospace',
    color: 'var(--text-primary)'
  },
  actions: {
    display: 'flex',
    gap: '0.5rem'
  },
  emptyState: {
    textAlign: 'center',
    padding: '2rem',
    color: '#6c757d'
  },
  emptyText: {
    color: 'var(--text-muted)',
    fontStyle: 'italic'
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
