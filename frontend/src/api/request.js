import axios from 'axios'
import { getToken, removeToken, removeUser } from '../utils/auth'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '',
  timeout: 15000,
})

request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.error || error.message || '请求失败'
    if (error.response?.status === 401) {
      removeToken()
      removeUser()
      router.push('/login')
      ElMessage.error('登录已过期/或用户名密码错误，请重新登录')
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request
