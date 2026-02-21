import api from './axios'
import type { Exam, ExamResult } from '../types'

export const getExams = (params?: Record<string, unknown>) =>
  api.get<Exam[]>('/exams', { params })
export const getExam = (id: string) => api.get<Exam>(`/exams/${id}`)
export const createExam = (data: Partial<Exam>) => api.post<Exam>('/exams', data)
export const enterResults = (examId: string, data: Record<string, unknown>) =>
  api.post(`/exams/${examId}/results`, data)
export const getExamResults = (examId: string, params?: Record<string, unknown>) =>
  api.get<ExamResult[]>(`/exams/${examId}/results`, { params })
export const getClassRanking = (examId: string, classId: string) =>
  api.get(`/exams/${examId}/ranking/${classId}`)
export const publishResults = (examId: string) => api.patch(`/exams/${examId}/publish`)
export const downloadReportCard = (examId: string, studentId: string, classId: string) =>
  api.get(`/exams/${examId}/report-card/${studentId}`, {
    params: { class_id: classId },
    responseType: 'blob',
  })
