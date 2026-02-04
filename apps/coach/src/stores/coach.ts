import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { coachApi, authApi } from '@/api'

interface CoachInfo {
  id: number
  name: string
  phone: string
  avatar: string | null
  coach_no: string
  specialties: string[]
  introduction: string
  hourly_rate: number
}

export const useCoachStore = defineStore('coach', () => {
  const coachInfo = ref<CoachInfo | null>(null)
  const token = ref<string>(uni.getStorageSync('token') || '')

  const isLoggedIn = computed(() => !!token.value)

  async function login(phone: string, password: string) {
    try {
      const res = await authApi.login({ phone, password })
      token.value = res.access_token
      uni.setStorageSync('token', res.access_token)
      await fetchProfile()
      return true
    } catch (error) {
      throw error
    }
  }

  function logout() {
    token.value = ''
    coachInfo.value = null
    uni.removeStorageSync('token')
    uni.reLaunch({ url: '/pages/user/login' })
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const res = await coachApi.getProfile()
      coachInfo.value = res
    } catch (error) {
      console.error('获取教练信息失败:', error)
    }
  }

  return {
    coachInfo,
    token,
    isLoggedIn,
    login,
    logout,
    fetchProfile
  }
})
