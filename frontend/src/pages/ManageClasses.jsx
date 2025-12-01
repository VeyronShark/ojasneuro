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
import { Plus, Edit2, Trash2, ArrowLeft, BookOpen } from 'lucide-react'
import { buttonStyles, formStyles, tableStyles, badgeStyles } from '../styles/commonStyles'

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
        <button onClick={handleBackClick} style={buttonStyles.secondary}>
          <ArrowLeft size={18} />
          <span>Back to Dashboard</span>
        </button>
      </div>

      {/* Classes Table */}
      <Card title={`All Classrooms (${classes.length})`}>
        <div style={styles.cardHeader}>
          <button onClick={() => setShowAddModal(true)} style={buttonStyles.primary}>
            <Plus size={18} />
            <span>Add Classroom</span>
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
                      <BookOpen size={20} color="var(--primary)" />
                      <span>{cls.name}</span>
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
                        style={buttonStyles.ghost}
                        title="Edit classroom"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={(e) => openDeleteDialog(cls, e)}
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
  cardHeader: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginBottom: '1.5rem'
  },
  table: tableStyles.table,
  th: tableStyles.th,
  row: tableStyles.row,
  td: tableStyles.td,
  classNameCell: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    fontWeight: '500'
  },
  gradeBadge: {
    ...badgeStyles.default,
    ...badgeStyles.primary
  },
  studentCount: {
    fontWeight: '600',
    color: 'var(--primary)'
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
