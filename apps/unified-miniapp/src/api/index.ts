/**
 * API request wrapper
 */
import { trackError, trackEvent } from '@/utils/telemetry'

const DEFAULT_REMOTE_API_BASE_URL = 'https://rl.cornna.xyz/api/v1'
const DEFAULT_H5_API_BASE_PATH = '/api/v1'

interface RuntimeEnv {
  VITE_API_BASE_URL?: string
  VITE_WS_URL?: string
}

function normalizeBaseUrl(url: string): string {
  return url.replace(/\/+$/, '')
}

function resolveApiBaseUrl(): string {
  const env = import.meta.env as RuntimeEnv
  const configuredBaseUrl = env.VITE_API_BASE_URL?.trim()
  if (configuredBaseUrl) {
    return normalizeBaseUrl(configuredBaseUrl)
  }

  // H5 默认走同源代理，其他端保留远程兜底，避免出现空地址请求。
  if (typeof window !== 'undefined') {
    return DEFAULT_H5_API_BASE_PATH
  }

  return DEFAULT_REMOTE_API_BASE_URL
}

function resolveWsUrl(apiBaseUrl: string): string {
  const env = import.meta.env as RuntimeEnv
  const configuredWsUrl = env.VITE_WS_URL?.trim()
  if (configuredWsUrl) {
    return normalizeBaseUrl(configuredWsUrl)
  }

  if (/^https?:\/\//i.test(apiBaseUrl)) {
    return `${apiBaseUrl.replace(/^http/i, 'ws')}/chat/ws`
  }

  if (typeof window !== 'undefined') {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${wsProtocol}//${window.location.host}${apiBaseUrl}/chat/ws`
  }

  return `${DEFAULT_REMOTE_API_BASE_URL.replace(/^http/i, 'ws')}/chat/ws`
}

const BASE_URL = resolveApiBaseUrl()
export const CHAT_WS_URL = resolveWsUrl(BASE_URL)

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  params?: any
  header?: Record<string, string>
}

function shouldHandleUnauthorized(url: string): boolean {
  const publicAuthPaths = [
    '/auth/login',
    '/auth/login/email',
    '/auth/login/email/send',
    '/auth/login/wechat',
    '/auth/login/wechat-phone',
    '/auth/register',
    '/auth/register/email',
    '/auth/register/coach',
    '/auth/password/reset',
    '/auth/dev/email-code'
  ]
  return !publicAuthPaths.some(path => url.startsWith(path))
}

// get stored token
function getToken(): string {
  return uni.getStorageSync('token') || ''
}

