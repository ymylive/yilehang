<template>
  <view class="page">
    <!-- 未登录：营销页 -->
    <view v-if="!userStore.isLoggedIn" class="marketing">
      <view class="hero">
        <view class="hero-bg">
          <view class="hero-orb orb-1"></view>
          <view class="hero-orb orb-2"></view>
        </view>
        <view class="hero-content fade-up">
          <view class="brand-pill">
            <wd-icon name="star-filled" size="26rpx" color="#ffffff" />
            <text>韧翎成长计划 · KTS 智慧体教</text>
          </view>
          <image class="hero-logo" :src="brandLogoSrc" mode="aspectFit" @error="handleLogoError" />
          <text class="hero-title">青春向上 · 运动更快乐</text>
          <text class="hero-subtitle">专业教练 + 科学课时 + 智能陪练</text>
          <view class="hero-actions">
            <button class="cta secondary" @tap="goIntro">平台介绍</button>
            <button class="cta primary" @tap="goLogin">立即登录</button>
          </view>
        </view>
      </view>

      <view class="marketing-body">
        <view class="marketing-main">
          <view class="marketing-card fade-up delay-1">
            <text class="marketing-title">为什么选择韧翎成长计划</text>
            <text class="marketing-item">• 体育 + 辅导联动，让放学后两小时更高效</text>
            <text class="marketing-item">• 训练反馈可视化，进步看得见</text>
            <text class="marketing-item">• 家长、教练、商家协同，形成成长闭环</text>
            <view class="marketing-link" @tap="goIntro">
              <text>查看完整平台介绍</text>
            </view>
          </view>

          <view class="marketing-grid fade-up delay-2">
            <view class="marketing-pill">家长：成长更确定</view>
            <view class="marketing-pill">教练：专业可沉淀</view>
            <view class="marketing-pill">商家：流量可复购</view>
          </view>
        </view>

        <view class="marketing-footer fade-up delay-3">
          <button class="marketing-btn primary" @tap="goRegister">立即注册体验</button>
        </view>
      </view>
    </view>

    <!-- 已登录：角色首页 -->
    <view v-else class="home">
      <!-- 顶部导航 -->
      <view class="header">
        <view class="user-info">
          <image class="avatar" :src="userStore.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <view class="user-text">
            <text class="nickname">{{ userStore.user?.nickname || '用户' }}</text>
            <text class="role-tag">{{ roleLabel }}</text>
          </view>
        </view>
        <RoleSwitcher v-if="showRoleSwitcher" />
      </view>

      <!-- 快捷入口 -->
      <view class="quick-actions">
        <view
          v-for="action in quickActions"
          :key="action.path"
          class="action-item"
          v-permission:role="action.roles"
          @tap="navigateTo(action.path)"
        >
          <view class="action-icon">
            <wd-icon :name="action.icon" size="44rpx" />
          </view>
          <text class="action-label">{{ action.label }}</text>
        </view>
      </view>

      <!-- 今日课程 -->
      <view class="section" v-permission:role="['parent', 'student']">
        <view class="section-header">
          <text class="section-title">今日课程</text>
          <text class="section-more" @tap="navigateTo('/pages/schedule/index')">查看全部</text>
        </view>
        <view v-if="todaySchedules.length === 0" class="empty-tip">
          <image :src="homeScheduleEmptyIcon" class="empty-tip-icon" mode="aspectFit" />
          <text>今日暂无课程安排</text>
        </view>
        <view v-else class="schedule-list">
          <view v-for="item in todaySchedules" :key="item.id" class="schedule-card">
            <view class="schedule-time">{{ item.start_time }} - {{ item.end_time }}</view>
            <view class="schedule-info">
              <text class="schedule-course">{{ item.course_name }}</text>
              <text class="schedule-coach">{{ item.coach_name }}</text>
            </view>
            <view class="schedule-status" :class="item.status">{{ statusLabel(item.status) }}</view>
          </view>
        </view>
      </view>

      <!-- 成长数据 -->
      <view class="section" v-permission:role="['parent', 'student']">
        <view class="section-header">
          <text class="section-title">成长数据</text>
          <text class="section-more" @tap="navigateTo('/pages/growth/index')">查看详情</text>
        </view>
        <view class="growth-stats">
          <view class="stat-item">
            <text class="stat-value">{{ growthData.totalLessons }}</text>
            <text class="stat-label">累计课时</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ growthData.thisMonth }}</text>
            <text class="stat-label">本月上课</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ growthData.energy }}</text>
            <text class="stat-label">能量值</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 自定义 TabBar -->
    <DynamicTabBar ref="tabBarRef" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { isTabBarPage, type UserRole } from '@/utils/role-guard'
