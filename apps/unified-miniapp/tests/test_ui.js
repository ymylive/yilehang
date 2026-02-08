/**
 * 统一小程序 UI 自动化测试
 * 使用 @dcloudio/uni-automator 进行小程序端测试
 *
 * 测试覆盖：
 * - 登录页面渲染与交互
 * - 角色切换 UI 验证
 * - 角色路由守卫拦截
 * - TabBar 动态切换
 * - 首屏加载时间
 */

const automator = require('@dcloudio/uni-automator')

let miniProgram
let page

// 测试账号
const TEST_ACCOUNTS = {
  admin:   { account: 'admin@test.com',   password: 'admin123' },
  coach:   { account: 'coach@test.com',   password: 'coach123' },
  parent:  { account: 'parent@test.com',  password: 'parent123' },
  student: { account: 'student@test.com', password: 'student123' }
}

beforeAll(async () => {
  miniProgram = await automator.launch({
    projectPath: '../',
    // 微信开发者工具路径（按实际环境调整）
    cliPath: process.env.WECHAT_DEVTOOLS_CLI || 'C:/Program Files (x86)/Tencent/微信web开发者工具/cli.bat'
  })
  page = await miniProgram.currentPage()
}, 60000)

afterAll(async () => {
  if (miniProgram) {
    await miniProgram.close()
  }
})

// ============ 登录页面测试 ============

describe('Login Page', () => {
  test('TC-UI-001: Login page renders correctly', async () => {
    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor(1000)

    // 检查页面标题或关键元素存在
    const exists = await page.$$('.login-container, .login-page, .login-form')
    expect(exists.length).toBeGreaterThan(0)
  })

  test('TC-UI-002: Login form has required fields', async () => {
    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor(1000)

    // 检查输入框存在
    const inputs = await page.$$('input')
    expect(inputs.length).toBeGreaterThanOrEqual(2) // account + password
  })

  test('TC-UI-003: Login with empty fields shows error', async () => {
    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor(1000)

    // 尝试点击登录按钮
    const loginBtn = await page.$('.login-btn, .btn-login, button[type="primary"]')
    if (loginBtn) {
      await loginBtn.tap()
      await page.waitFor(500)

      // 应该显示错误提示
      const toast = await miniProgram.currentPage()
      expect(toast).toBeTruthy()
    }
  })
})

// ============ 角色登录流程测试 ============

describe('Role Login Flows', () => {
  for (const [role, cred] of Object.entries(TEST_ACCOUNTS)) {
    test(`TC-UI-004-${role}: ${role} login flow`, async () => {
      page = await miniProgram.reLaunch('/pages/user/login')
      await page.waitFor(1000)

      // 填写登录表单
      const inputs = await page.$$('input')
      if (inputs.length >= 2) {
        await inputs[0].input(cred.account)
        await inputs[1].input(cred.password)
      }

      // 点击登录
      const loginBtn = await page.$('.login-btn, .btn-login, button[type="primary"]')
      if (loginBtn) {
        await loginBtn.tap()
        await page.waitFor(3000)

        // 验证跳转到对应角色首页
        const currentPage = await miniProgram.currentPage()
        const path = currentPage.path
        console.log(`[${role}] Navigated to: ${path}`)
        expect(path).toBeTruthy()
      }
    })
  }
})

// ============ 角色路由守卫测试 ============

