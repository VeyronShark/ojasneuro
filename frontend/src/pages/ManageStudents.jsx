/**
 * ManageStudents - Admin page for viewing all students across all classes
 * Requirements: 7.1, 7.2, 7.3 - View all students, search/filter, click-through to profile
 */
import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Layout from '../components/Layout'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import { schoolsAPI } from '../api/config'

export default function ManageStudents() {
  const navigate = useNavigate()
  const { user } = useAuth()
  
  // Get school ID from user
  const schoolId = user?.school_id || user?.schoolId
  
  // Students state
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch all students
  useEffect(() => {
    async function fetchStudents() {
      if (!schoolId) return
      
      setLoading(true)
      setError(null)
      try {
        const response = await schoolsAPI.getAllStudents(schoolId)
        setStudents(response.students || response.children || response || [])
      } catch (err) {
        setError(err.message || 'Failed to load students')
      } finally {
        setLoading(false)
      }
    }
    
    fetchStudents()
  }, [schoolId])

  // Filter students by search query (case-insensitive)
  const filteredStudents = useMemo(() => {
    if (!searchQuery.trim()) return students
    const searchLower = searchQuery.toLowerCase()
    return students.filter(student => {
      const name = student.display_name || student.name || ''
      return name.toLowerCase().includes(searchLower)
    })
  }, [students, searchQuery])

  // Navigate to student profile
  const handleStudentClick = (student) => {
    navigate(`/child/${student.id}`)
  }

  // Navigate back to admin dashboard
  const handleBackClick = () => {
    navigate('/admin')
  }

  // Clear search
  const handleClearSearch = () => {
    setSearchQuery('')
  }

  if (loading) {
    return (
      <Layout title="Manage Students">
        <LoadingSpinner message="Loading students..." />
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout title="Manage Students">
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
    <Layout title="Manage Students">
      {/* Back Navigation */}
      <div style={styles.backNav}>
        <button onClick={handleBackClick} style={styles.backButton}>
          ← Back to Dashboard
        </button>
      </div>

      {/* Students Table */}
      <Card title={`All Students (${students.length})`}>
        {/* Search Bar */}
        <div style={styles.searchSection}>
          <div style={styles.searchContainer}>
            <span style={styles.searchIcon}>🔍</span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search students by name..."
              style={styles.searchInput}
            />
            {searchQuery && (
              <button 
                onClick={handleClearSearch} 
                style={styles.clearSearchBtn}
                title="Clear search"
              >
                ×
              </button>
            )}
          </div>
          {searchQuery && (
            <div style={styles.searchInfo}>
              Showing {filteredStudents.length} of {students.length} students
            </div>
          )}
        </div>


        {students.length === 0 ? (
          <EmptyState
            icon="👦"
            title="No Students Yet"
            message="Your school doesn't have any students enrolled. Students can be added to classrooms by teachers or administrators."
            actionLabel="Go to Classes"
            onAction={() => navigate('/admin/classes')}
          />
        ) : filteredStudents.length === 0 ? (
          <EmptyState
            icon="🔍"
            title="No Matching Students"
            message={`No students match your search "${searchQuery}". Try a different search term or clear the search.`}
            actionLabel="Clear Search"
            onAction={handleClearSearch}
          />
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Age</th>
                <th style={styles.th}>Class</th>
                <th style={styles.th}>Child Code</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map(student => (
                <tr 
                  key={student.id} 
                  style={styles.row}
                  onClick={() => handleStudentClick(student)}
                >
                  <td style={styles.td}>
                    <div style={styles.studentName}>
                      <span style={styles.avatar}>
                        {(student.display_name || student.name || 'S').charAt(0).toUpperCase()}
                      </span>
                      {student.display_name || student.name}
                    </div>
                  </td>
                  <td style={styles.td}>
                    {student.age ? `${student.age} years` : '-'}
                  </td>
                  <td style={styles.td}>
                    <span style={styles.classBadge}>
                      {student.class_name || student.class?.name || '-'}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <code style={styles.code}>{student.child_code || '-'}</code>
                  </td>
                  <td style={styles.td}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleStudentClick(student)
                      }}
                      style={styles.viewButton}
                      title="View profile"
                    >
                      View Profile →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
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
  searchSection: {
    marginBottom: '1.5rem'
  },
  searchContainer: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    maxWidth: '400px'
  },
  searchIcon: {
    position: 'absolute',
    left: '12px',
    fontSize: '1rem',
    pointerEvents: 'none'
  },
  searchInput: {
    width: '100%',
    padding: '0.75rem 2.5rem 0.75rem 2.5rem',
    border: '1px solid #e1e4e8',
    borderRadius: '8px',
    fontSize: '0.9375rem',
    outline: 'none',
    transition: 'border-color 0.2s'
  },
  clearSearchBtn: {
    position: 'absolute',
    right: '12px',
    background: 'transparent',
    border: 'none',
    fontSize: '1.5rem',
    color: '#6c757d',
    cursor: 'pointer',
    padding: '0',
    lineHeight: 1
  },
  searchInfo: {
    marginTop: '0.5rem',
    fontSize: '0.875rem',
    color: '#6c757d'
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
  studentName: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem'
  },
  avatar: {
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.9375rem',
    fontWeight: '600'
  },
  classBadge: {
    padding: '0.25rem 0.75rem',
    background: '#e7f3ff',
    color: '#4a90e2',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '500'
  },
  code: {
    padding: '0.25rem 0.5rem',
    background: '#f1f3f5',
    borderRadius: '4px',
    fontSize: '0.8125rem',
    fontFamily: 'monospace'
  },
  viewButton: {
    padding: '0.375rem 0.75rem',
    background: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.8125rem',
    fontWeight: '500'
  },
  emptyState: {
    textAlign: 'center',
    padding: '2rem',
    color: '#6c757d'
  },
  clearButton: {
    marginTop: '1rem',
    padding: '0.5rem 1rem',
    background: '#f1f3f5',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.875rem',
    color: '#495057'
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
  }
}
