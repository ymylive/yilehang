# 易乐航·ITS智慧体教云平台 - 开发进度

## 已完成功能

### 后端 API (apps/api)

#### 数据模型 (`app/models/booking.py`)
- [x] MembershipCard - 课时卡/套餐
- [x] StudentMembership - 学员课时账户
- [x] CoachAvailableSlot - 教练可约时段
- [x] Booking - 预约记录
- [x] Transaction - 消费记录
- [x] Review - 评价
- [x] CoachFeedback - 教练反馈

#### API 端点
- [x] `/api/v1/bookings` - 预约管理
- [x] `/api/v1/memberships` - 课时卡管理
- [x] `/api/v1/coaches` - 教练列表/详情
- [x] `/api/v1/reviews` - 评价管理

#### 业务服务 (`app/services/booking_service.py`)
- [x] 预约冲突检测
- [x] 自动扣课时
- [x] 取消/改期逻辑

#### 数据库脚本
- [x] `scripts/init_db.py` - 初始化数据库表
- [x] `scripts/seed_data.py` - 种子测试数据

### 学员端小程序 (apps/client)

#### 页面
- [x] 约课首页 - 教练列表
- [x] 教练详情页
- [x] 选择时段页
- [x] 确认预约页
- [x] 我的课时卡页
- [x] 消费记录页
- [x] 课程详情页
- [x] 课程评价页
- [x] 消息通知页

### 教练端小程序 (apps/coach)

#### 页面
- [x] 工作台 - 今日概览
- [x] 我的课表 - 周视图
- [x] 课程详情
- [x] 可约时段管理
- [x] 学员列表
- [x] 学员详情
- [x] 提交学习反馈
- [x] 收入统计
- [x] 个人中心
- [x] 登录页

#### 配置
- [x] API 封装 (`api/index.ts`)
- [x] 状态管理 (`stores/coach.ts`)

### 管理后台 (apps/admin)

#### 页面
- [x] 预约管理
- [x] 课时卡管理
- [x] 学员课时卡管理

#### 配置
- [x] 路由更新
- [x] 侧边栏菜单更新

---

## 待完成功能

### 第一优先级
- [ ] 数据库迁移执行
- [ ] API 联调测试
- [ ] 微信登录集成
- [ ] Tabbar 图标设计

### 第二优先级
- [ ] 微信订阅消息推送
- [ ] 上课提醒定时任务
- [ ] 课时不足提醒

### 第三优先级
- [ ] 微信支付集成
- [ ] 首页宣传改版
- [ ] 体验课报名

---

## 启动说明

### 后端
```bash
cd apps/api

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m scripts.init_db

# 创建测试数据
python -m scripts.seed_data

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 学员端小程序
```bash
cd apps/client

# 安装依赖
pnpm install

# 开发模式
pnpm dev:mp-weixin

# 构建
pnpm build:mp-weixin
```

### 教练端小程序
```bash
cd apps/coach

# 安装依赖
pnpm install

# 开发模式
pnpm dev:mp-weixin

# 构建
pnpm build:mp-weixin
```

### 管理后台
```bash
cd apps/admin

# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 构建
pnpm build
```

---

## 测试账号

| 角色 | 手机号 | 密码 |
|------|--------|------|
| 管理员 | 13800000000 | admin123 |
| 教练 | 13800000001 | coach123 |
| 学员 | 13900000001 | student123 |

---

## 技术栈

- **前端**: UniApp + Vue3 + TypeScript + Wot Design Uni + Pinia
- **后端**: Python FastAPI + SQLAlchemy + PostgreSQL + Redis
- **管理后台**: Vue3 + Element Plus + ECharts
- **小程序**: 微信小程序 (AppID: wxdbd150a0458a3c7c)
