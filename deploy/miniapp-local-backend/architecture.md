# 小程序本地后端详细架构

> 本文档提供 `apps/unified-miniapp` 本地后端层的详细架构图、数据流说明和技术细节。

---

## 1. 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        微信小程序 / H5 前端                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    UI 层 (Vue 组件)                        │ │
│  │  - pages/*/  (页面组件)                                    │ │
│  │  - components/  (RoleSwitcher, DynamicTabBar)             │ │
│  │  - directives/permission.ts  (v-permission 指令)          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                          ↕                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  本地后端层 (Local Backend)                │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  状态管理 (Pinia Stores)                             │ │ │
│  │  │  - stores/user.ts       (用户、登录态、学员)         │ │ │
│  │  │  - stores/permission.ts (角色、权限、菜单)           │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                          ↕                                 │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  本地逻辑层 (Utils / Guards)                         │ │ │
│  │  │  - utils/role-guard.ts  (路由守卫、角色页面映射)    │ │ │
│  │  │  - directives/permission.ts (权限检查函数)          │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                          ↕                                 │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  API 封装层 (api/index.ts)                           │ │ │
│  │  │  - request() 统一请求函数                            │ │ │
│  │  │  - authApi, studentApi, bookingApi, ...             │ │ │
│  │  │  - Token 自动注入、401 自动处理                      │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                          ↕                                 │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  本地存储 (uni.storage)                              │ │ │
│  │  │  - token  (JWT 字符串)                               │ │ │
│  │  │  - user   (用户对象 JSON)                            │ │ │
│  │  │  - currentStudent  (学员对象 JSON)                   │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                          ↕                                      │
└─────────────────────────────────────────────────────────────────┘
                          ↕ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                    远程后端 API (FastAPI)                        │
│              https://rl.cornna.xyz/api/v1                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据流详解

### 2.1 登录流程

```
用户输入账号密码
  ↓
pages/user/login.vue 调用 userStore.login()
  ↓
userStore.login() 调用 authApi.login(account, password)
  ↓
api/index.ts request() 发起 POST /auth/login
  ↓
远程后端验证 → 返回 { access_token, user }
  ↓
userStore.saveLoginState(token, user)
  ├─ userStore.token = token  (响应式状态)
  ├─ userStore.user = user    (响应式状态)
  ├─ uni.setStorageSync('token', token)  (持久化)
  └─ uni.setStorageSync('user', JSON.stringify(user))  (持久化)
  ↓
跳转到角色首页 (routeByRole)
  ↓
permissionStore.init()  (并行获取角色、权限、菜单)
```

### 2.2 应用启动流程

```
App.vue onLaunch / onShow
  ↓
userStore.initFromStorage()
  ├─ token = uni.getStorageSync('token')
  ├─ user = JSON.parse(uni.getStorageSync('user'))
  └─ currentStudent = JSON.parse(uni.getStorageSync('currentStudent'))
  ↓
setTimeout(() => enforceRoleRoute(user.role), 0)
  ↓
role-guard.ts enforceRoleRoute()
  ├─ 获取当前页面路径
  ├─ 检查角色是否有权访问 (checkRolePermission)
  └─ 无权限 → uni.reLaunch 到角色首页
```

### 2.3 API 请求流程

```
业务代码调用 api.get('/students')
  ↓
api/index.ts request()
  ├─ 从 uni.getStorageSync('token') 读取 token
  ├─ 添加 Authorization: Bearer <token> 请求头
  ├─ 根据环境选择 BASE_URL
  │   ├─ 微信小程序 → https://rl.cornna.xyz/api/v1
  │   └─ H5 开发 → /api/v1 (Vite proxy 转发到 localhost:8000)
  └─ uni.request() 发起请求
  ↓
收到响应
  ├─ 200-299 → 返回 res.data
  ├─ 401 → shouldHandleUnauthorized() 判断
  │   ├─ 公开接口 → 返回错误
  │   └─ 非公开接口 → 清除 token/user → uni.reLaunch('/pages/user/login')
  └─ 其他错误 → 返回错误
```

### 2.4 角色切换流程

#### RoleSwitcher 组件（统一后端切换）

```
用户点击 RoleSwitcher 选择新角色
  ↓
RoleSwitcher.vue switchRole(newRole)
  ↓
uni.showModal 确认对话框
  ↓
用户确认
  ↓
permissionStore.switchRole(newRole)
  ├─ 检查用户是否拥有该角色 (roleCodes.includes(roleCode))
  ├─ 调用 api.post('/switch-role', { role_code: roleCode })
  ├─ 远程后端验证 → 返回 { access_token, active_role }
  ├─ uni.setStorageSync('token', access_token)  (更新 token)
  ├─ permissionStore.activeRole = active_role
  └─ 并行调用 fetchPermissions() + fetchMenus()  (重新拉取权限和菜单)
  ↓
userStore.setUser({ ...user, role: newRole })  (同步角色到 user store)
  ↓
uni.reLaunch(getRoleHomePage(newRole))
  ↓
跳转到新角色首页
```

### 2.5 权限检查流程

#### 页面级权限（路由守卫）

```
用户访问页面
  ↓
App.vue onShow → enforceRoleRoute(user.role)
  ↓
role-guard.ts checkRolePermission(role, route)
  ├─ 公共页面 (login/register) → 允许
  ├─ 获取 ROLE_PAGE_MAP[role].allowedPrefixes
  └─ 检查 route 是否匹配任一前缀
  ↓
无权限 → uni.reLaunch(getRoleHomePage(role))
```

#### 元素级权限（v-permission 指令）

```
<button v-permission="'booking:create'">预约</button>
  ↓
directives/permission.ts vPermission.mounted()
  ↓
checkPermission(binding)
  ├─ 角色模式 (arg === 'role')
  │   └─ 检查 userStore.user.role 是否匹配
  └─ 权限模式 (默认)
      ├─ arg === 'all' → 检查所有权限 (every)
      └─ 默认 → 检查任一权限 (some)
  ↓
permissionStore.hasPermission(code)
  ├─ admin 角色 → 返回 true
  └─ 检查 permissionCodes.has(code)
  ↓
无权限 → el.style.display = 'none'
```

### 2.6 动态 TabBar 渲染流程

```
DynamicTabBar.vue mounted
  ↓
computed tabItems
  ├─ 优先：permissionStore.getVisibleMenus() 中 type === 'tabbar' 的菜单
  └─ 回退：ROLE_PAGE_MAP[role].tabBar 本地配置
  ↓
watch userStore.user.role → 重置 currentIndex
  ↓
watch permissionStore.initialized → updateCurrentIndex()
  ↓
用户点击 tab
  ↓
switchTab(item, idx)
  ├─ 判断是否是 tabBar 页面
  └─ uni.reLaunch({ url })  (使用 reLaunch 确保正确切换)
```

---

## 3. 核心模块详解

### 3.1 API 封装层 (`api/index.ts`)

**关键常量**：
- `BASE_URL` — 根据环境自动选择：
  - `import.meta.env.VITE_API_BASE_URL` (优先)
  - 微信小程序环境 → `https://rl.cornna.xyz/api/v1`
  - H5 开发环境 → `/api/v1`

**核心函数**：
- `getToken()` — 从 `uni.getStorageSync('token')` 读取 token
- `shouldHandleUnauthorized(url)` — 判断是否为公开接口（登录、注册等）
- `request<T>(url, options)` — 统一请求封装
  - 自动注入 token
  - 401 自动处理（清除缓存 + 跳转登录）
  - 返回 Promise<T>

**API 对象导出**：
- `api` — 通用 CRUD 方法 (get, post, put, delete)
- `authApi` — 认证相关 (login, register, logout, getUserInfo, ...)
- `studentApi` — 学员管理
- `trainingApi` — 训练记录
- `scheduleApi` — 课表
- `growthApi` — 成长档案
- `bookingApi` — 预约
- `membershipApi` — 课时卡
- `coachApi` — 教练（学员视角）
- `reviewApi` — 评价
- `aiApi` — AI 功能
- `notificationApi` — 通知
- `uploadApi` — 文件上传（使用 `uni.uploadFile`）
- `chatApi` — 即时消息
- `coachProfileApi` — 教练个人信息（教练视角）
- `coachSlotsApi` — 教练可约时段
- `coachStudentsApi` — 教练学员管理
- `coachScheduleApi` — 教练课表
- `coachReviewApi` — 教练评价
- `coachFeedbackApi` — 教练反馈
- `energyApi` — 能量系统
- `merchantApi` — 商家系统
- `leaderboardApi` — 排行榜
- `roleApi` — RBAC 角色权限

### 3.2 User Store (`stores/user.ts`)

**状态**：
```typescript
token: string                    // JWT 访问令牌
user: User | null                // 当前用户对象
currentStudent: Student | null   // 当前选中学员
students: Student[]              // 学员列表
```

**计算属性**：
```typescript
isLoggedIn: boolean              // 是否已登录
isParent / isStudent / isCoach / isAdmin: boolean  // 角色判断
userRole: string                 // 当前角色
hasPhone / hasEmail / hasWechat: boolean  // 绑定状态
```

**关键方法**：
```typescript
initFromStorage()                // 从本地存储恢复状态
saveLoginState(token, user)      // 登录成功后保存状态
login(account, password)         // 账号密码登录
loginWithEmail(email, code)      // 邮箱验证码登录
wechatLogin(code, userInfo, deviceId)  // 微信登录
wechatPhoneLogin(code, phoneCode, deviceId)  // 微信手机号登录
register(...)                    // 注册
logout()                         // 登出
checkLogin()                     // 检查登录态
setCurrentStudent(student)       // 设置当前学员
setUser(userData)                // 更新用户信息
```

### 3.3 Permission Store (`stores/permission.ts`)

**状态**：
```typescript
roles: Role[]                    // 用户角色列表
permissions: Permission[]        // 用户权限列表
menus: Menu[]                    // 用户菜单树
activeRole: string               // 当前激活角色
initialized: boolean             // 是否已初始化
```

**计算属性**：
```typescript
permissionCodes: Set<string>     // 权限代码集合（快速查找）
roleCodes: string[]              // 角色代码列表
```

**关键方法**：
```typescript
init()                           // 初始化（并行获取角色、权限、菜单）
hasPermission(code)              // 检查权限（admin 自动拥有全部权限）
hasRole(code)                    // 检查角色
fetchRoles()                     // 获取角色列表
fetchPermissions()               // 获取权限列表
fetchMenus()                     // 获取菜单列表
switchRole(roleCode)             // 切换角色（调用后端接口）
reset()                          // 重置状态（登出时调用）
setActiveRole(role)              // 设置激活角色
getVisibleMenus()                // 根据权限过滤菜单
```

### 3.4 Role Guard (`utils/role-guard.ts`)

**核心数据结构**：
```typescript
ROLE_PAGE_MAP: Record<UserRole, {
  home: string                   // 角色首页
  allowedPrefixes: string[]      // 允许访问的页面前缀
  tabBar: { pagePath: string; text: string }[]  // TabBar 配置
}>

PUBLIC_PAGES: string[]           // 公共页面（无需登录）
```

**关键函数**：
```typescript
checkRolePermission(role, route)  // 检查角色是否有权访问页面
getRoleHomePage(role)             // 获取角色首页
getRoleTabBar(role)               // 获取角色 TabBar 配置
isTabBarPage(role, route)         // 判断是否是 TabBar 页面
enforceRoleRoute(role)            // 执行路由守卫（App.vue onShow 调用）
routeByRole(role)                 // 根据角色跳转首页
navigateWithPermission(url, role) // 带权限检查的导航
```

### 3.5 Permission Directive (`directives/permission.ts`)

**指令定义**：
```typescript
vPermission: Directive<HTMLElement, string | string[]>
```

**用法示例**：
```html
<!-- 单个权限 -->
<button v-permission="'booking:create'">预约</button>

<!-- 多个权限（任一） -->
<button v-permission="['booking:create', 'booking:cancel']">操作</button>

<!-- 多个权限（全部） -->
<button v-permission:all="['booking:create', 'booking:cancel']">操作</button>

<!-- 角色检查 -->
<view v-permission:role="'coach'">教练专属</view>
```

**函数式检查**：
```typescript
hasPermission(permission, mode)   // 权限检查（用于 v-if）
hasRole(role)                     // 角色检查（用于 v-if）
```

---

## 4. 本地存储策略

### 4.1 存储键值对

| 键 | 值类型 | 示例 |
|---|---|---|
| `token` | string | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `user` | JSON string | `{"id":1,"phone":"13800000000","role":"parent",...}` |
| `currentStudent` | JSON string | `{"id":1,"name":"张三","remaining_lessons":10,...}` |

### 4.2 读写时机

**写入**：
- 登录成功 → `uni.setStorageSync('token', token)` + `uni.setStorageSync('user', JSON.stringify(user))`
- 更新用户信息 → `uni.setStorageSync('user', JSON.stringify(user))`
- 选择学员 → `uni.setStorageSync('currentStudent', JSON.stringify(student))`
- 角色切换（后端） → `uni.setStorageSync('token', newToken)`

**读取**：
- 应用启动 → `App.vue onLaunch/onShow` → `userStore.initFromStorage()`
- API 请求 → `api/index.ts request()` → `uni.getStorageSync('token')`

**清除**：
- 登出 → `uni.removeStorageSync('token')` + `uni.removeStorageSync('user')` + `uni.removeStorageSync('currentStudent')`
- 401 响应 → `uni.removeStorageSync('token')` + `uni.removeStorageSync('user')`

### 4.3 存储 API

使用 UniApp 统一存储 API：
- `uni.setStorageSync(key, value)` — 同步写入
- `uni.getStorageSync(key)` — 同步读取
- `uni.removeStorageSync(key)` — 同步删除

在微信小程序中对应 `wx.setStorageSync` / `wx.getStorageSync` / `wx.removeStorageSync`，数据持久化在本地文件系统。

---

## 5. 角色页面映射

### 5.1 Admin（管理员）

- **首页**：`/pages/admin/dashboard/index`
- **允许访问**：`pages/admin/*`, `pages/user/*`, `pages/chat/*`
- **TabBar**：看板、用户、分析、我的

### 5.2 Coach（教练）

- **首页**：`/pages/coach/workbench/index`
- **允许访问**：`pages/coach/*`, `pages/user/*`, `pages/chat/*`
- **TabBar**：工作台、课表、学员、我的

### 5.3 Parent（家长）

- **首页**：`/pages/index/index`
- **允许访问**：`pages/index/*`, `pages/booking/*`, `pages/schedule/*`, `pages/membership/*`, `pages/growth/*`, `pages/training/*`, `pages/review/*`, `pages/energy/*`, `pages/leaderboard/*`, `pages/moments/*`, `pages/user/*`, `pages/chat/*`
- **TabBar**：首页、约课、成长、课表、我的

### 5.4 Student（学员）

- **首页**：`/pages/index/index`
- **允许访问**：`pages/index/*`, `pages/schedule/*`, `pages/training/*`, `pages/growth/*`, `pages/energy/*`, `pages/leaderboard/*`, `pages/moments/*`, `pages/user/*`, `pages/chat/*`
- **TabBar**：首页、训练、成长、课表、我的

---

## 6. 技术细节

### 6.1 Token 管理双通道设计

**问题**：为什么 token 既存在响应式状态（`userStore.token`）又直接从本地存储读取（`uni.getStorageSync('token')`）？

**原因**：
1. **响应式状态**用于 UI 层判断登录态（`isLoggedIn` 计算属性）
2. **本地存储直接读取**用于 API 请求头注入，避免 Pinia store 未初始化时请求失败
3. 两者通过 `saveLoginState()` 和 `initFromStorage()` 保持同步

### 6.2 权限检查双层架构

**粗粒度（页面级）**：
- 基于角色 + 页面路径前缀
- 在 `App.vue onShow` 中执行
- 使用 `role-guard.ts` 的 `ROLE_PAGE_MAP` 配置
- 越权访问时自动重定向到角色首页

**细粒度（元素级）**：
- 基于权限码（如 `booking:create`）
- 在组件渲染时执行
- 使用 `v-permission` 指令或 `hasPermission()` 函数
- 无权限时隐藏元素（`display: none`）

### 6.3 自定义 TabBar 实现

**为什么使用自定义 TabBar**：
- 不同角色需要不同的底部导航栏
- `pages.json` 的 `tabBar.list` 是静态配置，无法动态切换

**实现方式**：
- `pages.json` 中设置 `"tabBar": { "custom": true }`
- 使用 `DynamicTabBar.vue` 组件渲染自定义 TabBar
- 根据 `userStore.user.role` 动态生成 tab 列表
- 优先使用后端菜单配置，回退到本地 `ROLE_PAGE_MAP` 配置

**代价**：
- 需要使用 `uni.reLaunch` 替代 `uni.switchTab`（因为自定义 TabBar 页面可能不在 `pages.json` 的 `tabBar.list` 中）
- 页面切换时会重新加载页面（无法保持页面状态）

### 6.4 角色切换统一实现

`RoleSwitcher.vue` 已统一使用 `permissionStore.switchRole()` 方法切换角色：

```typescript
// RoleSwitcher.vue switchRole()
await permissionStore.switchRole(role)       // 调用后端 /switch-role，获取新 token，重新拉取权限和菜单
userStore.setUser({ ...userStore.user, role }) // 同步角色到 user store
uni.reLaunch(getRoleHomePage(role))           // 跳转到新角色首页
```

完整流程：
1. 调用后端 `/switch-role` 接口
2. 获取新 token 并更新本地存储
3. 重新拉取权限和菜单
4. 同步角色到 user store（保持 UI 响应式状态一致）
5. 跳转到新角色首页

---

## 7. 安全考虑

### 7.1 Token 存储

- Token 存储在本地存储（`uni.storage`），在微信小程序中对应 `wx.storage`
- 微信小程序的本地存储是加密的，但仍需注意：
  - 不要在 token 中存储敏感信息（如密码）
  - 使用短期 token + refresh token 机制（当前未实现）
  - 定期轮换 token

### 7.2 权限校验

- 前端权限检查仅用于 UI 控制，不能作为安全边界
- 所有敏感操作必须在后端进行权限校验
- 前端权限检查的目的是提升用户体验，避免无权限用户看到无法操作的按钮

### 7.3 401 自动处理

- 收到 401 响应时自动清除本地 token 和 user 信息
- 跳转到登录页，避免用户继续使用过期 token
- 公开接口（登录、注册等）不触发自动登出

---

## 8. 性能优化

### 8.1 权限数据缓存

- 登录后一次性获取角色、权限、菜单（`permissionStore.init()`）
- 缓存在 Pinia store 中，避免重复请求
- 角色切换时重新拉取权限和菜单

### 8.2 本地存储读取

- 应用启动时从本地存储恢复状态（`userStore.initFromStorage()`）
- 避免每次启动都请求后端获取用户信息
- 用户信息变更时同步更新本地存储

### 8.3 路由守卫异步执行

- 在 `App.vue onShow` 中使用 `setTimeout(() => enforceRoleRoute(...), 0)` 异步执行
- 避免阻塞页面渲染
- 确保页面栈已就绪后再执行守卫逻辑

---

## 9. 未来优化方向

1. ~~**统一角色切换逻辑**~~：已完成，`RoleSwitcher.vue` 已统一使用 `permissionStore.switchRole()` 方法
2. **Refresh Token 机制**：实现短期 access token + 长期 refresh token，提升安全性
3. **权限数据持久化**：将权限和菜单数据缓存到本地存储，减少网络请求
4. **离线模式支持**：在网络不可用时使用本地缓存数据，提升用户体验
5. **权限变更实时通知**：后端权限变更时通过 WebSocket 推送到前端，实时更新权限状态
6. **细粒度权限控制**：扩展 `v-permission` 指令，支持更复杂的权限表达式（如 `v-permission="'booking:create && coach:active'"`）
7. **TabBar 状态保持**：优化自定义 TabBar 实现，支持页面状态保持（如使用 `keep-alive`）
