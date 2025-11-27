/**
 * ManageClasses - Admin page for viewing and managing all classes
 * Requirements: 6.1, 6.2, 6.3, 6.4 - View all classes, CRUD operations
 */
import { useState } from 'react'
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

export default function ManageClasses() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showSuccess, showError } = useNotification()
  
  // Get school ID from user
  const schoolId = user?.school_id || user?.schoolId
  
  // Classes from hook
  const { 
    classes, 
    loading, 
    error, 
    addClass, 
    updateClass, 
    deleteClass, 
    refresh 
  } = useClasses(schoolId)
  
  // Modal states
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [selectedClass, setSelectedClass] = useState(null)
  
  // Form states
  const [className, setClassName] = useState('')
  const [gradeLevel, setGradeLevel] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Handle adding a new class
  const handleAddClass = async (e) => {
    e.preventDefault()
    
    if (!className.trim()) {
      showError('Please enter a class name')
      return
    }
    
    setSubmitting(true)
    try {
      await addClass({
        name: className.trim(),
        grade_level: gradeLevel.trim() || null
      })
      showSuccess(`Classroom "${className}" created successfully!`)
      setShowAddModal(false)
      resetForm()
    } catch (err) {
      showError(err.message || 'Failed to create classroom')
    } finally {
      setSubmitting(false)
    }
  }


  // Handle editing a class
  const handleEditClass = async (e) => {
    e.preventDefault()
    
    if (!className.trim()) {
      showError('Please enter a class name')
      return
    }
    
    setSubmitting(true)
    try {
      await updateClass(selectedClass.id, {
        name: className.trim(),
        grade_level: gradeLevel.trim() || null
      })
      showSuccess(`Classroom "${className}" updated successfully!`)
      setShowEditModal(false)
      setSelectedClass(null)
      resetForm()
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
      setShowDeleteDialog(false)
      setSelectedClass(null)
    } catch (err) {
      showError(err.message || 'Failed to delete classroom')
    } finally {
      setSubmitting(false)
    }
  }

  // Reset form fields
  const resetForm = () => {
    setClassName('')
    setGradeLevel('')
  }

  // Open edit modal with class data
  const openEditModal = (cls, e) => {
    e.stopPropagation()
    setSelectedClass(cls)
    setClassName(cls.name || '')
    setGradeLevel(cls.grade_level || '')
    setShowEditModal(true)
  }

  // Open delete dialog
  const openDeleteDialog = (cls, e) => {
    e.stopPropagation()
    setSelectedClass(cls)
    setShowDeleteDialog(true)
  }

  // Navigate to class details
  const handleClassClick = (cls) => {
    navigate(`/class/${cls.id}`)
  }

  // Navigate back to admin dashboard
  const handleBackClick = () => {
    navigate('/admin')
  }

  if (loading && classes.length === 0) {
    return (
      <Layout title="Manage Classes">
        <LoadingSpinner message="Loading classes..." />
      </Layout>
    )
  }

  if (error && classes.length === 0) {
    return (
      <Layout title="Manage Classes">
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
          <button onClick={refresh} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Manage Classes">
      {/* Back Navigation */}
      <div style={styles.backNav}>
        <button onClick={handleBackClick} style={styles.backButton}>
          ← Back to Dashboard
        </button>
      </div>

      {/* Classes Table */}
      <Card title={`All Classrooms (${classes.length})`}>
        <div style={styles.cardHeader}>
          <button onClick={() => setShowAddModal(true)} style={styles.addButton}>
            + Add Classroom
          </button>
        </div>

        {classes.length === 0 ? (
          <EmptyState
            icon="📚"
            title="No Classrooms Yet"
            message="Your school doesn't have any classrooms set up. Create your first classroom to start organizing students and tracking their progress."
            actionLabel="+ Add Your First Classroom"
            onAction={() => setShowAddModal(true)}
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
                  onClick={() => handleClassClick(cls)}
                >
                  <td style={styles.td}>
                    <div style={styles.classNameCell}>
                      <span style={styles.classIcon}>📚</span>
                      {cls.name}
                    </div>
                  </td>
                  <td style={styles.td}>
                    {cls.grade_level ? (
                      <span style={styles.gradeBadge}>{cls.grade_level}</span>
                    ) : '-'}
                  </td>
                  <td style={styles.td}>
                    <span style={styles.studentCount}>
                      {cls.student_count || cls.studentCount || 0}
                    </span>
                  </td>
                  <td style={styles.td}>
                    {cls.teacher_name || cls.primary_teacher?.name || '-'}
                  </td>
                  <td style={styles.td}>
                    <div style={styles.actions}>
                      <button
                        onClick={(e) => openEditModal(cls, e)}
                        style={styles.actionBtn}
                        title="Edit classroom"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={(e) => openDeleteDialog(cls, e)}
                        style={styles.actionBtn}
                        title="Delete classroom"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>


      {/* Add Classroom Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => { setShowAddModal(false); resetForm(); }}
        title="Add New Classroom"
        actions={
          <>
            <button 
              onClick={() => { setShowAddModal(false); resetForm(); }} 
              style={styles.cancelButton}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              onClick={handleAddClass} 
              style={styles.submitButton}
              disabled={submitting || !className.trim()}
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
              value={className}
              onChange={(e) => setClassName(e.target.value)}
              placeholder="e.g., Nursery A, KG-B"
              style={styles.input}
              autoFocus
            />
          </div>
          <div style={styles.formGroup}>
            <label style={styles.label}>Grade Level</label>
            <input
              type="text"
              value={gradeLevel}
              onChange={(e) => setGradeLevel(e.target.value)}
              placeholder="e.g., Pre-K, Kindergarten"
              style={styles.input}
            />
          </div>
        </form>
      </Modal>

      {/* Edit Classroom Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => { setShowEditModal(false); setSelectedClass(null); resetForm(); }}
        title="Edit Classroom"
        actions={
          <>
            <button 
              onClick={() => { setShowEditModal(false); setSelectedClass(null); resetForm(); }} 
              style={styles.cancelButton}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              onClick={handleEditClass} 
              style={styles.submitButton}
              disabled={submitting || !className.trim()}
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
              value={className}
              onChange={(e) => setClassName(e.target.value)}
              placeholder="e.g., Nursery A, KG-B"
              style={styles.input}
              autoFocus
            />
          </div>
          <div style={styles.formGroup}>
            <label style={styles.label}>Grade Level</label>
            <input
              type="text"
              value={gradeLevel}
              onChange={(e) => setGradeLevel(e.target.value)}
              placeholder="e.g., Pre-K, Kindergarten"
              style={styles.input}
            />
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        onClose={() => { setShowDeleteDialog(false); setSelectedClass(null); }}
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
  backNav: {
    marginBottom: '1.5rem'
  },
  backButton: {
    padding: '0.5rem 1rem',
    background: '#f1f3f5',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.875rem',
    color: '#495057',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  },
  cardHeader: {
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
    borderBottom: '1px solid #f1f3f5',
    transition: 'background 0.2s'
  },
  td: {
    padding: '1rem 0.75rem',
    fontSize: '0.875rem'
  },
  classNameCell: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem'
  },
  classIcon: {
    fontSize: '1.25rem'
  },
  gradeBadge: {
    padding: '0.25rem 0.75rem',
    background: '#e7f3ff',
    color: '#4a90e2',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '500'
  },
  studentCount: {
    fontWeight: '600',
    color: '#4a90e2'
  },
  actions: {
    display: 'flex',
    gap: '0.5rem'
  },
  actionBtn: {
    padding: '0.25rem 0.5rem',
    background: 'transparent',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.875rem'
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
