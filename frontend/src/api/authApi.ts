import api from './axios'
import type { User, TokenResponse } from '../types'

export const login = (data: { username: string; password: string }) =>
  api.post<TokenResponse>('/auth/login', data)
export const getMe = () => api.get<User>('/auth/me')
export const changePassword = (data: { current_password: string; new_password: string }) =>
  api.put('/auth/me/password', data)
export const listUsers = () => api.get<User[]>('/auth/users')
export const createUser = (data: Partial<User> & { password: string }) =>
  api.post<User>('/auth/users', data)
export const updateUser = (id: string, data: Partial<User>) =>
  api.put<User>(`/auth/users/${id}`, data)
