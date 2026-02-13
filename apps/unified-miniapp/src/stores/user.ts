/**
 * User store - 统一小程序用户状态管理
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
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userRole = computed(() => user.value?.role || '')
  const hasPhone = computed(() => !!user.value?.phone)
  const hasEmail = computed(() => !!user.value?.email)
  const hasWechat = computed(() => !!user.value?.wechat_bindded)

  function initFromStorage() {
    const storedToken = uni.getStorageSync('token')
    const storedUser = uni.getStorageSync('user')
    const storedStudent = uni.getStorageSync('currentStudent')

    if (storedToken) token.value = storedToken
    if (storedUser) {
      try { user.value = JSON.parse(storedUser) } catch (e) { /* ignore */ }
    }
    if (storedStudent) {
      try { currentStudent.value = JSON.parse(storedStudent) } catch (e) { /* ignore */ }
    }
  }

  function saveLoginState(accessToken: string, userData: User) {
    token.value = accessToken
    user.value = userData
    uni.setStorageSync('token', accessToken)
    uni.setStorageSync('user', JSON.stringify(userData))
  }

  async function login(account: string, password: string) {
    const res = await authApi.login(account, password)
    saveLoginState(res.access_token, res.user)
    return res
  }

  async function loginWithEmail(email: string, code: string) {
    const res = await authApi.loginWithEmail(email, code)
    saveLoginState(res.access_token, res.user)
    return res
  }

  async function wechatLogin(code: string, deviceId?: string) {
    const res = await authApi.wechatLogin(code, deviceId)
    saveLoginState(res.access_token, res.user)
    return res
  }

  async function wechatPhoneLogin(code: string, phoneCode: string, deviceId?: string) {
    const res = await authApi.wechatPhoneLogin(code, phoneCode, deviceId)
    saveLoginState(res.access_token, res.user)
    return res
  }

  async function register(email: string, password: string, role: string = 'parent', nickname?: string, phone?: string) {
    const res = await authApi.register(email, password, role, nickname, phone)
    saveLoginState(res.access_token, res.user)
    return res
  }

  async function registerWithEmail(email: string, code: string, password: string, role: string = 'parent', nickname?: string, phone?: string) {
    const res = await authApi.registerWithEmail(email, code, password, role, nickname, phone)
    saveLoginState(res.access_token, res.user)
    return res
  }

  async function registerWithRole(email: string, wechatOpenid: string, role: string, nickname?: string) {
    const res = await authApi.registerWithRole({
      email: email || undefined,
      wechat_openid: wechatOpenid || undefined,
      role,
      nickname
    })
    saveLoginState(res.access_token, res.user)
    return res
  }

  async function sendEmailCode(email: string) {
    const res: any = await authApi.sendEmailCode(email)
    return { success: true, delivery: res?.delivery || 'smtp', devCode: res?.dev_code || '' }
  }

  async function resetPassword(email: string, code: string, newPassword: string) {
    await authApi.resetPassword(email, code, newPassword)
    return true
  }

  async function fetchUserInfo() {
    if (!token.value) return null
    try {
      const res = await authApi.getUserInfo()
      user.value = res
      uni.setStorageSync('user', JSON.stringify(res))
      return res
    } catch (error) {
      console.error('Fetch user failed:', error)
      return null
    }
  }

  async function updateUserInfo(data: { nickname?: string; avatar?: string; phone?: string }) {
    const res = await authApi.updateUserInfo(data)
    user.value = res
    uni.setStorageSync('user', JSON.stringify(res))
    return res
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
    token, user, currentStudent, students,
    isLoggedIn, isParent, isStudent, isCoach, isAdmin, userRole,
    hasPhone, hasEmail, hasWechat,
    initFromStorage, login, loginWithEmail, wechatLogin, wechatPhoneLogin,
    register, registerWithEmail, registerWithRole, sendEmailCode, resetPassword,
    fetchUserInfo, updateUserInfo, logout,
    setCurrentStudent, setUser, checkLogin
  }
})
