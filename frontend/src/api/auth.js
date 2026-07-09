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
