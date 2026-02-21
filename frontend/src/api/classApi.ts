import api from './axios'
import type { Class, Subject, Student } from '../types'

export const getClasses = () => api.get<Class[]>('/classes')
export const getClass = (id: string) => api.get<Class>(`/classes/${id}`)
export const createClass = (data: Partial<Class>) => api.post<Class>('/classes', data)
export const updateClass = (id: string, data: Partial<Class>) =>
  api.put<Class>(`/classes/${id}`, data)
export const deleteClass = (id: string) => api.delete(`/classes/${id}`)
export const getClassStudents = (id: string) => api.get<Student[]>(`/classes/${id}/students`)
export const getTimetable = (id: string) => api.get(`/classes/${id}/timetable`)
export const addTimetableSlot = (id: string, data: Record<string, unknown>) =>
  api.post(`/classes/${id}/timetable`, data)
export const getSubjects = () => api.get<Subject[]>('/subjects')
export const createSubject = (data: Partial<Subject>) => api.post<Subject>('/subjects', data)
export const updateSubject = (id: string, data: Partial<Subject>) =>
  api.put<Subject>(`/subjects/${id}`, data)
export const deleteSubject = (id: string) => api.delete(`/subjects/${id}`)
