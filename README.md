# 易乐航·ITS智慧体教云平台

> 青少年体育培训智能管理系统

## 项目简介

易乐航·ITS智慧体教云平台是一个面向青少年体育培训机构的综合管理系统，采用"1+3+N"架构模式：

- **1个核心数据中台**：青少年运动成长数据库
- **3大应用端口**：学员/家长端(C端)、教练端(B端)、管理后台(Admin)
- **N个智能场景**：AI家庭陪练、线下体测、赛事直播等

## 技术栈

| 层级 | 技术方案 |
|------|---------|
| 前端(C端/B端) | UniApp + Vue3 + TypeScript |
| 前端(Admin) | Vue3 + Element Plus + ECharts |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL + Redis |
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

### 学员/家长端 (乐航成长)

- 成长档案：五维雷达图、体测历史
- AI智能陪练：实时姿态检测、运动计数
- 作业闯关：积分奖励系统
- 课程管理：排课、报名、签到

### 教练端 (乐航教务)

- 工作台：今日课程、待办事项
- 学员管理：学员列表、成长档案
- 排课管理：课程安排、考勤统计
- 作业管理：布置、批改、反馈

### 管理后台

- 数据驾驶舱：核心指标、趋势分析
- 用户管理：学员、教练、家长
- 课程管理：课程设置、排课
- 财务管理：收入统计、订单管理

## API文档

启动后端服务后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

### 生产环境部署

```bash
# 构建前端
pnpm build:client
pnpm build:admin

# 启动生产服务
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 许可证

MIT License
