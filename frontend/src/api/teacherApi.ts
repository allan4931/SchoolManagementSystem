import api from './axios'
import type { Teacher, PaginatedResponse } from '../types'

export const getTeachers = (params?: Record<string, unknown>) =>
  api.get<PaginatedResponse<Teacher>>('/teachers', { params })
export const getTeacher = (id: string) => api.get<Teacher>(`/teachers/${id}`)
export const createTeacher = (data: Partial<Teacher>) => api.post<Teacher>('/teachers', data)
export const updateTeacher = (id: string, data: Partial<Teacher>) =>
  api.put<Teacher>(`/teachers/${id}`, data)
export const deleteTeacher = (id: string) => api.delete(`/teachers/${id}`)
export const uploadTeacherPhoto = (id: string, file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<{ photo_url: string }>(`/teachers/${id}/photo`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const assignSubject = (id: string, data: Record<string, unknown>) =>
  api.post(`/teachers/${id}/subjects`, data)
export const getTeacherSubjects = (id: string) => api.get(`/teachers/${id}/subjects`)
export const addSalaryRecord = (id: string, data: Record<string, unknown>) =>
  api.post(`/teachers/${id}/salary`, data)
export const getSalaryRecords = (id: string) => api.get(`/teachers/${id}/salary`)
