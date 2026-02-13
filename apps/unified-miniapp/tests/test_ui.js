/**
 * Unified miniapp UI smoke tests for uni-automator v3.
 *
 * Notes:
 * - `program` and `uni` are injected by `@dcloudio/uni-automator` Jest environment.
 * - Keep cases focused and stable; full business flow belongs to manual/experience testing.
 */

let page

describe('Unified Miniapp UI smoke', () => {
  test('TC-UI-001: login page is reachable', async () => {
    page = await program.reLaunch('/pages/user/login')
    await page.waitFor(1200)

    const currentPage = await program.currentPage()
    expect(currentPage).toBeTruthy()
    expect(currentPage.path).toContain('pages/user/login')
  })

  test('TC-UI-002: login page renders basic form inputs', async () => {
    page = await program.reLaunch('/pages/user/login')
    await page.waitFor(1200)

    const inputs = await page.$$('input')
    expect(inputs.length).toBeGreaterThanOrEqual(2)
  })

  test('TC-UI-003: unauthenticated user is redirected to login', async () => {
    await uni.removeStorageSync('token')
    await uni.removeStorageSync('user')

    page = await program.reLaunch('/pages/index/index')
    await page.waitFor(1500)

    const currentPage = await program.currentPage()
    expect(currentPage.path).toContain('login')
  })
})
