import request from './request'

export function getBookings(params) {
  return request.get('/api/bookings', { params })
}

export function getMonthlyBookings(params) {
  return request.get('/api/bookings/month', { params })
}

export function createBooking(data) {
  return request.post('/api/bookings', data)
}

export function cancelBooking(id) {
  return request.delete(`/api/bookings/${id}`)
}

export function getMyBookings() {
  return request.get('/api/bookings/my')
}

export function getMyBookingsHistory(params) {
  return request.get('/api/bookings/my/history', { params })
}

export function getAllBookings(params) {
  return request.get('/api/bookings/all', { params })
}

export function transferBooking(id, data) {
  return request.put(`/api/bookings/${id}/transfer`, data)
}

export function uploadAttachment(id, formData) {
  return request.post(`/api/bookings/${id}/attachment`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getUserOptions(params) {
  return request.get('/api/users/options', { params })
}

export function getStatsOverview() {
  return request.get('/api/stats/overview')
}

export function getSystemBookings() {
  return request.get('/api/system-bookings')
}

export function createSystemBooking(data) {
  return request.post('/api/system-bookings', data)
}

export function updateSystemBooking(id, data) {
  return request.put(`/api/system-bookings/${id}`, data)
}

export function deleteSystemBooking(id) {
  return request.delete(`/api/system-bookings/${id}`)
}
