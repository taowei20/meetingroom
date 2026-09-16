import { defineStore } from 'pinia'
import { getUser, setUser, clearAllAuth } from '../utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: getUser(),
  }),
  getters: {
    isLoggedIn: (state) => !!state.user,
    isAdmin: (state) => state.user?.is_admin === true,
    userName: (state) => state.user?.name || '',
    userId: (state) => state.user?.id || null,
  },
  actions: {
    setUser(data) {
      this.user = data
      setUser(data)
    },
    logout() {
      this.user = null
      clearAllAuth()
    },
    updateUser(data) {
      this.user = { ...this.user, ...data }
      setUser(this.user)
    },
  },
})
