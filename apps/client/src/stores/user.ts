/**
 * User store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

interface User {
  id: number
  phone: string | null
  email: string | null
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
  const hasEmail = computed(() => !!user.value?.email)
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

  async function login(account: string, password: string) {
    try {
      const res = await authApi.login(account, password)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  async function loginWithEmail(email: string, code: string) {
    try {
      const res = await authApi.loginWithEmail(email, code)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  async function wechatLogin(code: string, userInfo?: any, deviceId?: string) {
    try {
      const res = await authApi.wechatLogin(code, userInfo, deviceId)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '微信登录失败')
    }
  }

  async function wechatPhoneLogin(code: string, phoneCode: string, deviceId?: string) {
    try {
      const res = await authApi.wechatPhoneLogin(code, phoneCode, deviceId)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  async function register(email: string, password: string, role: string = 'parent', nickname?: string, phone?: string) {
    try {
      const res = await authApi.register(email, password, role, nickname, phone)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '注册失败')
    }
  }

  async function registerWithEmail(email: string, code: string, password: string, role: string = 'parent', nickname?: string, phone?: string) {
    try {
      const res = await authApi.registerWithEmail(email, code, password, role, nickname, phone)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '注册失败')
    }
  }

  async function sendEmailCode(email: string) {
    try {
      const res: any = await authApi.sendEmailCode(email)
      return {
        success: true,
        delivery: res?.delivery || 'smtp',
        devCode: res?.dev_code || ''
      }
    } catch (error: any) {
      throw new Error(error.message || '发送失败')
    }
  }

  async function resetPassword(email: string, code: string, newPassword: string) {
    try {
      await authApi.resetPassword(email, code, newPassword)
      return true
    } catch (error: any) {
      throw new Error(error.message || '重置失败')
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

  async function updateUserInfo(data: { nickname?: string; avatar?: string; phone?: string }) {
    try {
      const res = await authApi.updateUserInfo(data)
      user.value = res
      uni.setStorageSync('user', JSON.stringify(res))
      return res
    } catch (error: any) {
      throw new Error(error.message || '更新失败')
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

  function setUser(userData: any) {
    user.value = userData
    uni.setStorageSync('user', JSON.stringify(userData))
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
    hasEmail,
    hasWechat,
    initFromStorage,
    login,
    loginWithEmail,
    wechatLogin,
    wechatPhoneLogin,
    register,
    registerWithEmail,
    sendEmailCode,
    resetPassword,
    fetchUserInfo,
    updateUserInfo,
    logout,
    setCurrentStudent,
    setUser,
    checkLogin
  }
})
