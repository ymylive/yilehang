/**
 * 易乐航 UI 工具函数
 */

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay = 300
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null
  return function (this: any, ...args: Parameters<T>) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay = 300
): (...args: Parameters<T>) => void {
  let lastTime = 0
  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

/**
 * 统一 Toast 提示
 */
export const toast = {
  success: (title: string, duration = 1500) => {
    uni.showToast({ title, icon: 'success', duration })
  },
  error: (title: string, duration = 2000) => {
    uni.showToast({ title, icon: 'none', duration })
  },
  info: (title: string, duration = 1500) => {
    uni.showToast({ title, icon: 'none', duration })
  },
  loading: (title = '加载中...') => {
    uni.showLoading({ title, mask: true })
  },
  hide: () => {
    uni.hideLoading()
    uni.hideToast()
  }
}

/**
 * 确认对话框
 */
export function confirm(
  content: string,
  title = '提示',
  options?: {
    confirmText?: string
    cancelText?: string
    confirmColor?: string
  }
): Promise<boolean> {
  return new Promise((resolve) => {
    uni.showModal({
      title,
      content,
      confirmText: options?.confirmText || '确定',
      cancelText: options?.cancelText || '取消',
      confirmColor: options?.confirmColor || '#FF8800',
      success: (res) => resolve(res.confirm)
    })
  })
}

/**
 * 操作菜单
 */
export function actionSheet(
  items: string[],
  options?: {
    title?: string
    itemColor?: string
  }
): Promise<number> {
  return new Promise((resolve, reject) => {
    uni.showActionSheet({
      title: options?.title,
      itemList: items,
      itemColor: options?.itemColor || '#2D2D2D',
      success: (res) => resolve(res.tapIndex),
      fail: () => reject(new Error('用户取消'))
    })
  })
}

/**
 * 延迟执行
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * 复制到剪贴板
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  return new Promise((resolve) => {
    uni.setClipboardData({
      data: text,
      success: () => {
        toast.success('已复制')
        resolve(true)
      },
      fail: () => {
        toast.error('复制失败')
        resolve(false)
      }
    })
  })
}

/**
 * 拨打电话
 */
export function makePhoneCall(phoneNumber: string): void {
  uni.makePhoneCall({
    phoneNumber,
    fail: () => {
      toast.error('拨打失败')
    }
  })
}

/**
 * 预览图片
 */
export function previewImage(
  urls: string[],
  current?: string | number
): void {
  const currentUrl = typeof current === 'number' ? urls[current] : current || urls[0]
  uni.previewImage({
    urls,
    current: currentUrl
  })
}

/**
 * 页面导航
 */
export const nav = {
  to: (url: string) => {
    uni.navigateTo({ url })
  },
  redirect: (url: string) => {
    uni.redirectTo({ url })
  },
  back: (delta = 1) => {
    uni.navigateBack({ delta })
  },
  switchTab: (url: string) => {
    uni.switchTab({ url })
  },
  reLaunch: (url: string) => {
    uni.reLaunch({ url })
  }
}

/**
 * 格式化日期
 */
export function formatDate(
  date: Date | string | number,
  format = 'YYYY-MM-DD'
): string {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 相对时间
 */
export function timeAgo(date: Date | string | number): string {
  const now = Date.now()
  const time = new Date(date).getTime()
  const diff = now - time

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  const month = 30 * day

  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  } else if (diff < week) {
    return `${Math.floor(diff / day)}天前`
  } else if (diff < month) {
    return `${Math.floor(diff / week)}周前`
  } else {
    return formatDate(date, 'MM-DD')
  }
}

/**
 * 价格格式化
 */
export function formatPrice(price: number, prefix = '¥'): string {
  return `${prefix}${price.toFixed(2)}`
}

/**
 * 手机号脱敏
 */
export function maskPhone(phone: string): string {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 生成唯一 ID
 */
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

/**
 * 检查是否为空
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 安全获取嵌套属性
 */
export function get<T>(
  obj: any,
  path: string,
  defaultValue?: T
): T | undefined {
  const keys = path.split('.')
  let result = obj
  for (const key of keys) {
    if (result === null || result === undefined) {
      return defaultValue
    }
    result = result[key]
  }
  return result ?? defaultValue
}
