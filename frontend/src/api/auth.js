import request from './request'

export function login(data) {
  return request.post('/api/auth/login', data)
}

export function changePassword(data) {
  return request.put('/api/auth/password', data)
}

export function getCurrentUser() {
  return request.get('/api/users/me')
}

export function updateCurrentUser(data) {
  return request.put('/api/users/me', data)
}

export function getMcpCode() {
  return request.get('/api/auth/mcp-code')
}

export function generateMcpCode() {
  return request.post('/api/auth/mcp-code')
}

export function deleteMcpCode() {
  return request.delete('/api/auth/mcp-code')
}
