# 小程序本地后端架构说明

> 本文档描述 `apps/unified-miniapp` 中运行在客户端（微信小程序 / H5）本地的"后端"逻辑层，包括 API 封装、状态管理、Token 管理、角色/权限守卫、本地缓存策略等。

---

## 1. 模块总览

| 目录/文件 | 职责 | 本地/远程 |
|---|---|---|
| `src/api/index.ts` | 统一 HTTP 请求封装 + 各业务 API 定义 | 远程调用入口 |
| `src/stores/user.ts` | 用户状态管理（登录态、用户信息、学员信息） | 本地状态 + 远程同步 |
| `src/stores/permission.ts` | 权限状态管理（角色、权限、菜单） | 本地状态 + 远程同步 |
| `src/utils/role-guard.ts` | 角色路由守卫（页面访问控制） | 纯本地逻辑 |
| `src/directives/permission.ts` | `v-permission` 指令 + 函数式权限检查 | 纯本地逻辑 |
| `src/components/RoleSwitcher.vue` | 角色切换 UI 组件 | 本地 UI + 本地状态写入 |
| `src/components/DynamicTabBar.vue` | 动态 TabBar（按角色/权限渲染） | 本地 UI + 本地状态读取 |
| `src/main.ts` | 应用入口，注册 Pinia、全局指令 | 本地初始化 |
| `src/App.vue` | 应用生命周期，启动存储恢复 + 路由守卫 | 本地初始化 |

---

## 2. API 封装层 (`src/api/index.ts`)

### 2.1 请求基础设施

- **基地址自动切换**：通过 `import.meta.env.VITE_API_BASE_URL` 或运行时检测 `wx` 全局对象，自动选择：
  - 微信小程序环境 → `https://rl.cornna.xyz/api/v1`
  - H5 开发环境 → `/api/v1`（由 Vite devServer proxy 转发到 `localhost:8000`）
- **Token 自动注入**：每次请求从 `uni.getStorageSync('token')` 读取 JWT，自动添加 `Authorization: Bearer <token>` 请求头。
- **401 自动处理**：收到 401 响应时，若当前持有 token 且不是公开认证接口，自动清除本地 token/user 缓存并跳转登录页。
- **公开接口白名单**：`shouldHandleUnauthorized()` 维护一组不触发自动登出的认证路径（登录、注册、重置密码等）。

### 2.2 业务 API 模块

| API 对象 | 对应后端路径前缀 | 说明 |
|---|---|---|
| `authApi` | `/auth/*` | 登录、注册、邮箱验证码、微信登录、密码重置、用户信息 |
| `studentApi` | `/students/*` | 学员列表、详情、成长档案 |
| `trainingApi` | `/training/*` | AI 陪练、训练记录 |
| `scheduleApi` | `/schedules/*` | 课表、签到 |
| `growthApi` | `/growth/*` | 体测历史 |
| `bookingApi` | `/bookings/*` | 预约、取消、改期 |
| `membershipApi` | `/memberships/*` | 课时卡、消费记录 |
| `coachApi` | `/coaches/*` | 教练列表、可约时段、评价（学员视角） |
| `reviewApi` | `/reviews/*` | 课程评价 |
| `aiApi` | `/ai/*` | AI 分析、建议、对话 |
| `notificationApi` | `/notifications/*` | 消息通知 |
| `uploadApi` | `/upload/*` | 头像/图片上传（使用 `uni.uploadFile`） |
| `chatApi` | `/chat/*` | 即时消息 |
| `coachProfileApi` | `/coaches/me/*` | 教练个人信息、收入（教练视角） |
| `coachSlotsApi` | `/coaches/me/slots/*` | 教练可约时段管理 |
| `coachStudentsApi` | `/coaches/me/students/*` | 教练学员管理 |
| `coachScheduleApi` | `/coaches/me/schedule/*` | 教练课表、预约确认/完成 |
| `coachReviewApi` | `/reviews/coach/*` | 教练收到的评价（含回退逻辑） |
| `coachFeedbackApi` | `/reviews/feedbacks/*` | 教练给学员的反馈 |
| `energyApi` | `/energy/*` | 能量账户、交易、规则、等级 |
| `merchantApi` | `/merchants/*` | 商家登录、兑换、核销、统计 |
| `leaderboardApi` | `/leaderboard/*` | 排行榜 |
| `roleApi` | `/roles`, `/permissions`, `/menus`, `/switch-role` | RBAC 角色权限 |

