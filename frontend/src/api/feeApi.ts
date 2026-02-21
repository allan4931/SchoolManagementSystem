import api from './axios'
import type { FeeStructure, FeeInvoice, FeePayment } from '../types'

export const getFeeStructures = (params?: Record<string, unknown>) =>
  api.get<FeeStructure[]>('/fees/structures', { params })
export const createFeeStructure = (data: Partial<FeeStructure>) =>
  api.post<FeeStructure>('/fees/structures', data)
export const generateInvoice = (data: Record<string, unknown>) =>
  api.post<FeeInvoice>('/fees/invoices', data)
export const getInvoice = (id: string) => api.get<FeeInvoice>(`/fees/invoices/${id}`)
export const getStudentInvoices = (studentId: string) =>
  api.get<FeeInvoice[]>(`/fees/student/${studentId}/invoices`)
export const makePayment = (data: Record<string, unknown>) =>
  api.post<FeePayment>('/fees/payments', data)
export const downloadReceipt = (paymentId: string) =>
  api.get(`/fees/payments/${paymentId}/receipt`, { responseType: 'blob' })
export const getArrears = (params?: Record<string, unknown>) =>
  api.get<FeeInvoice[]>('/fees/arrears', { params })
