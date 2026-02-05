/**
 * 管理后台 API 封装
 */
import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 创建axios实例
const instance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error('没有权限执行此操作')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else {
        ElMessage.error(data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

// 预约管理API
export const bookingApi = {
  // 获取预约列表
  list: (params?: {
    status?: string
    coach_id?: number
    student_name?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) => instance.get('/bookings', { params }),

  // 获取预约详情
  get: (id: number) => instance.get(`/bookings/${id}`),

  // 确认预约（管理员使用教练端点）
  confirm: (id: number) => instance.put(`/bookings/${id}/confirm`),

  // 取消预约
  cancel: (id: number, reason?: string) =>
    instance.put(`/bookings/${id}/cancel`, { cancel_reason: reason })
}

// 教练管理API
export const coachApi = {
  // 获取教练列表
  list: (params?: { page?: number; page_size?: number; specialty?: string }) =>
    instance.get('/coaches', { params }),

  // 获取教练详情
  get: (id: number) => instance.get(`/coaches/${id}`)
}

// 学员管理API
export const studentApi = {
  // 获取学员列表
  list: (params?: { page?: number; page_size?: number; name?: string }) =>
    instance.get('/students', { params }),

  // 获取学员详情
  get: (id: number) => instance.get(`/students/${id}`)
}

// 课时卡管理API
export const membershipApi = {
  // 获取课时卡类型列表
  getCards: (params?: { is_active?: boolean }) =>
    instance.get('/memberships/cards', { params }),

  // 创建课时卡类型
  createCard: (data: {
    name: string
    card_type: string
    total_times?: number
    duration_days?: number
    price: number
    original_price?: number
    course_type: string
    description?: string
  }) => instance.post('/memberships/cards', data),

  // 更新课时卡类型
  updateCard: (id: number, data: {
    name?: string
    card_type?: string
    total_times?: number
    duration_days?: number
    price?: number
    original_price?: number
    course_type?: string
    description?: string
    is_active?: boolean
  }) => instance.put(`/memberships/cards/${id}`, data),

  // 删除课时卡类型
  deleteCard: (id: number) => instance.delete(`/memberships/cards/${id}`),

  // 获取学员课时卡列表
  getStudentCards: (params?: {
    student_id?: number
    status?: string
    page?: number
    page_size?: number
  }) => instance.get('/memberships', { params }),

  // 手动充值/购买课时卡
  recharge: (data: {
    student_id: number
    card_id: number
    times?: number
    reason?: string
    remark?: string
  }) => instance.post('/memberships/recharge', data),

  // 获取消费记录
  getTransactions: (params?: {
    student_id?: number
    membership_id?: number
    page?: number
    page_size?: number
  }) => instance.get('/memberships/transactions', { params })
}

// 认证API
export const authApi = {
  // 登录
  login: (data: { phone: string; password: string }) =>
    instance.post('/auth/login', data),

  // 获取当前用户信息
  getUserInfo: () => instance.get('/auth/me'),

  // 登出
  logout: () => instance.post('/auth/logout')
}

// 用户管理API
export const userApi = {
  // 获取用户列表
  list: (params?: { role?: string; page?: number; page_size?: number }) =>
    instance.get('/users', { params }),

  // 获取用户详情
  get: (id: number) => instance.get(`/users/${id}`),

  // 更新用户状态
  updateStatus: (id: number, isActive: boolean) =>
    instance.put(`/users/${id}/status`, { is_active: isActive })
}

export default {
  booking: bookingApi,
  coach: coachApi,
  student: studentApi,
  membership: membershipApi,
  auth: authApi,
  user: userApi
}
