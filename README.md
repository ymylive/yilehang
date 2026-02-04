# 易乐航·ITS智慧体教云平台

> 青少年体育培训智能约课管理系统

## 项目简介

易乐航·ITS智慧体教云平台是一个面向青少年体育培训机构的综合管理系统，以**微信小程序**为主要载体，提供完整的约课、排课、课时管理功能。

### 核心功能

- **在线约课**：学员可自主选择教练、时段进行预约
- **课时管理**：支持次卡/时长卡，自动扣费和余额管理
- **教练排班**：教练自主设置可约时段，灵活管理课表
- **数据看板**：实时统计预约、收入、到课率等核心指标
- **AI陪练**：基于姿态识别的智能运动辅助（增值功能）

### 系统架构

- **3大应用端口**：学员端(C端)、教练端(B端)、管理后台(Admin)
- **1个核心数据中台**：统一的用户、课程、预约数据管理

## 技术栈

| 层级 | 技术方案 |
|------|---------|
| 前端(C端/B端) | UniApp + Vue3 + TypeScript |
| 前端(Admin) | Vue3 + Element Plus + ECharts |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL + Redis |
| 小程序 | 微信小程序 (AppID: wxdbd150a0458a3c7c) |
| AI视觉 | MediaPipe |

## 项目结构

```
yilehang/
├── apps/
│   ├── client/          # C端 - 乐航成长 (UniApp)
│   ├── coach/           # B端 - 乐航教务 (UniApp)
│   ├── admin/           # 管理后台 (Vue3)
│   └── api/             # 后端服务 (FastAPI)
├── packages/
│   ├── ai-core/         # AI核心包
│   ├── ui/              # 共享UI组件
│   ├── utils/           # 共享工具
│   └── types/           # TypeScript类型
├── database/
│   ├── migrations/      # 数据库迁移
│   └── seeds/           # 种子数据
└── docker/              # Docker配置
```

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- PostgreSQL >= 15
- Redis >= 7
- pnpm >= 8

### 安装依赖

```bash
# 安装前端依赖
pnpm install

# 安装后端依赖
cd apps/api
pip install -e .
```

### 启动开发服务

```bash
# 启动后端API
pnpm dev:api

# 启动C端(H5)
pnpm dev:client

# 启动管理后台
pnpm dev:admin
```

### Docker启动

```bash
# 启动所有服务
docker-compose -f docker/docker-compose.dev.yml up -d
```

## 核心功能

### 学员端 (乐航成长)

- **在线约课**：浏览教练、选择时段、确认预约
- **我的课表**：日历视图查看已约课程
- **课时卡**：查看余额、消费记录
- **成长档案**：五维雷达图、体测历史
- **AI陪练**：实���姿态检测、运动计数

### 教练端 (乐航教务)

- **工作台**：今日课程、待办事项、快捷操作
- **时段管理**：设置每周可约时段
- **我的课表**：查看预约、确认/完成课程
- **学员管理**：学员列表、上课记录、学习反馈
- **收入统计**：月度收入、课时费明细

### 管理后台

- **数据看板**：学员数、预约数、收入统计、趋势图表
- **用户管理**：学员、教练、管理员
- **预约管理**：预约列表、状态管理
- **课时卡管理**：套餐设置、学员课时卡
- **财务管理**：收入统计、消费记录

## API文档

启动后端服务后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/api/v1/auth` | 登录、注册、微信授权 |
| 学员 | `/api/v1/students` | 学员信息管理 |
| 教练 | `/api/v1/coaches` | 教练信息、时段、收入 |
| 预约 | `/api/v1/bookings` | 预约创建、取消、改期 |
| 课时卡 | `/api/v1/memberships` | 课时卡购买、查询 |
| 仪表盘 | `/api/v1/dashboard` | 统计数据、图表 |

## 开发指南

### 代码规范

- 前端：ESLint + Prettier
- 后端：Black + Ruff

### 提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 部署

### 小程序发布

```bash
# 构建微信小程序
cd apps/client
pnpm build:mp-weixin

# 使用微信开发者工具打开 dist/build/mp-weixin 目录上传
```

### 生产环境部署

```bash
# 构建前端
pnpm build:client
pnpm build:admin

# 启动生产服务
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 开发进度

- [x] 用户认证系统（微信登录、JWT）
- [x] 学员端约课流程（教练列表→选时段→确认预约）
- [x] 学员端课表页面
- [x] 教练端工作台
- [x] 教练端时段管理
- [x] 教练端收入统计
- [x] 管理后台数据看板
- [ ] 微信支付集成
- [ ] 订阅消息推送
- [ ] 评价系统

## 许可证

MIT License