---

## 3. 状态管理 (`src/stores/`)

### 3.1 User Store (`user.ts`)

**核心状态**：
- `token` — JWT 访问令牌
- `user` — 当前用户对象（id, phone, email, nickname, avatar, role, status）
- `currentStudent` — 当前选中的学员（家长模式下）
- `students` — 学员列表

**计算属性**：
- `isLoggedIn` — 是否已登录（基于 token 是否存在）
- `isParent / isStudent / isCoach / isAdmin` — 角色快捷判断
- `userRole` — 当前角色字符串
- `hasPhone / hasEmail / hasWechat` — 绑定状态

**关键方法**：
- `initFromStorage()` — 从 `uni.getStorageSync` 恢复 token、user、currentStudent
- `saveLoginState(token, user)` — 登录成功后同时写入响应式状态和本地存储
- `login() / loginWithEmail() / wechatLogin() / wechatPhoneLogin()` — 各登录方式，均调用 authApi 后执行 `saveLoginState`
- `register() / registerWithEmail()` — 注册后自动登录
- `logout()` — 清除所有状态和本地存储，跳转登录页
- `checkLogin()` — 检查登录态，未登录则跳转登录页

### 3.2 Permission Store (`permission.ts`)

**核心状态**：
- `roles` — 用户角色列表（从后端 `/roles` 获取）
- `permissions` — 用户权限列表（从后端 `/permissions` 获取）
- `menus` — 用户菜单树（从后端 `/menus` 获取）
- `activeRole` — 当前激活角色代码
- `initialized` — 是否已完成初始化

**关键方法**：
- `init()` — 并行获取角色、权限、菜单（登录后调用一次）
- `hasPermission(code)` — 检查权限（admin 角色自动拥有全部权限）
- `hasRole(code)` — 检查角色
- `switchRole(roleCode)` — 调用后端 `/switch-role`，获取新 token，重新拉取权限和菜单
- `getVisibleMenus()` — 递归过滤菜单树（按 is_visible、is_active、permission_code）
- `reset()` — 登出时清空所有权限状态

---

## 4. 角色路由守卫 (`src/utils/role-guard.ts`)

### 4.1 核心数据结构

`ROLE_PAGE_MAP` 为每个角色定义：
- `home` — 角色首页路径
- `allowedPrefixes` — 允许访问的页面路径前缀列表
- `tabBar` — 角色专属的底部导航栏配置

### 4.2 公共页面

`PUBLIC_PAGES` 定义无需登录即可访问的页面：`pages/user/login`、`pages/user/register`。

### 4.3 守卫函数

| 函数 | 说明 |
|---|---|
| `checkRolePermission(role, route)` | 检查角色是否有权访问指定路由 |
| `getRoleHomePage(role)` | 获取角色首页路径 |
| `getRoleTabBar(role)` | 获取角色 TabBar 配置 |
| `isTabBarPage(role, route)` | 判断路径是否是该角色的 TabBar 页面 |
| `enforceRoleRoute(role)` | 在 `App.vue onShow` 中调用，越权访问时自动重定向到角色首页 |
| `routeByRole(role)` | 登录后根据角色跳转到对应首页 |
| `navigateWithPermission(url, role)` | 带权限检查的导航，无权限时 toast 提示 |

### 4.4 执行时机

在 `App.vue` 的 `onShow` 生命周期中，通过 `setTimeout(() => enforceRoleRoute(...), 0)` 异步执行，确保页面栈已就绪。

---

## 5. 权限指令 (`src/directives/permission.ts`)

### 5.1 `v-permission` 指令

控制 DOM 元素的显示/隐藏（通过 `display: none`）：

```html
<!-- 单个权限 -->
<button v-permission="'booking:create'">预约</button>

<!-- 多个权限（任一满足） -->
<button v-permission="['booking:create', 'booking:cancel']">操作</button>

<!-- 多个权限（全部满足） -->
<button v-permission:all="['booking:create', 'booking:cancel']">操作</button>

<!-- 角色检查 -->
<view v-permission:role="'coach'">教练专属内容</view>

<!-- 多角色检查 -->
<view v-permission:role="['coach', 'admin']">管理内容</view>
```

### 5.2 函数式检查

供 `v-if` 场景使用：
- `hasPermission(code, mode)` — 权限检查（mode: 'any' | 'all'）
- `hasRole(role)` — 角色检查

