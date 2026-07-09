import request from './request'

export function getRooms(params) {
  return request.get('/api/rooms', { params })
}

export function createRoom(data) {
  return request.post('/api/rooms', data)
}

export function updateRoom(id, data) {
  return request.put(`/api/rooms/${id}`, data)
}

export function deleteRoom(id) {
  return request.delete(`/api/rooms/${id}`)
}
