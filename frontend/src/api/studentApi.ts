import api from './axios'
import type { Student, PaginatedResponse } from '../types'

export const getStudents = (params?: Record<string, unknown>) =>
  api.get<PaginatedResponse<Student>>('/students', { params })
export const getStudent = (id: string) => api.get<Student>(`/students/${id}`)
export const createStudent = (data: Partial<Student>) => api.post<Student>('/students', data)
export const updateStudent = (id: string, data: Partial<Student>) =>
  api.put<Student>(`/students/${id}`, data)
export const deleteStudent = (id: string) => api.delete(`/students/${id}`)
export const uploadPhoto = (id: string, file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<{ photo_url: string }>(`/students/${id}/photo`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const transferStudent = (id: string, data: Record<string, unknown>) =>
  api.post(`/students/${id}/transfer`, data)
export const suspendStudent = (id: string, data: Record<string, unknown>) =>
  api.post(`/students/${id}/suspend`, data)