### 5.3 注意事项

`main.ts` 中注册了一个简化版全局 `v-permission` 指令（基于角色匹配），与 `directives/permission.ts` 中的完整版存在实现差异。完整版通过 `permissionStore.hasPermission()` 检查细粒度权限码，简化版仅做角色字符串匹配。

---

## 6. UI 组件

### 6.1 RoleSwitcher（角色切换器）

- 显示当前角色名称，点击展开角色列表面板
- 切换时弹出确认对话框
- 切换操作：调用 `permissionStore.switchRole(role)`（后端接口）→ 同步 `userStore.user.role` → 跳转到新角色首页（`uni.reLaunch`）
- 已统一使用后端 `/switch-role` 接口切换角色，获取新 token 并重新拉取权限和菜单

### 6.2 DynamicTabBar（动态底部导航）

- 优先使用后端菜单配置（`permissionStore.getVisibleMenus()` 中 `type === 'tabbar'` 的菜单项）
- 回退到本地 `ROLE_PAGE_MAP` 配置
- 支持徽标（badge）和红点（dot）
- 监听角色变化自动重置选中索引
- 使用 `uni.reLaunch` 切换页面（因自定义 TabBar 页面可能不在 `pages.json` 的 `tabBar.list` 中）

---

## 7. Token 管理完整流程

```
登录成功
  → authApi 返回 { access_token, user }
  → userStore.saveLoginState() 写入响应式状态
  → uni.setStorageSync('token', token)  写入本地持久存储
  → uni.setStorageSync('user', JSON.stringify(user))

应用启动 / 切前台
  → App.vue onLaunch / onShow
  → userStore.initFromStorage()  从本地存储恢复到响应式状态

每次 API 请求
  → api/index.ts request()
  → uni.getStorageSync('token')  直接从本地存储读取（非响应式状态）
  → 添加 Authorization: Bearer <token> 请求头

收到 401 响应
  → 判断是否为公开接口（shouldHandleUnauthorized）
  → 非公开接口：清除 token + user 本地存储 → uni.reLaunch 到登录页

角色切换（permissionStore.switchRole）
  → 调用后端 /switch-role → 获取新 access_token
  → uni.setStorageSync('token', newToken)  更新本地存储
  → 重新拉取权限和菜单

登出
  → userStore.logout()
  → 清除 token / user / currentStudent 本地存储
  → uni.reLaunch 到登录页
```

---

## 8. 本地缓存策略

| 缓存键 | 存储内容 | 写入时机 | 读取时机 | 清除时机 |
|---|---|---|---|---|
| `token` | JWT 字符串 | 登录成功 / 角色切换 | 每次 API 请求、应用启动恢复 | 登出 / 401 |
| `user` | 用户对象 JSON | 登录成功 / 更新用户信息 | 应用启动恢复 | 登出 / 401 |
| `currentStudent` | 学员对象 JSON | 选择学员时 | 应用启动恢复 | 登出 |

所有缓存均使用 `uni.getStorageSync` / `uni.setStorageSync`（同步 API），在微信小程序中对应 `wx.getStorageSync` / `wx.setStorageSync`，数据持久化在本地文件系统中。

---

## 9. 关键设计决策

1. **Token 读取双通道**：响应式状态（`userStore.token`）用于 UI 判断登录态；本地存储直接读取（`uni.getStorageSync('token')`）用于 API 请求头注入，避免 Pinia store 未初始化时请求失败。

2. **权限双层架构**：
   - **粗粒度**：`role-guard.ts` 基于角色 + 页面路径前缀，控制页面级访问
   - **细粒度**：`permission.ts` store + `v-permission` 指令，基于权限码控制元素级显隐

3. **TabBar 动态化**：使用自定义 TabBar 组件替代 `pages.json` 静态配置，实现不同角色看到不同导航栏。代价是需要用 `uni.reLaunch` 替代 `uni.switchTab`。

4. **菜单优先级**：DynamicTabBar 优先使用后端下发的菜单配置，后端未配置时回退到本地 `ROLE_PAGE_MAP` 硬编码配置，保证离线或后端未就绪时仍可用。

5. **RoleSwitcher 统一后端切换**：`RoleSwitcher.vue` 组件已统一调用 `permissionStore.switchRole()` 方法，通过后端 `/switch-role` 接口获取新 token 并重新拉取权限和菜单，然后同步角色到 `userStore`。
