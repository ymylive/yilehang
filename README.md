# 易乐航 ITS 智慧体教云平台

一个以微信小程序为核心载体的青少年体育培训数字化平台，覆盖学员端、教练端、管理后台与后端服务。

## 项目定位

围绕“约课-上课-课时消耗-复购运营”主链路，提供三类角色产品：

- 学员端（`apps/client`）：约课、课表、课时卡、训练记录、消息通知
- 教练端（`apps/coach`）：工作台、排课、学员管理、反馈、收入、评价
- 商家端（`apps/merchant`）：兑换订单处理、核销、经营统计
- 统一多角色端（`apps/unified-miniapp`）：按角色动态呈现页面与权限
- 管理后台（`apps/admin`）：经营数据、用户管理、运营看板

后端服务位于 `apps/api`，使用 FastAPI + PostgreSQL 提供统一 API。

## 当前状态（2026-02）

已上线/已可用能力：

- 学员端：预约流程、课表、训练模块、会员卡与消费记录、基础评价流程
- 教练端：工作台、课表与详情、学员列表与详情、学习反馈、收入明细、评价回复、个人中心
- 商家端：兑换订单列表、扫码核销、商家数据看板
- 统一小程序：家长/学员/教练/管理员多角色路由与页面权限控制
- 后端：认证、教练、学员、预约、会员卡、评价、数据看板、AI 占位接口
- 部署：Docker 化（API + PostgreSQL + Nginx）并已启用 HTTPS

最近已完成的重构：

- 教练端主要页面由 Mock 数据切换为真实 API
- 学员端与教练端统一橙黄主视觉与交互动效
- 关键文案与展示逻辑统一，降低编码导致的乱码风险
- 新增消息、通知、上传、能量体系、商家兑换与排行榜相关 API/页面
- 接入 RBAC 角色权限模型，支持按角色分发菜单与页面能力

## 仓库结构

```text
yilehang/
|- apps/
|  |- client/          # 学员端小程序（UniApp）
|  |- coach/           # 教练端小程序（UniApp）
|  |- merchant/        # 商家端小程序（UniApp）
|  |- unified-miniapp/ # 统一多角色小程序（UniApp）
|  |- admin/           # 管理后台（Vue3 + Vite）
|  |- web/             # 官网静态资源
|  \- api/             # 后端服务（FastAPI）
|- website/            # 官网构建产物/部署目录
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
- 商家端/统一小程序：UniApp + Vue3 + TypeScript + Pinia
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
pnpm dev:merchant # 商家端 H5 调试
pnpm dev:admin    # 管理后台
```

### 4）构建微信小程序包

```bash
pnpm -C apps/client build:mp-weixin
pnpm -C apps/coach build:mp-weixin
pnpm -C apps/merchant build:h5
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
- `/user`（角色相关）
- `/notifications`
- `/upload`
- `/chat`
- `/energy`
- `/merchants`
- `/leaderboard`

角色-页面映射与权限说明见：`docs/role_pages_mapping.md`

## 登录与注册说明（小程序）

- 微信登录：必须在微信小程序内完成授权，后端会校验微信登录凭证并同步微信昵称/头像。
- 账号登录：支持 `用户名 / 手机号 / 邮箱 + 密码`。
- 邮箱注册：支持邮箱验证码注册，并可设置用户名、手机号作为后续登录凭证。

后端环境变量（`apps/api/.env`）至少需要配置：

- `WECHAT_APPID`
- `WECHAT_SECRET`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `ALLOW_WECHAT_LOGIN_WITHOUT_SECRET=false`

## 线上部署快照

详见：`DEPLOYMENT_REPORT.md`

- 线上域名：`https://yilehang.cornna.xyz`
- API 文档：`https://yilehang.cornna.xyz/docs`

## 后续开发计划（1 周冲刺）

详细计划见：`docs/dev_plan.md`

本周目标：在 7 天内交付“学员约课 + 教练完课 + 课时扣减 + 线上可部署”的可用闭环。

本周必做（P0）：

- 学员端：登录、约课、课表、课时/消费记录
- 教练端：课表、完课、学习反馈、学员查看
- 后端：预约冲突校验、扣课一致性、角色权限最小可用
- 运维：Docker 发布、HTTPS、回滚方案

延期到下周（非本周范围）：

- AI 跳绳识别与饮食建议
- 精细化运营看板与流失预警
- 复杂营销活动（老带新、组合促销）

详细日计划与验收标准见：`docs/dev_plan.md`

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

## Deployment Update (2026-02-09)

- Re-deployed services after VPS reboot on `82.158.88.34`.
- Production domain/API kept on `https://yilehang.cornna.xyz`.
- SSL re-issued and installed via `acme.sh` using Cloudflare DNS validation.
- Miniapp production env template updated in `deploy/miniapp/env.example`:
  - `VITE_API_BASE_URL=https://yilehang.cornna.xyz/api/v1`
  - `VITE_WS_URL=wss://yilehang.cornna.xyz/api/v1/chat/ws`
  - `VITE_UPLOAD_URL=https://yilehang.cornna.xyz/api/v1/upload`