export async function request<T = any>(
  url: string,
  options: RequestOptions = {}
): Promise<T> {
  const startedAt = Date.now()
  const { method = 'GET', data, params, header = {} } = options
  const payload = method === 'GET' ? (params ?? data) : data
  const requestHeaders: Record<string, string> = { ...header }

  const token = getToken()
  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method,
      data: payload,
      header: {
        'Content-Type': 'application/json',
        ...requestHeaders
      },
      success: (res: any) => {
        const latencyMs = Date.now() - startedAt

        if (res.statusCode >= 200 && res.statusCode < 300) {
          if (url.startsWith('/auth/login')) {
            trackEvent('auth.login.success', {
              url,
              method,
              statusCode: res.statusCode,
              latencyMs
            })
          } else if (latencyMs >= 1500) {
            trackEvent('api.slow', {
              url,
              method,
              statusCode: res.statusCode,
              latencyMs
            }, 'warn')
          }
          resolve(res.data as T)
          return
        }

        if (res.statusCode === 401) {
          const detail = res.data?.detail || 'Unauthorized'
          if (token && shouldHandleUnauthorized(url)) {
            uni.removeStorageSync('token')
            uni.removeStorageSync('user')
            uni.reLaunch({ url: '/pages/user/login' })
            trackEvent('auth.session.expired', {
              url,
              method,
              statusCode: 401,
              latencyMs
            }, 'warn')
            reject(new Error('Session expired'))
            return
          }

          const message = typeof detail === 'string' ? detail : (detail?.message || 'Unauthorized')
          const err: any = new Error(message)
          err.statusCode = res.statusCode
          err.detail = detail
          trackError('api.request.fail', err, {
            url,
            method,
            statusCode: res.statusCode,
            latencyMs
          })
          reject(err)
          return
        }

        const detail = res.data?.detail || 'Request failed'
        const message = typeof detail === 'string' ? detail : (detail?.message || 'Request failed')
        const err: any = new Error(message)
        err.statusCode = res.statusCode
        err.detail = detail
        trackError('api.request.fail', err, {
          url,
          method,
          statusCode: res.statusCode,
          latencyMs
        })
        reject(err)
      },
      fail: (err: any) => {
        const wrapped = new Error(err?.errMsg || 'Network error')
        trackError('api.network.fail', wrapped, {
          url,
          method,
          latencyMs: Date.now() - startedAt
        })
        reject(wrapped)
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
  // account + password login (phone/email)
  login: (account: string, password: string) =>
    api.post('/auth/login', { account, password }),

  // email code login
  loginWithEmail: (email: string, code: string) =>
    api.post('/auth/login/email', { email, code }),

  // send email verification code
  sendEmailCode: (email: string) =>
    api.post('/auth/login/email/send', { email }),

  // WeChat login (official mini program flow: client code -> backend code2session)
  wechatLogin: (code: string, deviceId?: string) =>
    api.post('/auth/login/wechat', { code, device_id: deviceId }),

  // WeChat phone login
  wechatPhoneLogin: (code: string, phoneCode: string, deviceId?: string) =>
    api.post('/auth/login/wechat-phone', { code, phone_code: phoneCode, device_id: deviceId }),

  // registration (email + password, no code)
  register: (email: string, password: string, role: string = 'parent', nickname?: string, phone?: string) =>
    api.post('/auth/register', { email, password, role, nickname, phone }),

  // email code registration
  registerWithEmail: (email: string, code: string, password: string, role: string = 'parent', nickname?: string, phone?: string) =>
    api.post('/auth/register/email', { email, code, password, role, nickname, phone }),

  // register with selected role (supports WeChat openid)
  registerWithRole: (payload: { email?: string; wechat_openid?: string; role: string; nickname?: string }) =>
    api.post('/auth/register/with-role', payload),

  // coach registration
  registerCoach: (data: { email: string; password: string; name: string; phone?: string; specialty?: string[]; introduction?: string }) =>
    api.post('/auth/register/coach', data),

  // reset password (via email code)
  resetPassword: (email: string, code: string, newPassword: string) =>
    api.post('/auth/password/reset', { email, code, new_password: newPassword }),

  // change password
  changePassword: (oldPassword: string, newPassword: string) =>
    api.post('/auth/password/change', { old_password: oldPassword, new_password: newPassword }),

  // get current user
  getUserInfo: () =>
    api.get('/auth/me'),

  // update user
  updateUserInfo: (data: { nickname?: string; avatar?: string; phone?: string }) =>
    api.put('/auth/me', data),

  // logout
  logout: () =>
    api.post('/auth/logout'),

  // add student
  addStudent: (data: { name: string; gender?: string; birth_date?: string; phone?: string }) =>
    api.post('/auth/students', data),

  // create student account (parent creates account for student)
  createStudentAccount: (studentId: number, data: { email: string; password: string }) =>
    api.post(`/auth/students/${studentId}/create-account`, data),

  // [DEV] get email verification code for testing
  devGetEmailCode: (email: string) =>
    api.get(`/auth/dev/email-code/${email}`)
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

// Admin Panel API
export const adminPanelApi = {
  listCoaches: (params?: { keyword?: string; page?: number; page_size?: number }) =>
    api.get('/admin-panel/coaches', params),

  updateCoach: (
    id: number,
    data: {
      name?: string
      avatar?: string
      specialty?: string[]
      introduction?: string
      hourly_rate?: number
      years_of_experience?: number
      status?: 'active' | 'inactive' | 'banned'
    }
  ) => api.put(`/admin-panel/coaches/${id}`, data),

  seedMockCoaches: (count = 8) =>
    api.post('/admin-panel/coaches/mock-seed', { count }),

  publishNotice: (data: { kind: 'announcement' | 'activity'; title: string; content: string }) =>
    api.post('/admin-panel/notices', data),

  listNotices: (limit = 30) =>
    api.get('/admin-panel/notices', { limit })
}

// Admin dashboard API
export const dashboardApi = {
  getOverview: () =>
    api.get('/dashboard/overview')
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

// Notification API
export const notificationApi = {
  list: (params?: { skip?: number; limit?: number; type?: string; is_read?: boolean }) =>
    api.get('/notifications', params),

  markRead: (id: number) =>
    api.put(`/notifications/${id}/read`),

  markAllRead: (notificationIds?: number[]) =>
    api.put('/notifications/read-all', notificationIds ? { notification_ids: notificationIds } : {}),

  delete: (id: number) =>
    api.delete(`/notifications/${id}`)
}

// Upload API
export const uploadApi = {
  avatar: (filePath: string) => {
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync('token') || ''
      uni.uploadFile({
        url: BASE_URL + '/upload/avatar',
        filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(res.data))
          } else {
            reject(new Error('上传失败'))
          }
        },
        fail: (err: any) => {
          reject(new Error(err?.errMsg || '上传失败'))
        }
      })
    })
  },

  syncWechatAvatar: () =>
    api.post('/upload/avatar/sync-wechat'),

  image: (filePath: string) => {
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync('token') || ''
      uni.uploadFile({
        url: BASE_URL + '/upload/image',
        filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(res.data))
          } else {
            reject(new Error('上传失败'))
          }
        },
        fail: (err: any) => {
          reject(new Error(err?.errMsg || '上传失败'))
        }
      })
    })
  }
}

