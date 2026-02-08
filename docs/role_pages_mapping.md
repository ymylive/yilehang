# 角色-页面映射文档

## 概述

统一小程序 (`apps/unified-miniapp`) 支持多角色动态界面，根据用户角色显示不同的页面和功能。

## 角色定义

| 角色代码 | 显示名称 | 说明 |
|---------|---------|------|
| `admin` | 管理员 | 平台管理员，拥有所有权限 |
| `coach` | 教练 | 教练用户，管理课程和学员 |
| `parent` | 家长 | 家长用户，为孩子预约课程 |
| `student` | 学员 | 学员用户，查看课程和训练 |

## 页面访问权限

### 主包页面（所有角色可访问）

| 页面路径 | 说明 | 权限 |
|---------|------|------|
| `pages/index/index` | 首页 | 所有已登录用户 |
| `pages/user/login` | 登录页 | 公开 |
| `pages/user/register` | 注册页 | 公开 |
| `pages/user/index` | 个人中心 | 所有已登录用户 |
| `pages/user/profile` | 个人资料 | 所有已登录用户 |
| `pages/chat/index` | 消息列表 | 所有已登录用户 |
| `pages/chat/conversation` | 聊天详情 | 所有已登录用户 |

### 家长专属页面

| 页面路径 | 说明 | 所需权限 |
|---------|------|---------|
| `pages/booking/index` | 约课首页 | `booking:view` |
| `pages/booking/coach-detail` | 教练详情 | `booking:view` |
| `pages/booking/select-time` | 选择时段 | `booking:create` |
| `pages/booking/confirm` | 确认预约 | `booking:create` |
| `pages/membership/index` | 课时卡 | `membership:view` |
| `pages/membership/transactions` | 消费记录 | `membership:view` |
| `pages/review/create` | 课程评价 | `review:create` |

### 学员专属页面

| 页面路径 | 说明 | 所需权限 |
|---------|------|---------|
| `pages/training/index` | AI陪练首页 | `training:view` |
| `pages/training/session` | 训练中 | `training:start` |
| `pages/energy/index` | 能量中心 | `energy:view` |
| `pages/energy/redeem` | 兑换商城 | `energy:redeem` |
| `pages/leaderboard/index` | 排行榜 | `leaderboard:view` |

### 家长+学员共享页面

| 页面路径 | 说明 | 所需权限 |
|---------|------|---------|
| `pages/schedule/index` | 我的课表 | `schedule:view` |
| `pages/schedule/detail` | 课程详情 | `schedule:view` |
| `pages/growth/index` | 成长档案 | `growth:view` |
| `pages/growth/history` | 体测历史 | `growth:view` |
| `pages/growth/detail` | 体测详情 | `growth:view` |
| `pages/moments/index` | 精彩瞬间 | `moments:view` |

### 教练专属页面

| 页面路径 | 说明 | 所需权限 |
|---------|------|---------|
| `pages/coach/workbench/index` | 工作台 | `coach:workbench` |
| `pages/coach/schedule/index` | 教练课表 | `coach:schedule` |
| `pages/coach/schedule/detail` | 课程详情 | `coach:schedule` |
| `pages/coach/students/index` | 我的学员 | `coach:students` |
| `pages/coach/students/detail` | 学员详情 | `coach:students` |
| `pages/coach/students/feedback` | 提交反馈 | `coach:feedback` |
| `pages/coach/slots/manage` | 可约时段 | `coach:slots` |
| `pages/coach/income/index` | 收入统计 | `coach:income` |
| `pages/coach/reviews/index` | 评价中心 | `coach:reviews` |

### 管理员专属页面

| 页面路径 | 说明 | 所需权限 |
|---------|------|---------|
| `pages/admin/dashboard/index` | 数据看板 | `admin:dashboard` |
| `pages/admin/users/index` | 用户管理 | `admin:users` |
| `pages/admin/users/detail` | 用户详情 | `admin:users` |
| `pages/admin/analytics/index` | 数据分析 | `admin:analytics` |

## TabBar 配置

### 家长 TabBar

```
首页 → 约课 → 成长 → 课表 → 我的
```

### 学员 TabBar

```
首页 → 训练 → 成长 → 课表 → 我的
```

### 教练 TabBar

```
工作台 → 课表 → 学员 → 我的
```

### 管理员 TabBar

```
看板 → 用户 → 分析 → 我的
```

## 权限控制实现

### 1. 路由守卫 (`src/utils/role-guard.ts`)

```typescript
import { checkRolePermission, getRoleHomePage } from '@/utils/role-guard'

// 检查权限
if (!checkRolePermission(userRole, targetRoute)) {
  uni.reLaunch({ url: getRoleHomePage(userRole) })
}
```

### 2. v-permission 指令 (`src/directives/permission.ts`)

```vue
<!-- 单个权限 -->
<button v-permission="'booking:create'">预约课程</button>

<!-- 多个权限（满足任一） -->
<view v-permission="['booking:view', 'schedule:view']">...</view>

<!-- 多个权限（全部满足） -->
<view v-permission:all="['booking:create', 'booking:cancel']">...</view>

<!-- 角色检查 -->
<view v-permission:role="'coach'">教练专属内容</view>
<view v-permission:role="['coach', 'admin']">教练或管理员可见</view>
```

### 3. 函数式检查

```typescript
import { hasPermission, hasRole } from '@/directives/permission'

// 在 v-if 中使用
<view v-if="hasPermission('booking:create')">...</view>
<view v-if="hasRole('coach')">...</view>
```

## 后端 API 对接

### 获取用户角色

```
GET /api/v1/roles
Response: { data: [{ id, code, name, is_system, is_active }] }
```

### 获取用户权限

```
GET /api/v1/permissions
Response: { data: [{ id, code, name, type, resource, action }] }
```

### 获取用户菜单

```
GET /api/v1/menus
Response: { data: [{ id, code, name, type, path, icon, children }] }
```

### 切换角色

```
POST /api/v1/switch-role
Body: { role_code: "coach" }
Response: { data: { access_token, active_role, roles } }
```

## 主包大小控制

为确保主包 < 2MB：

1. **分包策略**：将角色专属页面放入 `subPackages`
2. **按需加载**：组件和工具函数按需导入
3. **图片优化**：使用 WebP 格式，压缩静态资源
4. **代码分割**：避免在主包引入大型依赖

### 当前分包结构

```
主包 (pages/)
├── index/          # 首页
├── user/           # 用户相关
└── chat/           # 消息

分包 (subPackages)
├── booking/        # 约课（家长）
├── schedule/       # 课表（家长+学员）
├── growth/         # 成长（家长+学员）
├── training/       # 训练（学员）
├── membership/     # 会员（家长）
├── energy/         # 能量（学员）
├── leaderboard/    # 排行榜（学员）
├── moments/        # 瞬间（家长+学员）
├── review/         # 评价（家长）
├── coach/          # 教练端
└── admin/          # 管理端
```
