/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

interface User {
  id: number
  phone: string
  nickname: string
  avatar: string
  role: string
  status: string
}

interface Student {
  id: number
  student_no: string
  name: string
  gender: string
  remaining_lessons: number
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref('')
  const user = ref<User | null>(null)
  const currentStudent = ref<Student | null>(null)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isParent = computed(() => user.value?.role === 'parent')
  const isCoach = computed(() => user.value?.role === 'coach')

  // 从存储初始化
  function initFromStorage() {
    const storedToken = uni.getStorageSync('token')
    const storedUser = uni.getStorageSync('user')
    const storedStudent = uni.getStorageSync('currentStudent')

    if (storedToken) {
      token.value = storedToken
    }
    if (storedUser) {
      user.value = JSON.parse(storedUser)
    }
    if (storedStudent) {
      currentStudent.value = JSON.parse(storedStudent)
    }
  }

  // 登录
  async function login(phone: string, password: string) {
    try {
      const res = await authApi.login(phone, password)
      token.value = res.access_token
      user.value = res.user

      // 存储到本地
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('user', JSON.stringify(res.user))

      return res
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    }
  }

  // 注册
  async function register(phone: string, password: string) {
    try {
      const res = await authApi.register(phone, password)
      token.value = res.access_token
      user.value = res.user

      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('user', JSON.stringify(res.user))

      return res
    } catch (error: any) {
      throw new Error(error.message || '注册失败')
    }
  }

  // 登出
  function logout() {
    token.value = ''
    user.value = null
    currentStudent.value = null

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

  return {
    token,
    user,
    currentStudent,
    isLoggedIn,
    isParent,
    isCoach,
    initFromStorage,
    login,
    register,
    logout,
    setCurrentStudent
  }
})
