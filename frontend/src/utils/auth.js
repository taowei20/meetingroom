const TOKEN_KEY = 'meeting_room_token'
const USER_KEY = 'meeting_room_user'
const LOGIN_TIME_KEY = 'meeting_room_login_time'
const MOBILE_LOGIN_TIME_KEY = 'meeting_room_mobile_login_time'
const AUTO_LOGIN_DAYS = 10

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function setUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeUser() {
  localStorage.removeItem(USER_KEY)
}

export function setLoginTime() {
  const now = Date.now()
  localStorage.setItem(LOGIN_TIME_KEY, String(now))
  localStorage.setItem(MOBILE_LOGIN_TIME_KEY, String(now))
}

export function isMobileAutoLoginValid() {
  const ts = localStorage.getItem(MOBILE_LOGIN_TIME_KEY)
  if (!ts) return false
  const elapsed = Date.now() - Number(ts)
  return elapsed < AUTO_LOGIN_DAYS * 24 * 60 * 60 * 1000
}

export function removeLoginTime() {
  localStorage.removeItem(LOGIN_TIME_KEY)
  localStorage.removeItem(MOBILE_LOGIN_TIME_KEY)
}

export function clearAllAuth() {
  removeToken()
  removeUser()
  removeLoginTime()
}
