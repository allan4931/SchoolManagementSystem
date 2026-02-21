import api from './axios'

export const markStudentAttendance = (data: Record<string, unknown>) =>
  api.post('/attendance/students', data)
export const bulkMarkAttendance = (data: Record<string, unknown>) =>
  api.post('/attendance/students/bulk', data)
export const getStudentAttendanceReport = (params?: Record<string, unknown>) =>
  api.get('/attendance/students/report', { params })
export const markTeacherAttendance = (data: Record<string, unknown>) =>
  api.post('/attendance/teachers', data)
export const getTeacherAttendanceReport = (params?: Record<string, unknown>) =>
  api.get('/attendance/teachers/report', { params })
