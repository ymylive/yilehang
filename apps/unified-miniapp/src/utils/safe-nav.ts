import { trackEvent } from '@/utils/telemetry'

type NavigateMode = 'navigateTo' | 'reLaunch' | 'switchTab'

const REGISTERED_PAGE_PATHS = new Set<string>([
  'pages/admin/analytics/index',
  'pages/admin/coaches/index',
  'pages/admin/dashboard/index',
  'pages/admin/notices/index',
  'pages/admin/users/detail',
  'pages/admin/users/index',
  'pages/booking/coach-detail',
  'pages/booking/confirm',
  'pages/booking/index',
  'pages/booking/select-time',
  'pages/brand/intro',
  'pages/chat/conversation',
  'pages/chat/index',
  'pages/coach/income/index',
  'pages/coach/reviews/index',
  'pages/coach/schedule/detail',
  'pages/coach/schedule/index',
  'pages/coach/slots/manage',
  'pages/coach/students/detail',
  'pages/coach/students/feedback',
  'pages/coach/students/index',
  'pages/coach/workbench/index',
  'pages/energy/index',
  'pages/energy/orders',
  'pages/energy/redeem',
  'pages/growth/detail',
  'pages/growth/history',
  'pages/growth/index',
  'pages/index/index',
  'pages/leaderboard/index',
  'pages/membership/index',
  'pages/membership/transactions',
  'pages/moments/index',
  'pages/review/create',
  'pages/schedule/detail',
  'pages/schedule/index',
  'pages/training/index',
  'pages/training/session',
  'pages/user/create-student-account',
  'pages/user/index',
  'pages/user/login',
  'pages/user/messages',
  'pages/user/profile',
  'pages/user/register'
])

function normalizePagePath(url: string): string {
  const pathOnly = (url || '').split('?')[0].split('#')[0]
  return pathOnly.startsWith('/') ? pathOnly.slice(1) : pathOnly
}

function getNavigator(mode: NavigateMode) {
  if (mode === 'reLaunch') return uni.reLaunch
  if (mode === 'switchTab') return uni.switchTab
  return uni.navigateTo
}

export function hasRegisteredPage(url: string): boolean {
  return REGISTERED_PAGE_PATHS.has(normalizePagePath(url))
}

export function safeNavigate(
  url: string,
  mode: NavigateMode = 'navigateTo',
  tip = '页面暂不可用'
): boolean {
  trackEvent('nav.attempt', { url, mode })

  if (!hasRegisteredPage(url)) {
    trackEvent('nav.blocked', { url, mode, reason: 'unregistered-page' }, 'warn')
    uni.showToast({ title: tip, icon: 'none' })
    return false
  }

  const route = normalizePagePath(url)
  getNavigator(mode)({
    url,
    success: () => {
      trackEvent('nav.success', { url: route, mode })
    },
    fail: (err: any) => {
      trackEvent(
        'nav.fail',
        { url: route, mode, message: err?.errMsg || 'navigate failed' },
        'error'
      )
      uni.showToast({ title: '跳转失败', icon: 'none' })
    }
  })

  return true
}
