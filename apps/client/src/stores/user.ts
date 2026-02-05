/**
 * 用户状态管理
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
  // 状态
  const token = ref('')
  const user = ref<User | null>(null)
  const currentStudent = ref<Student | null>(null)
  const students = ref<Student[]>([])

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isParent = computed(() => user.value?.role === 'parent')
  const isStudent = computed(() => user.value?.role === 'student')
  const isCoach = computed(() => user.value?.role === 'coach')
  const hasPhone = computed(() => !!user.value?.phone)
  const hasWechat = computed(() => !!user.value?.wechat_bindded)

  // 从存储初始化
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
        console.error('解析用户信息失败')
      }
    }
    if (storedStudent) {
      try {
        currentStudent.value = JSON.parse(storedStudent)
      } catch (e) {
        console.error('解析学员信息失败')
      }
    }
  }

  // 保存登录状态
  function saveLoginState(accessToken: string, userData: User) {
    token.value = accessToken
    user.value = userData
    uni.setStorageSync('token', accessToken)
    uni.setStorageSync('user', JSON.stringify(userData))
  }

  // 手机号密码登录
  async function login(phone: string, password: string) {
    try {
      const res = await authApi.login(phone, password)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  // 邮箱验证码登录
  async function emailLogin(email: string, code: string) {
    try {
      const res = await authApi.emailLogin(email, code)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  // 短信验证码登录
  async function loginWithSms(phone: string, code: string) {
    try {
      const res = await authApi.loginWithSms(phone, code)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  // 微信登录
  async function wechatLogin(code: string, userInfo?: any) {
    try {
      const res = await authApi.wechatLogin(code, userInfo)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '微信登录失败')
    }
  }

  // 微信手机号登录
  async function wechatPhoneLogin(code: string, phoneCode: string) {
    try {
      const res = await authApi.wechatPhoneLogin(code, phoneCode)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  // 注册
  async function register(phone: string, password: string, role: string = 'parent', nickname?: string) {
    try {
      const res = await authApi.register(phone, password, role, nickname)
      saveLoginState(res.access_token, res.user)
      return res
    } catch (error: any) {
      throw new Error(error.message || '注册失败')
    }
  }

  // 发送短信验证码
  async function sendSmsCode(phone: string) {
    try {
      await authApi.sendSmsCode(phone)
      return true
    } catch (error: any) {
      throw new Error(error.message || '发送失败')
    }
  }

  // 重置密码
  async function resetPassword(phone: string, code: string, newPassword: string) {
    try {
      await authApi.resetPassword(phone, code, newPassword)
      return true
    } catch (error: any) {
      throw new Error(error.message || '重置失败')
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    if (!token.value) return null
    try {
      const res = await authApi.getUserInfo()
      user.value = res
      uni.setStorageSync('user', JSON.stringify(res))
      return res
    } catch (error: any) {
      console.error('获取用户信息失败:', error)
      return null
    }
  }

  // 更新用户信息
  async function updateUserInfo(data: { nickname?: string; avatar?: string }) {
    try {
      const res = await authApi.updateUserInfo(data)
      user.value = res
      uni.setStorageSync('user', JSON.stringify(res))
      return res
    } catch (error: any) {
      throw new Error(error.message || '更新失败')
    }
  }

  // 登出
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

  // 设置当前学员
  function setCurrentStudent(student: Student) {
    currentStudent.value = student
    uni.setStorageSync('currentStudent', JSON.stringify(student))
  }

  // 检查登录状态
  function checkLogin(): boolean {
    if (!token.value) {
      uni.navigateTo({ url: '/pages/user/login' })
      return false
    }
    return true
  }

  return {
    // 状态
    token,
    user,
    currentStudent,
    students,
    // 计算属性
    isLoggedIn,
    isParent,
    isStudent,
    isCoach,
    hasPhone,
    hasWechat,
    // 方法
    initFromStorage,
    login,
    emailLogin,
    loginWithSms,
    wechatLogin,
    wechatPhoneLogin,
    register,
    sendSmsCode,
    resetPassword,
    fetchUserInfo,
    updateUserInfo,
    logout,
    setCurrentStudent,
    checkLogin
  }
})
