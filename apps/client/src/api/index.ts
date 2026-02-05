/**
 * API请求封装
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

interface ApiResponse<T = any> {
  data: T
  statusCode: number
  errMsg: string
}

// 获取存储的token
function getToken(): string {
  return uni.getStorageSync('token') || ''
}

// 请求封装
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
          // Token过期，跳转登录
          uni.removeStorageSync('token')
          uni.navigateTo({ url: '/pages/user/login' })
          reject(new Error('登录已过期'))
        } else {
          reject(new Error(res.data?.detail || '请求失败'))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '网络错误'))
      }
    })
  })
}

// 便捷方法
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

// 认证API
export const authApi = {
  // 手机号密码登录
  login: (phone: string, password: string) =>
    api.post('/auth/login', { phone, password }),

  // 邮箱验证码登录
  emailLogin: (email: string, code: string) =>
    api.post('/auth/login/email', { phone: email, code }),

  // 短信验证码登录
  loginWithSms: (phone: string, code: string) =>
    api.post('/auth/login/sms', { phone, code }),

  // 发送短信验证码
  sendSmsCode: (phone: string) =>
    api.post('/auth/login/sms/send', { phone }),

  // 微信登录
  wechatLogin: (code: string, userInfo?: any) =>
    api.post('/auth/login/wechat', { code, user_info: userInfo }),

  // 微信手机号登录
  wechatPhoneLogin: (code: string, phoneCode: string) =>
    api.post('/auth/login/wechat-phone', { code, phone_code: phoneCode }),

  // 注册
  register: (phone: string, password: string, role: string = 'parent', nickname?: string) =>
    api.post('/auth/register', { phone, password, role, nickname }),

  // 教练注册
  registerCoach: (data: { phone: string; password: string; name: string; specialty?: string[]; introduction?: string }) =>
    api.post('/auth/register/coach', data),

  // 重置密码
  resetPassword: (phone: string, code: string, newPassword: string) =>
    api.post('/auth/password/reset', { phone, code, new_password: newPassword }),

  // 修改密码
  changePassword: (oldPassword: string, newPassword: string) =>
    api.post('/auth/password/change', { old_password: oldPassword, new_password: newPassword }),

  // 获取当前用户信息
  getUserInfo: () =>
    api.get('/auth/me'),

  // 更新用户信息
  updateUserInfo: (data: { nickname?: string; avatar?: string }) =>
    api.put('/auth/me', data),

  // 退出登录
  logout: () =>
    api.post('/auth/logout'),

  // 添加学员
  addStudent: (data: { name: string; gender?: string; birth_date?: string; phone?: string }) =>
    api.post('/auth/students', data)
}

// 学员API
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

// 训练API
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

// 排课API
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

// 成长档案API
export const growthApi = {
  getFitnessHistory: (studentId: number, skip = 0, limit = 10) =>
    api.get(`/growth/fitness-test/${studentId}`, { skip, limit }),

  getLatestFitness: (studentId: number) =>
    api.get(`/growth/fitness-test/${studentId}/latest`)
}

// 预约API
export const bookingApi = {
  // 获取我的预约列表
  list: (params?: { status?: string; start_date?: string; end_date?: string; page?: number; page_size?: number }) =>
    api.get('/bookings', params),

  // 获取预约详情
  get: (id: number) =>
    api.get(`/bookings/${id}`),

  // 创建预约
  create: (data: {
    coach_id: number
    booking_date: string
    start_time: string
    end_time: string
    course_type?: string
    remark?: string
  }) => api.post('/bookings', data),

  // 取消预约
  cancel: (id: number, reason?: string) =>
    api.put(`/bookings/${id}/cancel`, { cancel_reason: reason }),

  // 改期预约
  reschedule: (id: number, data: { new_date: string; new_start_time: string; new_end_time: string }) =>
    api.put(`/bookings/${id}/reschedule`, data)
}

// 课时卡API
export const membershipApi = {
  // 获取我的课时卡列表
  list: () =>
    api.get('/memberships'),

  // 获取消费记录
  getTransactions: (page = 1, pageSize = 20) =>
    api.get('/memberships/transactions', { page, page_size: pageSize }),

  // 获取可购买的课时卡类型
  getCards: () =>
    api.get('/memberships/cards')
}

// 教练API
export const coachApi = {
  // 获取教练列表
  list: (params?: { specialty?: string; page?: number; page_size?: number }) =>
    api.get('/coaches', params),

  // 获取教练详情
  get: (id: number) =>
    api.get(`/coaches/${id}`),

  // 获取教练可约时段
  getAvailableSlots: (id: number, startDate?: string, endDate?: string) =>
    api.get(`/coaches/${id}/available-slots`, { start_date: startDate, end_date: endDate }),

  // 获取教练评价
  getReviews: (id: number, page = 1, pageSize = 20) =>
    api.get(`/coaches/${id}/reviews`, { page, page_size: pageSize })
}

// 评价API
export const reviewApi = {
  // 提交评价
  create: (data: {
    booking_id: number
    rating: number
    content?: string
    tags?: string[]
    is_anonymous?: boolean
  }) => api.post('/reviews', data),

  // 获取我收到的教练反馈
  getMyFeedbacks: (page = 1, pageSize = 20) =>
    api.get('/reviews/feedbacks/my', { page, page_size: pageSize })
}

