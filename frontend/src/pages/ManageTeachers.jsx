/**
 * ManageTeachers - Admin page for viewing and managing teachers
 * Requirements: 5.1, 5.2, 5.3 - View all teachers, details, and assigned classes
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Layout from '../components/Layout'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import { teachersAPI } from '../api/config'

export default function ManageTeachers() {
  const navigate = useNavigate()
  const { user } = useAuth()
  
  // Get school ID from user
  const schoolId = user?.school_id || user?.schoolId
  
  // Teachers state
  const [teachers, setTeachers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Selected teacher for details view
  const [selectedTeacher, setSelectedTeacher] = useState(null)
  const [teacherClasses, setTeacherClasses] = useState([])
  const [classesLoading, setClassesLoading] = useState(false)

  // Fetch all teachers
  useEffect(() => {
    async function fetchTeachers() {
      if (!schoolId) return
      
      setLoading(true)
      setError(null)
      try {
        const response = await teachersAPI.getAll(schoolId)
        setTeachers(response.teachers || response || [])
      } catch (err) {
        setError(err.message || 'Failed to load teachers')
      } finally {
        setLoading(false)
      }
    }
    
    fetchTeachers()
  }, [schoolId])


  // Fetch teacher's classes when selected
  useEffect(() => {
    async function fetchTeacherClasses() {
      if (!selectedTeacher) {
        setTeacherClasses([])
        return
      }
      
      setClassesLoading(true)
      try {
        const response = await teachersAPI.getClasses(selectedTeacher.id)
        setTeacherClasses(response.classes || response || [])
      } catch (err) {
        // If endpoint doesn't exist, use classes from teacher object
        setTeacherClasses(selectedTeacher.classes || [])
      } finally {
        setClassesLoading(false)
      }
    }
    
    fetchTeacherClasses()
  }, [selectedTeacher])

  // Handle teacher row click
  const handleTeacherClick = (teacher) => {
    setSelectedTeacher(selectedTeacher?.id === teacher.id ? null : teacher)
  }

  // Navigate back to admin dashboard
  const handleBackClick = () => {
    navigate('/admin')
  }

  if (loading) {
    return (
      <Layout title="Manage Teachers">
        <LoadingSpinner message="Loading teachers..." />
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout title="Manage Teachers">
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
          <button onClick={() => window.location.reload()} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Manage Teachers">
      {/* Back Navigation */}
      <div style={styles.backNav}>
        <button onClick={handleBackClick} style={styles.backButton}>
          ← Back to Dashboard
        </button>
      </div>

      {/* Teachers Table */}
      <Card title={`All Teachers (${teachers.length})`}>
        {teachers.length === 0 ? (
          <EmptyState
            icon="👩‍🏫"
            title="No Teachers Yet"
            message="Your school doesn't have any teachers registered. Teachers can sign up and join your school using the school selection during registration."
            secondaryActionLabel="Back to Dashboard"
            onSecondaryAction={handleBackClick}
          />
        ) : (
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
                <tr 
                  key={teacher.id} 
                  style={{
                    ...styles.row,
                    ...(selectedTeacher?.id === teacher.id ? styles.selectedRow : {})
                  }}
                  onClick={() => handleTeacherClick(teacher)}
                >
                  <td style={styles.td}>
                    <div style={styles.teacherName}>
                      <span style={styles.avatar}>
                        {(teacher.name || 'T').charAt(0).toUpperCase()}
                      </span>
                      {teacher.name}
                    </div>
                  </td>
                  <td style={styles.td}>{teacher.email}</td>
                  <td style={styles.td}>
                    <span style={styles.roleBadge}>{teacher.role || 'Teacher'}</span>
                  </td>
                  <td style={styles.td}>
                    {teacher.class_names?.join(', ') || 
                     teacher.classes?.map(c => c.name).join(', ') || 
                     '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>


      {/* Teacher Details Panel */}
      {selectedTeacher && (
        <Card title="Teacher Details" style={{ marginTop: '1.5rem' }}>
          <div style={styles.detailsGrid}>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Name</span>
              <span style={styles.detailValue}>{selectedTeacher.name}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Email</span>
              <span style={styles.detailValue}>{selectedTeacher.email}</span>
            </div>
            <div style={styles.detailItem}>
              <span style={styles.detailLabel}>Role</span>
              <span style={styles.detailValue}>
                <span style={styles.roleBadge}>{selectedTeacher.role || 'Teacher'}</span>
              </span>
            </div>
          </div>

          <div style={styles.classesSection}>
            <h4 style={styles.sectionTitle}>Assigned Classes</h4>
            {classesLoading ? (
              <LoadingSpinner message="Loading classes..." />
            ) : teacherClasses.length === 0 ? (
              <p style={styles.emptyText}>No classes assigned to this teacher.</p>
            ) : (
              <div style={styles.classesList}>
                {teacherClasses.map(cls => (
                  <div 
                    key={cls.id} 
                    style={styles.classCard}
                    onClick={() => navigate(`/class/${cls.id}`)}
                  >
                    <div style={styles.className}>{cls.name}</div>
                    <div style={styles.classInfo}>
                      {cls.grade_level && <span>{cls.grade_level}</span>}
                      {cls.student_count !== undefined && (
                        <span>{cls.student_count} students</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      )}
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
  selectedRow: {
    background: '#e7f3ff'
  },
  td: {
    padding: '1rem 0.75rem',
    fontSize: '0.875rem'
  },
  teacherName: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem'
  },
  avatar: {
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    background: '#4a90e2',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.875rem',
    fontWeight: '600'
  },
  roleBadge: {
    padding: '0.25rem 0.75rem',
    background: '#e7f3ff',
    color: '#4a90e2',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '500',
    textTransform: 'capitalize'
  },
  emptyState: {
    textAlign: 'center',
    padding: '2rem',
    color: '#6c757d'
  },
  emptyText: {
    color: '#6c757d',
    fontStyle: 'italic'
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
  detailsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1.5rem',
    marginBottom: '1.5rem'
  },
  detailItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem'
  },
  detailLabel: {
    fontSize: '0.75rem',
    color: '#6c757d',
    textTransform: 'uppercase',
    fontWeight: '600'
  },
  detailValue: {
    fontSize: '1rem',
    color: '#2c3e50'
  },
  classesSection: {
    borderTop: '1px solid #e1e4e8',
    paddingTop: '1rem'
  },
  sectionTitle: {
    fontSize: '0.9375rem',
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: '1rem'
  },
  classesList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '1rem'
  },
  classCard: {
    padding: '1rem',
    background: '#f8f9fa',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background 0.2s',
    border: '1px solid #e1e4e8'
  },
  className: {
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: '0.25rem'
  },
  classInfo: {
    fontSize: '0.8125rem',
    color: '#6c757d',
    display: 'flex',
    gap: '0.75rem'
  }
}
