/**
 * User store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

interface User {
  id: number
  phone: string | null
  nickname: string | null
  avatar: string | null
  role: string
  status: string
  wechat_bindded?: boolean
}

interface Student {
  id: number
  student_no: string
  name: string
  gender: string | null
  remaining_lessons: number
}

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const user = ref<User | null>(null)
  const currentStudent = ref<Student | null>(null)
  const students = ref<Student[]>([])

  const isLoggedIn = computed(() => !!token.value)
  const isParent = computed(() => user.value?.role === 'parent')
  const isStudent = computed(() => user.value?.role === 'student')
  const isCoach = computed(() => user.value?.role === 'coach')
  const hasPhone = computed(() => !!user.value?.phone)
  const hasWechat = computed(() => !!user.value?.wechat_bindded)

  function initFromStorage() {
    const storedToken = uni.getStorageSync('token')
    const storedUser = uni.getStorageSync('user')
    const storedStudent = uni.getStorageSync('currentStudent')

    if (storedToken) {
      token.value = storedToken
    }
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Failed to parse user')
      }
    }
    if (storedStudent) {
      try {
        currentStudent.value = JSON.parse(storedStudent)
      } catch (e) {
        console.error('Failed to parse student')
      }
    }
  }

  function saveLoginState(accessToken: string, userData: User) {
    token.value = accessToken
    user.value = userData
    uni.setStorageSync('token', accessToken)
    uni.setStorageSync('user', JSON.stringify(userData))
  }

  async function login(phone: string, password: string) {
    try {
      const res = await authApi.login(phone, password)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || 'Login failed')
    }
  }

  async function loginWithSms(phone: string, code: string) {
    try {
      const res = await authApi.loginWithSms(phone, code)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || 'Login failed')
    }
  }

  async function wechatLogin(code: string, userInfo?: any) {
    try {
      const res = await authApi.wechatLogin(code, userInfo)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || 'WeChat login failed')
    }
  }

  async function wechatPhoneLogin(code: string, phoneCode: string) {
    try {
      const res = await authApi.wechatPhoneLogin(code, phoneCode)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || 'Login failed')
    }
  }

  async function register(phone: string, password: string, role: string = 'parent', nickname?: string) {
    try {
      const res = await authApi.register(phone, password, role, nickname)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || 'Register failed')
    }
  }

  async function registerWithSms(phone: string, code: string, password: string, role: string = 'parent', nickname?: string) {
    try {
      const res = await authApi.registerWithSms(phone, code, password, role, nickname)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || 'Register failed')
    }
  }

  async function sendSmsCode(phone: string) {
    try {
      await authApi.sendSmsCode(phone)
      return true
    } catch (error: any) {
      throw new Error(error.message || 'Send failed')
    }
  }

  async function resetPassword(phone: string, code: string, newPassword: string) {
    try {
      await authApi.resetPassword(phone, code, newPassword)
      return true
    } catch (error: any) {
      throw new Error(error.message || 'Reset failed')
    }
  }

  async function fetchUserInfo() {
    if (!token.value) return null
    try {
      const res = await authApi.getUserInfo()
      user.value = res
      uni.setStorageSync('user', JSON.stringify(res))
      return res
    } catch (error: any) {
      console.error('Fetch user failed:', error)
      return null
    }
  }

  async function updateUserInfo(data: { nickname?: string; avatar?: string }) {
    try {
      const res = await authApi.updateUserInfo(data)
      user.value = res
      uni.setStorageSync('user', JSON.stringify(res))
      return res
    } catch (error: any) {
      throw new Error(error.message || 'Update failed')
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    currentStudent.value = null
    students.value = []

    uni.removeStorageSync('token')
    uni.removeStorageSync('user')
    uni.removeStorageSync('currentStudent')

    uni.reLaunch({ url: '/pages/user/login' })
  }

  function setCurrentStudent(student: Student) {
    currentStudent.value = student
    uni.setStorageSync('currentStudent', JSON.stringify(student))
  }

  function checkLogin(): boolean {
    if (!token.value) {
      uni.navigateTo({ url: '/pages/user/login' })
      return false
    }
    return true
  }

  return {
    token,
    user,
    currentStudent,
    students,
    isLoggedIn,
    isParent,
    isStudent,
    isCoach,
    hasPhone,
    hasWechat,
    initFromStorage,
    login,
    loginWithSms,
    wechatLogin,
    wechatPhoneLogin,
    register,
    registerWithSms,
    sendSmsCode,
    resetPassword,
    fetchUserInfo,
    updateUserInfo,
    logout,
    setCurrentStudent,
    checkLogin
  }
})