import { scheduleApi, energyApi } from '@/api'
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import RoleSwitcher from '@/components/RoleSwitcher.vue'
import { BRAND_LOGO_INLINE_DATA_URI, BRAND_LOGO_PROJECT_PATH } from '@/utils/brand-logo'
import { getSemanticIcon } from '@/constants/semantic-icons'

const userStore = useUserStore()
const permissionStore = usePermissionStore()
const tabBarRef = ref()
const brandLogoSrc = ref(BRAND_LOGO_PROJECT_PATH)
const homeScheduleEmptyIcon = getSemanticIcon('home-schedule-empty')

const todaySchedules = ref<any[]>([])
const growthData = ref({
  totalLessons: 0,
  thisMonth: 0,
  energy: 0,
})

function handleLogoError() {
  if (brandLogoSrc.value !== BRAND_LOGO_INLINE_DATA_URI) {
    brandLogoSrc.value = BRAND_LOGO_INLINE_DATA_URI
  }
}

const ROLE_LABELS: Record<string, string> = {
  admin: '管理员',
  coach: '教练',
  parent: '家长',
  student: '学员',
}

const roleLabel = computed(() => ROLE_LABELS[userStore.user?.role || ''] || '用户')

const showRoleSwitcher = computed(() => {
  // 如果用户有多个角色，显示切换器
  return permissionStore.roles.length > 1
})

// 快捷入口配置
const quickActions = computed(() => {
  const role = userStore.user?.role
  const actions = [
    { icon: 'calendar', label: '约课', path: '/pages/booking/index', roles: ['parent'] },
    { icon: 'view-list', label: '课表', path: '/pages/schedule/index', roles: ['parent', 'student'] },
    { icon: 'chart-bar', label: '成长', path: '/pages/growth/index', roles: ['parent', 'student'] },
    { icon: 'app', label: '训练', path: '/pages/training/index', roles: ['student'] },
    { icon: 'star', label: '能量', path: '/pages/energy/index', roles: ['student'] },
    { icon: 'chat', label: '消息', path: '/pages/chat/index', roles: ['parent', 'student', 'coach'] },
  ]
  return actions.filter(a => a.roles.includes(role || 'parent'))
})

function goLogin() {
  uni.navigateTo({ url: '/pages/user/login' })
}

function goIntro() {
  uni.navigateTo({ url: '/pages/brand/intro' })
}

function goRegister() {
  uni.navigateTo({
    url: '/pages/user/register',
    fail: () => {
      uni.reLaunch({ url: '/pages/user/register' })
    }
  })
}

