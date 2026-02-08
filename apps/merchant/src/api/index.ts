const envBase = (import.meta.env.VITE_API_BASE_URL || '').trim()
const isMpWeixin = typeof wx !== 'undefined' && typeof (globalThis as any).__wxConfig !== 'undefined'
const BASE_URL = envBase || (isMpWeixin ? 'https://yilehang.cornna.xyz/api/v1' : '/api/v1')

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

function shouldHandleUnauthorized(url: string): boolean {
  const publicAuthPaths = ['/merchants/auth/login']
  return !publicAuthPaths.includes(url)
}

function normalizeOrder(order: any) {
  if (!order) return order
  const statusMap: Record<string, string> = {
    verified: 'completed'
  }
  const normalizedStatus = statusMap[order.status] || order.status
  return {
    ...order,
    status: normalizedStatus,
    product_name: order.product_name || order.item_name || '',
    product_image: order.product_image || order.item_image || null,
    redemption_code: order.redemption_code || order.verify_code || '',
    expires_at: order.expires_at || order.expire_at || null,
    student_name: order.student_name || order.student || ''
  }
}

function normalizeStats(res: any) {
  if (!res) return res
  const todayVerified = Number(res.today_verified || 0)
  const todayPending = Number(res.today_pending || 0)
  const weekVerified = Number(res.week_verified || 0)
  const monthVerified = Number(res.month_verified || 0)
  const totalVerified = Number(res.total_verified || 0)
  const totalEnergy = Number(res.total_energy_consumed || 0)

  return {
    ...res,
    pending_count: todayPending,
    completed_count: todayVerified,
    energy_consumed: totalEnergy,
    total_orders: totalVerified,
    total_energy: totalEnergy,
    unique_students: Number(res.unique_students || 0),
    week_total_orders: weekVerified,
    month_total_orders: monthVerified,
    cancelled_count: Number(res.cancelled_count || 0),
    expired_count: Number(res.expired_count || 0)
  }
}

function getToken(): string {
  return uni.getStorageSync('merchant_token') || ''
}

export async function request<T = any>(url: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', data, header = {} } = options

  const token = getToken()
  if (token) {
    header.Authorization = `Bearer ${token}`
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
          return
        }

        if (res.statusCode === 401) {
          const detail = res.data?.detail || 'Unauthorized'
          if (token && shouldHandleUnauthorized(url)) {
            uni.removeStorageSync('merchant_token')
            uni.removeStorageSync('merchant_info')
            uni.reLaunch({ url: '/pages/user/login' })
            reject(new Error('Session expired'))
            return
          }
          reject(new Error(detail))
          return
        }

        reject(new Error(res.data?.detail || 'Request failed'))
      },
      fail: (err) => {
        reject(new Error(err.errMsg || 'Network error'))
      }
    })
  })
}

export const api = {
  get: <T = any>(url: string, params?: any) => request<T>(url, { method: 'GET', data: params }),
  post: <T = any>(url: string, data?: any) => request<T>(url, { method: 'POST', data }),
  put: <T = any>(url: string, data?: any) => request<T>(url, { method: 'PUT', data }),
  delete: <T = any>(url: string) => request<T>(url, { method: 'DELETE' })
}

export const merchantAuthApi = {
  login: (account: string, password: string) => api.post('/merchants/auth/login', { account, password }),
  getProfile: () => api.get('/merchants/me'),
  updateProfile: (data: any) => api.put('/merchants/me', data),
  logout: () => {
    uni.removeStorageSync('merchant_token')
    uni.removeStorageSync('merchant_info')
  }
}

export const redemptionApi = {
  getPendingOrders: async (params?: { page?: number; page_size?: number }) => {
    const res: any = await api.get('/merchants/merchant/orders', { ...params, status: 'pending' })
    return { ...res, items: (res?.items || []).map(normalizeOrder) }
  },
  getCompletedOrders: async (params?: { page?: number; page_size?: number }) => {
    const res: any = await api.get('/merchants/merchant/orders', { ...params, status: 'verified' })
    return { ...res, items: (res?.items || []).map(normalizeOrder) }
  },
  getOrders: async (params?: { page?: number; page_size?: number; status?: string }) => {
    const rawStatus = params?.status
    const status = rawStatus === 'completed' ? 'verified' : rawStatus
    const res: any = await api.get('/merchants/merchant/orders', { ...params, status })
    return { ...res, items: (res?.items || []).map(normalizeOrder) }
  },
  getByCode: async (code: string) => normalizeOrder(await api.get(`/merchants/redeem/code/${code}`)),
  verify: async (redemptionId: number, verifyCode?: string) => {
    const payload = { verify_code: verifyCode || '' }
    const res: any = await api.post(`/merchants/redeem/${redemptionId}/verify`, payload)
    if (!res?.success) {
      throw new Error(res?.message || '核销失败')
    }
    return res
  },
  verifyByCode: (code: string) => api.post('/merchants/redeem/verify-by-code', { verify_code: code }),
  getDetail: async (id: number) => normalizeOrder(await api.get(`/merchants/redeem/${id}`))
}

export const statsApi = {
  getToday: async () => normalizeStats(await api.get('/merchants/merchant/stats')),
  getWeek: async () => {
    const s: any = normalizeStats(await api.get('/merchants/merchant/stats'))
    return {
      ...s,
      total_orders: s.week_total_orders || s.total_orders,
      completed_count: s.week_total_orders || s.completed_count
    }
  },
  getMonth: async () => {
    const s: any = normalizeStats(await api.get('/merchants/merchant/stats'))
    return {
      ...s,
      total_orders: s.month_total_orders || s.total_orders,
      completed_count: s.month_total_orders || s.completed_count
    }
  },
  getSummary: async () => normalizeStats(await api.get('/merchants/merchant/stats')),
  getRange: async (_startDate: string, _endDate: string) => normalizeStats(await api.get('/merchants/merchant/stats'))
}

export const productApi = {
  getProducts: (params?: { page?: number; page_size?: number; status?: string }) =>
    api.get('/merchants/me/products', params),
  getProduct: (id: number) => api.get(`/merchants/products/${id}`),
  updateStock: (id: number, stock: number) => api.put(`/merchants/products/${id}/stock`, { stock })
}