// Chat API
export const chatApi = {
  getWsTicket: () =>
    api.post<{ ticket: string; expires_in: number }>('/chat/ws-ticket'),

  getConversations: (params?: { skip?: number; limit?: number }) =>
    api.get('/chat/conversations', params),

  createConversation: (data: { participant_id: number; student_id?: number; type?: string }) =>
    api.post('/chat/conversations', data),

  getMessages: (conversationId: number, params?: { skip?: number; limit?: number }) =>
    api.get(`/chat/conversations/${conversationId}/messages`, params),

  sendMessage: (conversationId: number, data: { type?: string; content: string; reply_to_id?: number }) =>
    api.post(`/chat/conversations/${conversationId}/messages`, data),

  markMessageRead: (messageId: number) =>
    api.put(`/chat/messages/${messageId}/read`)
}

// ============ 教练端 API ============

// Coach Profile API (教练自己的信息)
export const coachProfileApi = {
  getProfile: () => api.get('/coaches/me/profile'),
  updateProfile: (data: any) => api.put('/coaches/me/profile', data),
  getIncomeSummary: () => api.get('/coaches/me/income/summary'),
  getIncomeDetails: (params?: { month?: string; page?: number; page_size?: number }) =>
    api.get('/coaches/me/income/details', params)
}

// Coach Slots API (教练可约时段)
export const coachSlotsApi = {
  getSlots: () => api.get('/coaches/me/slots'),
  createSlot: (data: {
    day_of_week: number
    start_time: string
    end_time: string
    slot_duration?: number
    max_students?: number
  }) => api.post('/coaches/me/slots', data),
  updateSlot: (id: number, data: {
    start_time?: string
    end_time?: string
    slot_duration?: number
    max_students?: number
    is_active?: boolean
  }) => api.put(`/coaches/me/slots/${id}`, data),
  deleteSlot: (id: number) => api.delete(`/coaches/me/slots/${id}`)
}

// Coach Students API (教练的学员)
export const coachStudentsApi = {
  getStudents: (params?: { page?: number; page_size?: number }) =>
    api.get('/coaches/me/students', params),
  getStudent: (id: number) => api.get(`/coaches/me/students/${id}`)
}

// Coach Schedule API (教练的课表)
export const coachScheduleApi = {
  getSchedule: (params?: {
    start_date?: string
    end_date?: string
    status?: string
    page?: number
    page_size?: number
  }) => api.get('/coaches/me/schedule', params),

  getBookingDetail: async (id: number) => {
    try {
      return await api.get(`/coaches/me/bookings/${id}`)
    } catch (error) {
      // 回退：从课表中查找
      const today = new Date()
      const start = new Date(today)
      const end = new Date(today)
      start.setDate(start.getDate() - 30)
      end.setDate(end.getDate() + 30)

      const data: any = await api.get('/coaches/me/schedule', {
        start_date: start.toISOString().slice(0, 10),
        end_date: end.toISOString().slice(0, 10),
        page: 1,
        page_size: 300
      })

      const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
      const found = list.find((item: any) => Number(item?.id) === id)
      if (found) return found
      throw error
    }
  },

  confirmBooking: (id: number) => api.put(`/coaches/me/bookings/${id}/confirm`),
  completeBooking: (id: number, notes?: string) =>
    api.put(`/coaches/me/bookings/${id}/complete`, notes ? { notes } : undefined),
  markNoShow: (id: number) => api.put(`/coaches/me/bookings/${id}/no-show`)
}

