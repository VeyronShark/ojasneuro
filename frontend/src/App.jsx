import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import AdminDashboard from './pages/AdminDashboard'
import TeacherDashboard from './pages/TeacherDashboard'
import ClassView from './pages/ClassView'
import ChildProfile from './pages/ChildProfile'
import SkillSuggestions from './pages/SkillSuggestions'
import ParentCommunication from './pages/ParentCommunication'
import ManageTeachers from './pages/ManageTeachers'
import ManageClasses from './pages/ManageClasses'
import ManageStudents from './pages/ManageStudents'

// Loading spinner component
function LoadingScreen() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f8f9fa'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '3px solid #e1e4e8',
          borderTopColor: '#4a90e2',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 1rem'
        }} />
        <p style={{ color: '#6c757d' }}>Loading...</p>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  )
}

// Protected route wrapper
function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated, loading } = useAuth()

  if (loading) {
    return <LoadingScreen />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    // Redirect to appropriate dashboard based on role
    return <Navigate to={user?.role === 'admin' ? '/admin' : '/teacher'} replace />
  }

  return children
}

// App routes component that uses auth context
function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen />
  }

  return (
    <Routes>
      <Route path="/login" element={
        user ? <Navigate to={user.role === 'admin' ? '/admin' : '/teacher'} replace /> : <Login />
      } />
      <Route path="/admin" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <AdminDashboard />
        </ProtectedRoute>
      } />
      <Route path="/admin/teachers" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <ManageTeachers />
        </ProtectedRoute>
      } />
      <Route path="/admin/classes" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <ManageClasses />
        </ProtectedRoute>
      } />
      <Route path="/admin/students" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <ManageStudents />
        </ProtectedRoute>
      } />
      <Route path="/teacher" element={
        <ProtectedRoute allowedRoles={['teacher']}>
          <TeacherDashboard />
        </ProtectedRoute>
      } />
      <Route path="/class/:classId" element={
        <ProtectedRoute allowedRoles={['teacher', 'admin']}>
          <ClassView />
        </ProtectedRoute>
      } />
      <Route path="/child/:childId" element={
        <ProtectedRoute allowedRoles={['teacher', 'admin']}>
          <ChildProfile />
        </ProtectedRoute>
      } />
      <Route path="/skills" element={
        <ProtectedRoute allowedRoles={['teacher', 'admin']}>
          <SkillSuggestions />
        </ProtectedRoute>
      } />
      <Route path="/communication" element={
        <ProtectedRoute>
          <ParentCommunication />
        </ProtectedRoute>
      } />
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
