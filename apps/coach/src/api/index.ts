/**
 * 教练端 API 封装
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  params?: Record<string, any>
}

async function request<T = any>(url: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', data, params } = options

  let fullUrl = `${BASE_URL}${url}`
  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      fullUrl += `?${queryString}`
    }
  }

  const token = uni.getStorageSync('token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: fullUrl,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.reLaunch({ url: '/pages/user/login' })
          reject(new Error('登录已过期'))
        } else {
          reject(new Error((res.data as any)?.detail || '请求失败'))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '网络错误'))
      }
    })
  })
}

// 教练信息
export const coachApi = {
  // 获取当前教练信息
  getProfile: () => request('/coaches/me/profile'),

  // 更新教练信息
  updateProfile: (data: any) => request('/coaches/me/profile', { method: 'PUT', data }),

  // 获取收入统计
  getIncomeSummary: () => request('/coaches/me/income/summary'),

  // 获取收入明细
  getIncomeDetails: (params?: { month?: string; page?: number; page_size?: number }) =>
    request('/coaches/me/income/details', { params })
}

// 可约时段管理
export const slotsApi = {
  // 获取可约时段列表
  getSlots: () => request('/coaches/me/slots'),

  // 创建可约时段
  createSlot: (data: {
    day_of_week: number
    start_time: string
    end_time: string
    slot_duration?: number
    max_students?: number
  }) => request('/coaches/me/slots', { method: 'POST', data }),

  // 更新可约时段
  updateSlot: (id: number, data: any) =>
    request(`/coaches/me/slots/${id}`, { method: 'PUT', data }),

  // 删除可约时段
  deleteSlot: (id: number) =>
    request(`/coaches/me/slots/${id}`, { method: 'DELETE' })
}

// 学员管理
export const studentsApi = {
  // 获取我的学员列表
  getStudents: (params?: { page?: number; page_size?: number }) =>
    request('/coaches/me/students', { params }),

  // 获取学员详情
  getStudent: (id: number) => request(`/coaches/me/students/${id}`)
}

// 课程/预约管理
export const scheduleApi = {
  // 获取我的课表
  getSchedule: (params?: { start_date?: string; end_date?: string; status?: string }) =>
    request('/coaches/me/schedule', { params }),

  // 确认预约
  confirmBooking: (id: number) =>
    request(`/coaches/me/bookings/${id}/confirm`, { method: 'PUT' }),

  // 完成课程
  completeBooking: (id: number, notes?: string) =>
    request(`/coaches/me/bookings/${id}/complete`, { method: 'PUT', params: notes ? { notes } : undefined }),

  // 标记未到
  markNoShow: (id: number) =>
    request(`/coaches/me/bookings/${id}/no-show`, { method: 'PUT' })
}

// 评价管理
export const reviewApi = {
  // 获取我的评价列表
  getMyReviews: (params?: { page?: number; page_size?: number }) =>
    request('/reviews/coach/my', { params }),

  // 回复评价
  replyReview: (id: number, reply: string) =>
    request(`/coaches/me/reviews/${id}/reply`, { method: 'POST', data: { reply } })
}

// 反馈管理
export const feedbackApi = {
  // 提交学习反馈
  createFeedback: (data: {
    booking_id?: number
    student_id: number
    performance_rating: number
    content: string
    suggestions?: string
  }) => request('/reviews/feedbacks', { method: 'POST', data }),

  // 获取反馈列表
  getFeedbacks: (params?: { page?: number; page_size?: number; student_id?: number }) =>
    request('/reviews/feedbacks', { params })
}

// 认证
export const authApi = {
  // 登录
  login: (data: { phone: string; password: string }) =>
    request('/auth/login', { method: 'POST', data }),

  // 获取用户信息
  getUserInfo: () => request('/auth/me'),

  // 登出
  logout: () => request('/auth/logout', { method: 'POST' })
}

export default {
  coach: coachApi,
  slots: slotsApi,
  students: studentsApi,
  schedule: scheduleApi,
  review: reviewApi,
  feedback: feedbackApi,
  auth: authApi
}
