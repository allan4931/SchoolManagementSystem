import api from './axios'
import type { Book, LibraryIssue, PaginatedResponse } from '../types'

export const getBooks = (params?: Record<string, unknown>) =>
  api.get<PaginatedResponse<Book> | Book[]>('/library/books', { params })
export const getBook = (id: string) => api.get<Book>(`/library/books/${id}`)
export const addBook = (data: Partial<Book>) => api.post<Book>('/library/books', data)
export const updateBook = (id: string, data: Partial<Book>) =>
  api.put<Book>(`/library/books/${id}`, data)
export const issueBook = (data: Record<string, unknown>) =>
  api.post('/library/issue', data)
export const returnBook = (data: Record<string, unknown>) =>
  api.post('/library/return', data)
export const getFines = () => api.get<LibraryIssue[]>('/library/fines')
export const getStudentHistory = (studentId: string) =>
  api.get<LibraryIssue[]>(`/library/history/${studentId}`)
