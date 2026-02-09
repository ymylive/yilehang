/**
 * 角色路由守卫
 * 根据用户角色控制页面访问权限
 */

export type UserRole = 'admin' | 'coach' | 'parent' | 'student'

// 角色页面映射配置
export const ROLE_PAGE_MAP: Record<UserRole, {
  home: string
  allowedPrefixes: string[]
  tabBar: { pagePath: string; text: string }[]
}> = {
  admin: {
    home: '/pages/admin/dashboard/index',
    allowedPrefixes: [
      'pages/admin/',
      'pages/user/',
      'pages/chat/'
    ],
    tabBar: [
      { pagePath: 'pages/admin/dashboard/index', text: '看板' },
      { pagePath: 'pages/admin/users/index', text: '用户' },
      { pagePath: 'pages/admin/analytics/index', text: '分析' },
      { pagePath: 'pages/user/index', text: '我的' }
    ]
  },
  coach: {
    home: '/pages/coach/workbench/index',
    allowedPrefixes: [
      'pages/coach/',
      'pages/user/',
      'pages/chat/'
    ],
    tabBar: [
      { pagePath: 'pages/coach/workbench/index', text: '工作台' },
      { pagePath: 'pages/coach/schedule/index', text: '课表' },
      { pagePath: 'pages/coach/students/index', text: '学员' },
      { pagePath: 'pages/user/index', text: '我的' }
    ]
  },
  parent: {
    home: '/pages/index/index',
    allowedPrefixes: [
      'pages/index/',
      'pages/booking/',
      'pages/schedule/',
      'pages/membership/',
      'pages/growth/',
      'pages/training/',
      'pages/review/',
      'pages/energy/',
      'pages/leaderboard/',
      'pages/moments/',
      'pages/user/',
      'pages/chat/'
    ],
    tabBar: [
      { pagePath: 'pages/index/index', text: '首页' },
      { pagePath: 'pages/booking/index', text: '约课' },
      { pagePath: 'pages/growth/index', text: '成长' },
      { pagePath: 'pages/schedule/index', text: '课表' },
      { pagePath: 'pages/user/index', text: '我的' }
    ]
  },
  student: {
    home: '/pages/index/index',
    allowedPrefixes: [
      'pages/index/',
      'pages/schedule/',
      'pages/training/',
      'pages/growth/',
      'pages/energy/',
      'pages/leaderboard/',
      'pages/moments/',
      'pages/user/',
      'pages/chat/'
    ],
    tabBar: [
      { pagePath: 'pages/index/index', text: '首页' },
      { pagePath: 'pages/training/index', text: '训练' },
      { pagePath: 'pages/growth/index', text: '成长' },
      { pagePath: 'pages/schedule/index', text: '课表' },
      { pagePath: 'pages/user/index', text: '我的' }
    ]
  }
}

// 公共页面（无需登录即可访问）
const PUBLIC_PAGES = [
  'pages/user/login',
  'pages/user/register'
]

/**
 * 检查角色是否有权限访问指定页面
 */
export function checkRolePermission(role: UserRole, route: string): boolean {
  // 去掉开头的 /
  const normalizedRoute = route.startsWith('/') ? route.slice(1) : route

  // 公共页面始终允许
  if (PUBLIC_PAGES.some(p => normalizedRoute.startsWith(p))) {
    return true
  }

  const config = ROLE_PAGE_MAP[role]
  if (!config) return false

  return config.allowedPrefixes.some(prefix => normalizedRoute.startsWith(prefix))
}

/**
 * 获取角色的首页路径
 */
export function getRoleHomePage(role: UserRole): string {
  return ROLE_PAGE_MAP[role]?.home || '/pages/user/login'
}

/**
 * 获取角色的 TabBar 配置
 */
export function getRoleTabBar(role: UserRole) {
  return ROLE_PAGE_MAP[role]?.tabBar || []
}

/**
 * 判断路径是否是某角色的 tabBar 页面
 */
export function isTabBarPage(role: UserRole, route: string): boolean {
  const normalizedRoute = route.startsWith('/') ? route.slice(1) : route
  const tabBar = getRoleTabBar(role)
  return tabBar.some(item => item.pagePath === normalizedRoute)
}

/**
 * 执行角色路由守卫（在 App.vue onShow 中调用）
 */
export function enforceRoleRoute(role?: string) {
  if (!role) return

  const pages = getCurrentPages()
  const current = pages[pages.length - 1] as any
  const route: string = current?.route || ''

  if (!route) return

  // 公共页面不拦截
  if (PUBLIC_PAGES.some(p => route.startsWith(p))) return

  const userRole = role as UserRole

  if (!checkRolePermission(userRole, route)) {
    console.warn(`[RoleGuard] "${role}" cannot access "${route}", redirecting...`)
    const homePage = getRoleHomePage(userRole)
    uni.reLaunch({ url: homePage })
  }
}

/**
 * 根据角色跳转到对应首页
 */
export function routeByRole(role?: string) {
  if (!role) {
    uni.switchTab({ url: '/pages/index/index' })
    return
  }
  const home = getRoleHomePage(role as UserRole)
  const tabBar = getRoleTabBar(role as UserRole)
  const isTab = tabBar.some(item => `/${item.pagePath}` === home)
  if (isTab) {
    uni.switchTab({ url: home })
  } else {
    uni.navigateTo({ url: home })
  }
}

/**
 * 带权限检查的导航
 */
export function navigateWithPermission(url: string, role?: string) {
  if (!role) {
    uni.navigateTo({ url: '/pages/user/login' })
    return
  }

  const userRole = role as UserRole

  if (!checkRolePermission(userRole, url)) {
    uni.showToast({ title: '无权限访问', icon: 'none' })
    return
  }

  if (isTabBarPage(userRole, url)) {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}
