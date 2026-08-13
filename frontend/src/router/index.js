import { createRouter, createWebHistory } from 'vue-router'
import { getToken, setToken } from '../utils/auth'
import { useUserStore } from '../store/user'
import { getCurrentUser } from '../api/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/UserManage.vue'),
        meta: { title: '用户管理', admin: true },
      },
      {
        path: 'rooms',
        name: 'Rooms',
        component: () => import('../views/RoomManage.vue'),
        meta: { title: '会议室管理', admin: true },
      },
      {
        path: 'booking',
        name: 'Booking',
        component: () => import('../views/Booking.vue'),
        meta: { title: '会议室预订' },
      },
      {
        path: 'my-bookings',
        name: 'MyBookings',
        component: () => import('../views/MyBookings.vue'),
        meta: { title: '我的预订' },
      },
      {
        path: 'admin-bookings',
        name: 'AdminBookings',
        component: () => import('../views/AdminBookings.vue'),
        meta: { title: '预订管理', admin: true },
      },
      {
        path: 'login-logs',
        name: 'LoginLogs',
        component: () => import('../views/LoginLog.vue'),
        meta: { title: '登录日志', admin: true },
      },
      {
        path: 'api-docs',
        name: 'ApiDocs',
        component: () => import('../views/ApiDocs.vue'),
        meta: { title: 'API接口' },
      },
      {
        path: 'change-password',
        name: 'ChangePassword',
        component: () => import('../views/ChangePassword.vue'),
        meta: { title: '修改密码' },
      },
      {
        path: 'user-info',
        name: 'UserInfo',
        component: () => import('../views/UserInfo.vue'),
        meta: { title: '个人信息' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const urlParams = new URLSearchParams(window.location.search)
  const urlToken = urlParams.get('token')
  const cleanPath = window.location.pathname + window.location.hash

  if (urlToken) {
    setToken(urlToken)
    try {
      const user = await getCurrentUser()
      const userStore = useUserStore()
      userStore.setUser(user)
      window.history.replaceState({}, '', cleanPath)
      return next('/')
    } catch (e) {
      window.history.replaceState({}, '', cleanPath)
      return next('/login')
    }
  }

  const token = getToken()
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else if (to.meta.admin) {
    const userStore = useUserStore()
    if (!userStore.isAdmin) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