function navigateTo(path: string) {
  const userRole = userStore.user?.role as UserRole
  if (userRole && isTabBarPage(userRole, path)) {
    uni.switchTab({
      url: path,
      fail: () => {
        uni.reLaunch({ url: path })
      }
    })
  } else {
    uni.navigateTo({
      url: path,
      fail: () => {
        uni.reLaunch({ url: path })
      }
    })
  }
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待上课',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

async function loadTodaySchedules() {
  if (!userStore.isLoggedIn) return
  const role = userStore.userRole
  if (role !== 'parent' && role !== 'student') {
    todaySchedules.value = []
    return
  }

  try {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const dateStr = `${year}-${month}-${day}`
    const res: any = await scheduleApi.list({
      start_date: `${dateStr}T00:00:00`,
      end_date: `${dateStr}T23:59:59`
    })
    todaySchedules.value = res?.items || res || []
  } catch (e) {
    console.error('Load schedules failed:', e)
  }
}

async function loadGrowthData() {
  if (!userStore.isLoggedIn) return
  const role = userStore.userRole
  if (role !== 'parent' && role !== 'student') {
    growthData.value = { totalLessons: 0, thisMonth: 0, energy: 0 }
    return
  }
  if (role === 'parent' && !userStore.currentStudent) {
    growthData.value = { totalLessons: 0, thisMonth: 0, energy: 0 }
    return
  }

  try {
    const res: any = await energyApi.getSummary()
    growthData.value = {
      totalLessons: res?.total_lessons || 0,
      thisMonth: res?.this_month_lessons || 0,
      energy: res?.energy_balance || 0,
    }
  } catch (e: any) {
    if (e?.statusCode === 400 && String(e?.message || '').includes('未找到关联的学员账户')) {
      growthData.value = { totalLessons: 0, thisMonth: 0, energy: 0 }
      return
    }
    console.error('Load growth data failed:', e)
  }
}

onMounted(async () => {
  if (userStore.isLoggedIn) {
    await Promise.all([loadTodaySchedules(), loadGrowthData()])
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  overflow-x: hidden;
}

/* 营销页样式 */
.marketing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: calc(36rpx + env(safe-area-inset-bottom));
}

.marketing .hero {
  min-height: 560rpx;
  background: linear-gradient(135deg, #ffb347 0%, #ff8800 100%);
  position: relative;
  overflow: hidden;
  display: flex;
}

.marketing-body {
  flex: 1;
  margin-top: 24rpx;
  padding: 0 24rpx 8rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 22rpx;
}

.marketing-main {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.marketing-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 12rpx 28rpx rgba(31, 41, 55, 0.08);
}

.marketing-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2937;
}

.marketing-item {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #6b7280;
}

.marketing-link {
  margin-top: 16rpx;
  height: 68rpx;
  border-radius: 999rpx;
  background: #fff7eb;
  color: #ff8800;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 200ms ease, opacity 200ms ease;
}

.marketing-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12rpx;
}

.marketing-footer {
  display: block;
  padding-bottom: 6rpx;
}

.marketing-btn {
  width: 100%;
  height: 88rpx;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 200ms ease, opacity 200ms ease;
}

.marketing-btn::after {
  border: none;
}

.marketing-btn.primary {
  background: linear-gradient(135deg, #ffb347, #ff8800);
  color: #fff;
}

.marketing-pill {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 18rpx 20rpx;
  color: #374151;
  font-size: 24rpx;
  box-shadow: 0 8rpx 20rpx rgba(31, 41, 55, 0.06);
}

.hero-bg {
  position: absolute;
  inset: 0;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.orb-1 {
  width: 300rpx;
  height: 300rpx;
  right: -100rpx;
  top: -100rpx;
}

.orb-2 {
  width: 200rpx;
  height: 200rpx;
  left: -50rpx;
  bottom: -50rpx;
}

.hero-content {
  position: relative;
  z-index: 2;
  width: 100%;
  padding: calc(env(safe-area-inset-top) + 56rpx) 32rpx 44rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  box-sizing: border-box;
}

.brand-pill {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(255, 255, 255, 0.2);
  padding: 12rpx 24rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  color: #fff;
  max-width: 100%;
}

.hero-logo {
  display: block;
  width: 216rpx;
  height: 144rpx;
  margin: 0 auto;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 10rpx 26rpx rgba(0, 0, 0, 0.12);
}

.hero-title {
  display: block;
  margin-top: 0;
  font-size: 44rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
}

.hero-subtitle {
  display: block;
  margin-top: 0;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
  max-width: 560rpx;
}

.hero-actions {
  margin-top: 12rpx;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16rpx;
  width: 100%;
  max-width: 520rpx;
}

.cta {
  border: none;
  border-radius: 999rpx;
  font-size: 30rpx;
  font-weight: 600;
  min-width: 220rpx;
  min-height: 88rpx;
  line-height: 88rpx;
  padding: 0 44rpx;
  box-sizing: border-box;
  cursor: pointer;
  transition: transform 200ms ease, opacity 200ms ease;
}

.cta::after {
  border: none;
}

.cta.primary {
  background: #fff;
  color: #ff8800;
}

.cta.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1rpx solid rgba(255, 255, 255, 0.65);
}

.marketing-link:active,
.marketing-btn:active,
.cta:active {
  transform: translateY(2rpx);
  opacity: 0.94;
}

.fade-up {
  opacity: 0;
  transform: translateY(14rpx);
  animation: fadeUp 260ms ease-out forwards;
}

.delay-1 {
  animation-delay: 80ms;
}

.delay-2 {
  animation-delay: 140ms;
}

.delay-3 {
  animation-delay: 200ms;
}

@keyframes fadeUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 已登录首页样式 */
.home {
  padding: 0 24rpx calc(120rpx + env(safe-area-inset-bottom));
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(env(safe-area-inset-top) + 20rpx) 0 20rpx;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #eee;
}

.user-text {
  display: flex;
  flex-direction: column;
}

.nickname {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.role-tag {
  font-size: 22rpx;
  color: #ff8800;
  margin-top: 4rpx;
}

/* 快捷入口 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(252, 253, 255, 0.9));
  border-radius: 24rpx;
  border: 1rpx solid rgba(227, 233, 245, 0.92);
  padding: 30rpx 20rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 14rpx 32rpx rgba(29, 52, 84, 0.08);
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  min-height: 118rpx;
  justify-content: center;
  border-radius: 18rpx;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
  border: 1rpx solid rgba(228, 234, 246, 0.95);
  cursor: pointer;
  transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
}

.action-icon {
  width: 78rpx;
  height: 78rpx;
  border-radius: 22rpx;
  background: linear-gradient(135deg, #eef4ff, #eaf2ff);
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1rpx rgba(195, 212, 242, 0.55);
}

.action-label {
  font-size: 24rpx;
  color: #4b5565;
  text-align: center;
  line-height: 1.4;
}

.action-item:active {
  transform: translateY(2rpx);
  box-shadow: 0 6rpx 14rpx rgba(28, 46, 76, 0.12);
}

/* 区块样式 */
.section {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.section-more {
  font-size: 24rpx;
  color: #999;
  cursor: pointer;
}

@media screen and (max-width: 360px) {
  .marketing .hero {
    min-height: 620rpx;
  }

  .hero-content {
    padding: calc(env(safe-area-inset-top) + 46rpx) 28rpx 40rpx;
  }

  .hero-title {
    font-size: 38rpx;
  }

  .hero-subtitle {
    font-size: 24rpx;
  }

  .hero-actions {
    gap: 12rpx;
  }

  .cta {
    width: 100%;
    max-width: 420rpx;
  }

  .marketing-body {
    padding: 0 20rpx 8rpx;
  }

  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .fade-up {
    animation: none;
    opacity: 1;
    transform: none;
  }

  .marketing-link,
  .marketing-btn,
  .cta,
  .action-item {
    transition: none;
  }
}

.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
}

.empty-tip-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 10rpx;
}

/* 课程卡片 */
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.schedule-card {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #f9f9f9;
  border-radius: 12rpx;
}

.schedule-time {
  font-size: 24rpx;
  color: #ff8800;
  font-weight: 500;
  min-width: 160rpx;
}

.schedule-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.schedule-course {
  font-size: 28rpx;
  color: #333;
}

.schedule-coach {
  font-size: 22rpx;
  color: #999;
}

.schedule-status {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  background: #f0f0f0;
  color: #666;
}

.schedule-status.confirmed {
  background: #e6f7ff;
  color: #1890ff;
}

.schedule-status.completed {
  background: #f6ffed;
  color: #52c41a;
}

/* 成长数据 */
.growth-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.stat-value {
  font-size: 40rpx;
  font-weight: 700;
  color: #ff8800;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
}
</style>
