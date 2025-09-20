import { defineStore } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null')
  }),
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem('token', token)
    },
    setUserInfo(userInfo: any) {
      this.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },
    clearUserInfo() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  },
  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['token', 'userInfo']
  }
})

export const piniaPersistedState = createPersistedState()

import { useAppStore } from './modules/app/app'
import { useFontStore } from './modules/font/font'

const pinia = createPinia()

export default pinia

export {
    useAppStore,
    useFontStore,
}