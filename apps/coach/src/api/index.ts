const envBase = (import.meta.env.VITE_API_BASE_URL || '').trim()
const isMpWeixin = typeof wx !== 'undefined' && typeof (globalThis as any).__wxConfig !== 'undefined'
const BASE_URL = envBase || (isMpWeixin ? 'https://yilehang.cornna.xyz/api/v1' : '/api/v1')

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  params?: Record<string, any>
}

function shouldHandleUnauthorized(url: string): boolean {
  const publicAuthPaths = ['/auth/login']
  return !publicAuthPaths.includes(url)
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
          return
        }

        if (res.statusCode === 401) {
          const detail = (res.data as any)?.detail || '\u672a\u6388\u6743'
          if (token && shouldHandleUnauthorized(url)) {
            uni.removeStorageSync('token')
            uni.reLaunch({ url: '/pages/user/login' })
            reject(new Error('\u767b\u5f55\u5df2\u8fc7\u671f'))
            return
          }
          reject(new Error(typeof detail === 'string' ? detail : '\u8bf7\u6c42\u5931\u8d25'))
          return
        }

        const detail = (res.data as any)?.detail
        reject(new Error(typeof detail === 'string' && detail.trim() ? detail : '\u8bf7\u6c42\u5931\u8d25'))
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '\u7f51\u7edc\u9519\u8bef'))
      }
    })
  })
}

export const coachApi = {
  getProfile: () => request('/coaches/me/profile'),
  updateProfile: (data: any) => request('/coaches/me/profile', { method: 'PUT', data }),
  getIncomeSummary: () => request('/coaches/me/income/summary'),
  getIncomeDetails: (params?: { month?: string; page?: number; page_size?: number }) =>
    request('/coaches/me/income/details', { params })
}

export const slotsApi = {
  getSlots: () => request('/coaches/me/slots'),
  createSlot: (data: {
    day_of_week: number
    start_time: string
    end_time: string
    slot_duration?: number
    max_students?: number
  }) => request('/coaches/me/slots', { method: 'POST', data }),
  updateSlot: (id: number, data: any) => request(`/coaches/me/slots/${id}`, { method: 'PUT', data }),
  deleteSlot: (id: number) => request(`/coaches/me/slots/${id}`, { method: 'DELETE' })
}

export const studentsApi = {
  getStudents: (params?: { page?: number; page_size?: number }) =>
    request('/coaches/me/students', { params }),
  getStudent: (id: number) => request(`/coaches/me/students/${id}`)
}

export const scheduleApi = {
  getSchedule: (params?: {
    start_date?: string
    end_date?: string
    status?: string
    page?: number
    page_size?: number
  }) => request('/coaches/me/schedule', { params }),

  getBookingDetail: async (id: number) => {
    try {
      return await request(`/coaches/me/bookings/${id}`)
    } catch (error) {
      const today = new Date()
      const start = new Date(today)
      const end = new Date(today)
      start.setDate(start.getDate() - 30)
      end.setDate(end.getDate() + 30)

      const data: any = await request('/coaches/me/schedule', {
        params: {
          start_date: start.toISOString().slice(0, 10),
          end_date: end.toISOString().slice(0, 10),
          page: 1,
          page_size: 300
        }
      })

      const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
      const found = list.find((item: any) => Number(item?.id) === id)
      if (found) {
        return found
      }
      throw error
    }
  },

  confirmBooking: (id: number) => request(`/coaches/me/bookings/${id}/confirm`, { method: 'PUT' }),
  completeBooking: (id: number, notes?: string) =>
    request(`/coaches/me/bookings/${id}/complete`, { method: 'PUT', params: notes ? { notes } : undefined }),
  markNoShow: (id: number) => request(`/coaches/me/bookings/${id}/no-show`, { method: 'PUT' })
}

export const reviewApi = {
  getMyReviews: async (params?: { page?: number; page_size?: number }) => {
    try {
      return await request('/reviews/coach/my', { params })
    } catch (error) {
      const profile: any = await coachApi.getProfile()
      if (!profile?.id) {
        throw error
      }
      return request(`/coaches/${profile.id}/reviews`, { params })
    }
  },

  replyReview: (id: number, reply: string) =>
    request(`/coaches/me/reviews/${id}/reply`, { method: 'POST', data: { reply } })
}

export const feedbackApi = {
  createFeedback: (data: {
    booking_id?: number
    student_id: number
    performance_rating: number | null
    content: string
    suggestions?: string | null
  }) => request('/reviews/feedbacks', { method: 'POST', data }),

  getFeedbacks: (params?: { page?: number; page_size?: number; student_id?: number }) =>
    request('/reviews/feedbacks', { params })
}

export const authApi = {
  login: (data: { account: string; password: string }) => request('/auth/login', { method: 'POST', data }),
  getUserInfo: () => request('/auth/me'),
  logout: () => request('/auth/logout', { method: 'POST' })
}

export const chatApi = {
  getConversations: (params?: { skip?: number; limit?: number }) =>
    request('/chat/conversations', { params }),

  createConversation: (data: { participant_id: number; student_id?: number; type?: string }) =>
    request('/chat/conversations', { method: 'POST', data }),

  getMessages: (conversationId: number, params?: { skip?: number; limit?: number }) =>
    request(`/chat/conversations/${conversationId}/messages`, { params }),

  sendMessage: (conversationId: number, data: { type?: string; content: string; reply_to_id?: number }) =>
    request(`/chat/conversations/${conversationId}/messages`, { method: 'POST', data }),

  markMessageRead: (messageId: number) =>
    request(`/chat/messages/${messageId}/read`, { method: 'PUT' })
}

export const uploadApi = {
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
        fail: (err) => {
          reject(new Error(err.errMsg || '上传失败'))
        }
      })
    })
  }
}

export default {
  coach: coachApi,
  slots: slotsApi,
  students: studentsApi,
  schedule: scheduleApi,
  review: reviewApi,
  feedback: feedbackApi,
  auth: authApi,
  chat: chatApi,
  upload: uploadApi
}
