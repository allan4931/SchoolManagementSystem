import api from './axios'
import type { InventoryItem, PaginatedResponse } from '../types'

export const getInventory = (params?: Record<string, unknown>) =>
  api.get<PaginatedResponse<InventoryItem> | InventoryItem[]>('/inventory', { params })
export const addItem = (data: Partial<InventoryItem>) =>
  api.post<InventoryItem>('/inventory', data)
export const updateItem = (id: string, data: Partial<InventoryItem>) =>
  api.put<InventoryItem>(`/inventory/${id}`, data)
export const deleteItem = (id: string) => api.delete(`/inventory/${id}`)
export const addMaintenance = (id: string, data: Record<string, unknown>) =>
  api.post(`/inventory/${id}/maintenance`, data)
export const getMaintenanceHistory = (id: string) =>
  api.get(`/inventory/${id}/maintenance`)
