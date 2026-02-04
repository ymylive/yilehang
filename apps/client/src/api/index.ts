/**
 * API请求封装
 */
const BASE_URL = '/api/v1'

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
  login: (phone: string, password: string) =>
    api.post('/auth/login', { phone, password }),

  register: (phone: string, password: string, role: string = 'parent') =>
    api.post('/auth/register', { phone, password, role }),

  wechatLogin: (code: string) =>
    api.post('/auth/wechat-login', { code })
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
