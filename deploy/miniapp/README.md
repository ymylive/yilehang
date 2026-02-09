# 易乐航统一小程序 - 构建与发布指南

## 项目概述

统一小程序 (`apps/unified-miniapp`) 是基于 UniApp 3.x + Vue 3 的多角色动态界面小程序，支持家长、学员、教练、管理员等多种角色。

## 技术栈

- **框架**: UniApp 3.x + Vue 3 Composition API
- **UI库**: Wot Design Uni (橙黄主题)
- **状态管理**: Pinia
- **构建工具**: Vite 5.x
- **包管理**: pnpm (monorepo)

## 依赖的共享包

项目依赖以下 monorepo 共享包：
- `packages/ui` - 通用UI组件
- `packages/utils` - 工具函数
- `packages/types` - TypeScript类型定义
- `packages/ai-core` - AI功能核心

## 构建流程

### 1. 环境准备

确保已安装：
- Node.js >= 18.0.0
- pnpm >= 8.0.0

```bash
# 安装依赖（在项目根目录执行）
pnpm install
```

### 2. 配置环境变量

复制环境变量模板并配置：

```bash
cp deploy/miniapp/env.example apps/unified-miniapp/.env.production
```

编辑 `.env.production` 设置生产环境API地址。

### 3. 构建小程序

#### 方式一：使用一键构建脚本（推荐）

```bash
# Windows
deploy\miniapp\build.bat

# Linux/Mac
bash deploy/miniapp/build.sh
```

#### 方式二：手动构建

```bash
# 在项目根目录执行
pnpm build:mp

# 或直接在小程序目录执行
pnpm -C apps/unified-miniapp build:mp-weixin
```

### 4. 构建产物

构建完成后，产物位于：
```
apps/unified-miniapp/dist/build/mp-weixin/
```

该目录包含：
- `app.js` - 小程序入口
- `app.json` - 小程序配置
- `pages/` - 页面文件
- `static/` - 静态资源
- `project.config.json` - 微信开发者工具配置

## 上传与发布

### 方式一：微信开发者工具手动上传（推荐）

1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择构建产物目录：`apps/unified-miniapp/dist/build/mp-weixin`
4. AppID填写：`wxdbd150a0458a3c7c`（manifest.json中配置）
5. 点击工具栏"上传"按钮
6. 填写版本号（如 1.0.0）和更新说明
7. 点击"上传"

### 方式二：使用CLI工具上传

项目提供了自动化上传脚本 `scripts/upload_miniprogram.py`：

```bash
# 在项目根目录执行
python scripts/upload_miniprogram.py
```

**注意**：CLI上传需要：
- 安装微信开发者工具
- 配置CLI环境变量
- 配置上传密钥

如果CLI不可用，脚本会自动生成手动上传指南。

### 上传后的版本管理

上传成功后，版本将显示在微信小程序后台的"版本管理 > 开发版本"中。

## 测试流程

### 1. 设置体验版

在微信小程序后台：
1. 进入"版本管理"
2. 选择开发版本，点击"设为体验版"
3. 在"成员管理 > 体验成员"中添加测试账号

### 2. 扫码体验

使用体验成员的微信扫描体验版二维码进入测试。

### 3. 功能测试清单

- [ ] 登录/注册（手机号、邮箱、微信授权）
- [ ] 角色切换（家长/学员/教练/管理员）
- [ ] 约课流程（选择教练 → 选择时段 → 确认预约）
- [ ] 课表查看（我的课表、教练课表）
- [ ] 课时卡管理（查看余额、消费记录）
- [ ] 成长档案（体测记录、训练历史）
- [ ] AI陪练功能
- [ ] 消息通知
- [ ] 评价反馈

## 发布上线

### 1. 提交审核

在微信小程序后台：
1. 进入"版本管理"
2. 选择体验版，点击"提交审核"
3. 填写审核信息：
   - 小程序类别：教育 > 在线教育
   - 标签：体育培训、青少年教育
   - 功能页面：提供主要功能页面路径
4. 提交审核

### 2. 审核周期

通常1-3个工作日，审核期间可继续更新体验版测试。

### 3. 发布上线

审核通过后：
1. 在"版本管理"中点击"发布"
2. 小程序将在微信中正式上线
3. 用户可通过搜索"易乐航"找到小程序

## 多角色页面路由

小程序根据用户角色动态显示不同页面：

| 角色 | 主要页面路径 |
|------|-------------|
| 家长 | `/pages/booking/*`, `/pages/membership/*`, `/pages/growth/*` |
| 学员 | `/pages/training/*`, `/pages/growth/*`, `/pages/energy/*` |
| 教练 | `/pages/coach/*` (工作台、课表、学员管理) |
| 管理员 | `/pages/admin/*` (数据看板、用户管理) |

## 常见问题

### Q: 构建失败提示依赖错误
A: 在项目根目录执行 `pnpm install` 重新安装依赖

### Q: 上传后小程序无法访问API
A: 检查 `.env.production` 中的API地址配置，确保使用HTTPS且已在小程序后台配置服务器域名白名单

### Q: 微信开发者工具无法导入项目
A: 确保导入的是构建产物目录 `dist/build/mp-weixin`，而非源码目录 `src`

### Q: 页面显示空白或报错
A: 检查 `manifest.json` 中的 `appid` 是否正确，确保已在微信公众平台创建小程序

## 版本信息

- 当前版本：1.0.0
- AppID：wxdbd150a0458a3c7c
- 小程序名称：易乐航

## 相关文档

- [UniApp官方文档](https://uniapp.dcloud.net.cn/)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [Wot Design Uni组件库](https://wot-design-uni.netlify.app/)
