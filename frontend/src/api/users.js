import request from './request'
import { getToken } from '../utils/auth'

export function getUsers(params) {
  return request.get('/api/users', { params })
}

export function createUser(data) {
  return request.post('/api/users', data)
}

export function updateUser(id, data) {
  return request.put(`/api/users/${id}`, data)
}

export function deleteUser(id) {
  return request.delete(`/api/users/${id}`)
}

export function downloadUserImportTemplate() {
  return fetch('/api/users/import/template', {
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

export function importUsers(formData) {
  return request.post('/api/users/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function getLoginLogs(params) {
  return request.get('/api/login-logs', { params })
}
