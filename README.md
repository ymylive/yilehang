# 易乐航 ITS 智慧体教云平台

一个以微信小程序为核心载体的青少年体育培训数字化平台，覆盖学员端、教练端、管理后台与后端服务。

## 项目定位

围绕“约课-上课-课时消耗-复购运营”主链路，提供三类角色产品：

- 学员端（`apps/client`）：约课、课表、课时卡、训练记录、消息通知
- 教练端（`apps/coach`）：工作台、排课、学员管理、反馈、收入、评价
- 管理后台（`apps/admin`）：经营数据、用户管理、运营看板

后端服务位于 `apps/api`，使用 FastAPI + PostgreSQL 提供统一 API。

## 当前状态（2026-02）

已上线/已可用能力：

- 学员端：预约流程、课表、训练模块、会员卡与消费记录、基础评价流程
- 教练端：工作台、课表与详情、学员列表与详情、学习反馈、收入明细、评价回复、个人中心
- 后端：认证、教练、学员、预约、会员卡、评价、数据看板、AI 占位接口
- 部署：Docker 化（API + PostgreSQL + Nginx）并已启用 HTTPS

最近已完成的重构：

- 教练端主要页面由 Mock 数据切换为真实 API
- 学员端与教练端统一橙黄主视觉与交互动效
- 关键文案与展示逻辑统一，降低编码导致的乱码风险

## 仓库结构

```text
yilehang/
|- apps/
|  |- client/          # 学员端小程序（UniApp）
|  |- coach/           # 教练端小程序（UniApp）
|  |- admin/           # 管理后台（Vue3 + Vite）
|  \- api/             # 后端服务（FastAPI）
|- packages/
|  |- ui/
|  |- utils/
|  \- types/
|- database/
|- docker/
|- scripts/
|- docs/
\- README.md
```

## 技术栈

- 学员端/教练端：UniApp + Vue3 + TypeScript + Pinia + Wot Design Uni
- 管理后台：Vue3 + TypeScript + Element Plus + ECharts
- 后端：FastAPI + SQLAlchemy + PostgreSQL
- 部署：Docker Compose + Nginx + acme.sh（Cloudflare DNS 验证）

## 快速开始

### 1）环境要求

- Node.js >= 18
- pnpm >= 8
- Python >= 3.10
- PostgreSQL >= 15

### 2）安装依赖

```bash
pnpm install

cd apps/api
pip install -e .
cp .env.example .env
```

### 3）本地开发启动

在仓库根目录执行：

```bash
pnpm dev:api      # FastAPI，默认 :8000
pnpm dev:client   # 学员端 H5 调试
pnpm dev:coach    # 教练端 H5 调试
pnpm dev:admin    # 管理后台
```

### 4）构建微信小程序包

```bash
pnpm -C apps/client build:mp-weixin
pnpm -C apps/coach build:mp-weixin
```

微信开发者工具导入目录：

- `apps/client/dist/build/mp-weixin`
- `apps/coach/dist/build/mp-weixin`

## API 入口

后端启动后可访问：

- Swagger：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- Health：`http://localhost:8000/health`

主要模块（统一前缀 `/api/v1`）：

- `/auth`
- `/students`
- `/schedules`
- `/training`
- `/growth`
- `/bookings`
- `/memberships`
- `/coaches`
- `/reviews`
- `/dashboard`
- `/ai`

## 线上部署快照

详见：`DEPLOYMENT_REPORT.md`

- 线上域名：`https://yilehang.cornna.xyz`
- API 文档：`https://yilehang.cornna.xyz/docs`

## 后续开发计划（12 周）

详细计划见：`docs/dev_plan.md`

### 阶段 1（第 1-3 周）：内部 MVP 稳定化

目标：确保学员/教练/约课/课时主流程可稳定日常使用。

- 对齐前后端接口契约
- 完善约课冲突校验与课时扣减一致性
- 强化取消/改期异常处理与重试体验
- 完成角色权限回归检查

### 阶段 2（第 4-6 周）：外部增长能力

目标：支持对外获客与转化。

- 小程序宣传首页
- 免费体验课报名 + 一键咨询
- 简单营销能力（优惠券/推荐码）
- 转化漏斗埋点与基础看板

### 阶段 3（第 7-9 周）：运营与数据能力

目标：支持老板/运营的日常经营决策。

- 到课率、新客、续费、收入、教练课时量看板
- 低出勤/高流失/排班异常预警
- 跟进任务与闭环状态管理

### 阶段 4（第 10-12 周）：AI 运动模块 MVP

目标：上线第一批可用 AI 能力并可追踪价值。

- 跳绳动作识别（视频片段分析）
- 训练建议 + 饮食建议接口
- AI 分析历史沉淀并关联学员档案

## 质量与安全基线

- 认证：手机号验证码登录 + token 生命周期管理
- 数据安全：角色隔离、隐私协议、授权流程
- 可运维性：灰度/回滚策略、结构化日志、告警阈值

## 开发协作规范

推荐提交规范：

```text
feat: 新功能
fix: 修复问题
refactor: 重构（不改行为）
docs: 文档更新
test: 测试相关
chore: 工具链/构建维护
```

---

如需云端一键部署，请参考：

- `scripts/deploy_full.py`
- `scripts/setup_ssl.py`

并结合 `DEPLOYMENT_REPORT.md` 对照线上配置执行。
