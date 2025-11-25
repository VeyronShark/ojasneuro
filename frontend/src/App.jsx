import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Login from './pages/Login'
import AdminDashboard from './pages/AdminDashboard'
import TeacherDashboard from './pages/TeacherDashboard'
import ClassView from './pages/ClassView'
import ChildProfile from './pages/ChildProfile'
import SkillSuggestions from './pages/SkillSuggestions'
import ParentCommunication from './pages/ParentCommunication'

function App() {
  const [user, setUser] = useState(null)

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/admin" element={user?.role === 'admin' ? <AdminDashboard user={user} /> : <Navigate to="/login" />} />
        <Route path="/teacher" element={user?.role === 'teacher' ? <TeacherDashboard user={user} /> : <Navigate to="/login" />} />
        <Route path="/class/:classId" element={user?.role === 'teacher' ? <ClassView user={user} /> : <Navigate to="/login" />} />
        <Route path="/child/:childId" element={user?.role === 'teacher' ? <ChildProfile user={user} /> : <Navigate to="/login" />} />
        <Route path="/skills" element={user?.role === 'teacher' ? <SkillSuggestions user={user} /> : <Navigate to="/login" />} />
        <Route path="/communication" element={user ? <ParentCommunication user={user} /> : <Navigate to="/login" />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
