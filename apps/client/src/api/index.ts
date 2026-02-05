/**
 * API request wrapper
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

// get stored token
function getToken(): string {
  return uni.getStorageSync('token') || ''
}

export async function request<T = any>(
  url: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', data, header = {} } = options

  const token = getToken()
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header
      },
      success: (res: any) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.navigateTo({ url: '/pages/user/login' })
          reject(new Error('Session expired'))
        } else {
          reject(new Error(res.data?.detail || 'Request failed'))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || 'Network error'))
      }
    })
  })
}

export const api = {
  get: <T = any>(url: string, params?: any) =>
    request<T>(url, { method: 'GET', data: params }),

  post: <T = any>(url: string, data?: any) =>
    request<T>(url, { method: 'POST', data }),

  put: <T = any>(url: string, data?: any) =>
    request<T>(url, { method: 'PUT', data }),

  delete: <T = any>(url: string) =>
    request<T>(url, { method: 'DELETE' })
}

// Auth API
export const authApi = {
  // phone + password login
  login: (phone: string, password: string) =>
    api.post('/auth/login', { phone, password }),

  // SMS code login
  loginWithSms: (phone: string, code: string) =>
    api.post('/auth/login/sms', { phone, code }),

  // send SMS code
  sendSmsCode: (phone: string) =>
    api.post('/auth/login/sms/send', { phone }),

  // WeChat login
  wechatLogin: (code: string, userInfo?: any) =>
    api.post('/auth/login/wechat', { code, user_info: userInfo }),

  // WeChat phone login
  wechatPhoneLogin: (code: string, phoneCode: string) =>
    api.post('/auth/login/wechat-phone', { code, phone_code: phoneCode }),

  // registration
  register: (phone: string, password: string, role: string = 'parent', nickname?: string) =>
    api.post('/auth/register', { phone, password, role, nickname }),

  // SMS registration
  registerWithSms: (phone: string, code: string, password: string, role: string = 'parent', nickname?: string) =>
    api.post('/auth/register/sms', { phone, code, password, role, nickname }),

  // coach registration
  registerCoach: (data: { phone: string; password: string; name: string; specialty?: string[]; introduction?: string }) =>
    api.post('/auth/register/coach', data),

  // reset password
  resetPassword: (phone: string, code: string, newPassword: string) =>
    api.post('/auth/password/reset', { phone, code, new_password: newPassword }),

  // change password
  changePassword: (oldPassword: string, newPassword: string) =>
    api.post('/auth/password/change', { old_password: oldPassword, new_password: newPassword }),

  // get current user
  getUserInfo: () =>
    api.get('/auth/me'),

  // update user
  updateUserInfo: (data: { nickname?: string; avatar?: string }) =>
    api.put('/auth/me', data),

  // logout
  logout: () =>
    api.post('/auth/logout'),

  // add student
  addStudent: (data: { name: string; gender?: string; birth_date?: string; phone?: string }) =>
    api.post('/auth/students', data)
}

// Student API
export const studentApi = {
  list: (skip = 0, limit = 20) =>
    api.get('/students', { skip, limit }),

  get: (id: number) =>
    api.get(`/students/${id}`),

  getGrowth: (id: number) =>
    api.get(`/students/${id}/growth`),

  update: (id: number, data: any) =>
    api.put(`/students/${id}`, data)
}

// Training API
export const trainingApi = {
  getExercises: () =>
    api.get('/training/exercises'),

  start: (exerciseType: string, studentId: number) =>
    api.post('/training/start', { exercise_type: exerciseType, student_id: studentId }),

  complete: (data: any) =>
    api.post('/training/complete', data),

  getHistory: (studentId: number, skip = 0, limit = 20) =>
    api.get('/training/history', { student_id: studentId, skip, limit })
}

// Schedule API
export const scheduleApi = {
  list: (params?: any) =>
    api.get('/schedules', params),

  get: (id: number) =>
    api.get(`/schedules/${id}`),

  enroll: (scheduleId: number, studentId: number) =>
    api.post(`/schedules/${scheduleId}/enroll`, { schedule_id: scheduleId, student_id: studentId }),

  checkin: (scheduleId: number, studentId: number, method = 'qrcode') =>
    api.post(`/schedules/${scheduleId}/checkin`, {
      schedule_id: scheduleId,
      student_id: studentId,
      check_in_method: method
    })
}

// Growth API
export const growthApi = {
  getFitnessHistory: (studentId: number, skip = 0, limit = 10) =>
    api.get(`/growth/fitness-test/${studentId}`, { skip, limit }),

  getLatestFitness: (studentId: number) =>
    api.get(`/growth/fitness-test/${studentId}/latest`)
}

// Booking API
export const bookingApi = {
  list: (params?: { status?: string; start_date?: string; end_date?: string; page?: number; page_size?: number }) =>
    api.get('/bookings', params),

  get: (id: number) =>
    api.get(`/bookings/${id}`),

  create: (data: {
    coach_id: number
    booking_date: string
    start_time: string
    end_time: string
    course_type?: string
    remark?: string
  }) => api.post('/bookings', data),

  cancel: (id: number, reason?: string) =>
    api.put(`/bookings/${id}/cancel`, { cancel_reason: reason }),

  reschedule: (id: number, data: { new_date: string; new_start_time: string; new_end_time: string }) =>
    api.put(`/bookings/${id}/reschedule`, data)
}

// Membership API
export const membershipApi = {
  list: () =>
    api.get('/memberships'),

  getTransactions: (page = 1, pageSize = 20) =>
    api.get('/memberships/transactions', { page, page_size: pageSize }),

  getCards: () =>
    api.get('/memberships/cards')
}

// Coach API
export const coachApi = {
  list: (params?: { specialty?: string; page?: number; page_size?: number }) =>
    api.get('/coaches', params),

  get: (id: number) =>
    api.get(`/coaches/${id}`),

  getAvailableSlots: (id: number, startDate?: string, endDate?: string) =>
    api.get(`/coaches/${id}/available-slots`, { start_date: startDate, end_date: endDate }),

  getReviews: (id: number, page = 1, pageSize = 20) =>
    api.get(`/coaches/${id}/reviews`, { page, page_size: pageSize })
}

// Review API
export const reviewApi = {
  create: (data: {
    booking_id: number
    rating: number
    content?: string
    tags?: string[]
    is_anonymous?: boolean
  }) => api.post('/reviews', data),

  getMyFeedbacks: (page = 1, pageSize = 20) =>
    api.get('/reviews/feedbacks/my', { page, page_size: pageSize })
}

// AI API (stub)
export const aiApi = {
  analyzeJumpRope: (data: {
    student_id: number
    video_url?: string
    fps?: number
    duration_sec?: number
    meta?: Record<string, any>
  }) => api.post('/ai/jump-rope/analyze', data),

  getAdvice: (data: {
    student_id?: number
    age?: number
    height_cm?: number
    weight_kg?: number
    goal?: string
    activity_level?: string
    recent_sessions?: any[]
    diet_preference?: string
  }) => api.post('/ai/advice', data),

  chat: (data: { question: string; context?: Record<string, any> }) =>
    api.post('/ai/chat', data)
}
