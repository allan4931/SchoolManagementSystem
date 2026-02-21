import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import StudentList from './pages/students/StudentList'
import StudentForm from './pages/students/StudentForm'
import StudentProfile from './pages/students/StudentProfile'
import TeacherList from './pages/teachers/TeacherList'
import TeacherForm from './pages/teachers/TeacherForm'
import ClassList from './pages/classes/ClassList'
import AttendancePage from './pages/attendance/Attendance'
import FeeList from './pages/fees/FeeList'
import ExamList from './pages/exams/ExamList'
import LibraryPage from './pages/library/Library'
import TransportPage from './pages/transport/Transport'
import InventoryPage from './pages/inventory/Inventory'

function Guard({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Guard><Layout /></Guard>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="students" element={<StudentList />} />
        <Route path="students/new" element={<StudentForm />} />
        <Route path="students/:id/edit" element={<StudentForm />} />
        <Route path="students/:id" element={<StudentProfile />} />
        <Route path="teachers" element={<TeacherList />} />
        <Route path="teachers/new" element={<TeacherForm />} />
        <Route path="teachers/:id/edit" element={<TeacherForm />} />
        <Route path="classes" element={<ClassList />} />
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="fees" element={<FeeList />} />
        <Route path="exams" element={<ExamList />} />
        <Route path="library" element={<LibraryPage />} />
        <Route path="transport" element={<TransportPage />} />
        <Route path="inventory" element={<InventoryPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