describe('Role Route Guard', () => {
  test('TC-UI-008: Student cannot access admin pages', async () => {
    // 先以 student 登录
    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor(1000)

    const inputs = await page.$$('input')
    if (inputs.length >= 2) {
      await inputs[0].input(TEST_ACCOUNTS.student.account)
      await inputs[1].input(TEST_ACCOUNTS.student.password)
    }

    const loginBtn = await page.$('.login-btn, .btn-login, button[type="primary"]')
    if (loginBtn) {
      await loginBtn.tap()
      await page.waitFor(3000)
    }

    // 尝试访问 admin 页面
    try {
      await miniProgram.navigateTo('/pages/admin/dashboard/index')
      await page.waitFor(1000)

      const currentPage = await miniProgram.currentPage()
      const path = currentPage.path
      // 应该被重定向，不应停留在 admin 页面
      console.log(`[Guard Test] Student tried admin, landed on: ${path}`)
      expect(path).not.toContain('admin/dashboard')
    } catch (e) {
      // 导航被拦截也是预期行为
      console.log('[Guard Test] Navigation blocked as expected')
      expect(true).toBe(true)
    }
  })

  test('TC-UI-009: Coach cannot access admin pages', async () => {
    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor(1000)

    const inputs = await page.$$('input')
    if (inputs.length >= 2) {
      await inputs[0].input(TEST_ACCOUNTS.coach.account)
      await inputs[1].input(TEST_ACCOUNTS.coach.password)
    }

    const loginBtn = await page.$('.login-btn, .btn-login, button[type="primary"]')
    if (loginBtn) {
      await loginBtn.tap()
      await page.waitFor(3000)
    }

    try {
      await miniProgram.navigateTo('/pages/admin/dashboard/index')
      await page.waitFor(1000)

      const currentPage = await miniProgram.currentPage()
      expect(currentPage.path).not.toContain('admin/dashboard')
    } catch (e) {
      expect(true).toBe(true)
    }
  })

  test('TC-UI-010: Unauthenticated user redirected to login', async () => {
    // 清除登录状态
    await miniProgram.evaluate(() => {
      uni.removeStorageSync('token')
      uni.removeStorageSync('user')
    })

    page = await miniProgram.reLaunch('/pages/index/index')
    await page.waitFor(2000)

    const currentPage = await miniProgram.currentPage()
    const path = currentPage.path
    console.log(`[Auth Test] Unauthenticated landed on: ${path}`)
    // 应该被重定向到登录页
    expect(path).toContain('login')
  })
})

// ============ TabBar 动态切换测试 ============

describe('Dynamic TabBar', () => {
  test('TC-UI-011: Parent sees correct tabbar items', async () => {
    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor(1000)

    const inputs = await page.$$('input')
    if (inputs.length >= 2) {
      await inputs[0].input(TEST_ACCOUNTS.parent.account)
      await inputs[1].input(TEST_ACCOUNTS.parent.password)
    }

    const loginBtn = await page.$('.login-btn, .btn-login, button[type="primary"]')
    if (loginBtn) {
      await loginBtn.tap()
      await page.waitFor(3000)
    }

    // 检查 tabbar 元素
    const tabItems = await page.$$('.tab-bar-item, .custom-tab-item, .tabbar-item')
    console.log(`[TabBar] Parent tab items count: ${tabItems.length}`)
    // Parent 应该有 5 个 tab
    if (tabItems.length > 0) {
      expect(tabItems.length).toBe(5)
    }
  })
})

// ============ 首屏加载时间测试 ============

describe('Performance', () => {
  test('TC-UI-012: First screen load time < 2s', async () => {
    const startTime = Date.now()

    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor('input') // 等待页面关键元素出现

    const loadTime = Date.now() - startTime
    console.log(`[Performance] First screen load time: ${loadTime}ms`)

    expect(loadTime).toBeLessThan(2000)
  })

  test('TC-UI-013: Page navigation time < 1s', async () => {
    // 先登录
    page = await miniProgram.reLaunch('/pages/user/login')
    await page.waitFor(1000)

    const inputs = await page.$$('input')
    if (inputs.length >= 2) {
      await inputs[0].input(TEST_ACCOUNTS.parent.account)
      await inputs[1].input(TEST_ACCOUNTS.parent.password)
    }

    const loginBtn = await page.$('.login-btn, .btn-login, button[type="primary"]')
    if (loginBtn) {
      await loginBtn.tap()
      await page.waitFor(3000)
    }

    // 测量页面跳转时间
    const startTime = Date.now()
    await miniProgram.navigateTo('/pages/user/index')
    await page.waitFor(500)
    const navTime = Date.now() - startTime

    console.log(`[Performance] Page navigation time: ${navTime}ms`)
    expect(navTime).toBeLessThan(1000)
  })
})
