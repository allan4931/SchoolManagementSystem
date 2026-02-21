import api from './axios'
import type { Bus, TransportRoute } from '../types'

export const getBuses = () => api.get<Bus[]>('/transport/buses')
export const addBus = (data: Partial<Bus>) => api.post<Bus>('/transport/buses', data)
export const updateBus = (id: string, data: Partial<Bus>) =>
  api.put<Bus>(`/transport/buses/${id}`, data)
export const getRoutes = () => api.get<TransportRoute[]>('/transport/routes')
export const createRoute = (data: Partial<TransportRoute>) =>
  api.post<TransportRoute>('/transport/routes', data)
export const assignTransport = (data: Record<string, unknown>) =>
  api.post('/transport/assign', data)
export const getAssignments = () => api.get('/transport/assignments')
export const removeAssignment = (studentId: string) =>
  api.delete(`/transport/assignments/${studentId}`)