// Coach Review API (教练收到的评价)
export const coachReviewApi = {
  getMyReviews: async (params?: { page?: number; page_size?: number }) => {
    try {
      return await api.get('/reviews/coach/my', params)
    } catch (error) {
      const profile: any = await coachProfileApi.getProfile()
      if (!profile?.id) throw error
      return api.get(`/coaches/${profile.id}/reviews`, params)
    }
  },
  replyReview: (id: number, reply: string) =>
    api.post(`/coaches/me/reviews/${id}/reply`, { reply })
}

// Coach Feedback API (教练给学员的反馈)
export const coachFeedbackApi = {
  createFeedback: (data: {
    booking_id?: number
    student_id: number
    performance_rating: number | null
    content: string
    suggestions?: string | null
  }) => api.post('/reviews/feedbacks', data),

  getFeedbacks: (params?: { page?: number; page_size?: number; student_id?: number }) =>
    api.get('/reviews/feedbacks', params)
}

// ============ 能量系统 API ============

export const energyApi = {
  // 获取能量账户
  getAccount: () => api.get('/energy/account'),

  // 获取能量账户摘要
  getSummary: () => api.get('/energy/account/summary'),

  // 获取能量交易记录
  getTransactions: (params?: { page?: number; page_size?: number; type?: string }) =>
    api.get('/energy/transactions', params),

  // 获取积分规则
  getRules: () => api.get('/energy/rules'),

  // 获取能量等级配置
  getLevels: () => api.get('/energy/levels')
}

// ============ 商家系统 API ============

export const merchantApi = {
  // 商家登录
  login: (account: string, password: string) =>
    api.post('/merchants/auth/login', { account, password }),

  // 获取我的商家信息
  getMyMerchant: () => api.get('/merchants/me'),

  // 更新商家信息
  updateMyMerchant: (data: any) => api.put('/merchants/me', data),

  // 获取商家列表（学生端）
  getMerchants: (params?: { category?: string; featured?: boolean }) =>
    api.get('/merchants', params),

  // 获取商家详情
  getMerchantDetail: (merchantId: number) =>
    api.get(`/merchants/${merchantId}`),

  // 获取商家商品列表
  getMerchantItems: (merchantId: number) =>
    api.get(`/merchants/${merchantId}/items`),

  // 获取所有兑换商品
  getAllItems: (params?: { category?: string; min_cost?: number; max_cost?: number }) =>
    api.get('/merchants/items/all', params),

  // 兑换商品
  redeemItem: (data: { item_id: number }) =>
    api.post('/merchants/redeem', data),

  // 获取我的兑换订单
  getMyOrders: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get('/merchants/redeem/orders', params),

  // 核销订单（商家端）
  verifyOrder: (orderId: number, verifyCode: string) =>
    api.post(`/merchants/redeem/${orderId}/verify`, { verify_code: verifyCode }),

  // 通过核销码核销订单（商家端）
  verifyByCode: (verifyCode: string) =>
    api.post('/merchants/redeem/verify-by-code', { verify_code: verifyCode }),

  // 通过核销码查询订单（商家端）
  getOrderByCode: (verifyCode: string) =>
    api.get(`/merchants/redeem/code/${verifyCode}`),

  // 获取订单详情（商家端）
  getOrderDetail: (orderId: number) =>
    api.get(`/merchants/redeem/${orderId}`),

  // 获取商家统计数据（商家端）
  getStats: () => api.get('/merchants/merchant/stats'),

  // 获取商家订单列表（商家端）
  getOrders: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get('/merchants/merchant/orders', params)
}

// ============ 排行榜 API ============

export const leaderboardApi = {
  // 获取能量排行榜
  getEnergyLeaderboard: (params?: { period?: string; limit?: number }) =>
    api.get('/leaderboard/energy', params),

  // 获取训练排行榜
  getTrainingLeaderboard: (params?: { period?: string; limit?: number }) =>
    api.get('/leaderboard/training', params),

  // 获取体测排行榜
  getFitnessLeaderboard: (params?: { metric?: string; limit?: number }) =>
    api.get('/leaderboard/fitness', params)
}

// ============ 角色权限 API ============

export const roleApi = {
  // 获取当前用户所有角色
  getRoles: () => api.get('/user/roles'),

  // 获取当前用户权限列表
  getPermissions: () => api.get('/user/permissions'),

  // 获取当前用户可见菜单
  getMenus: () => api.get('/user/menus'),

  // 切换当前激活角色
  switchRole: (roleCode: string) =>
    api.post('/user/switch-role', { role_code: roleCode })
}
