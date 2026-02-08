<template>
  <view class="page">
    <!-- 未登录：营销页 -->
    <view v-if="!userStore.isLoggedIn" class="marketing">
      <view class="hero">
        <view class="hero-bg">
          <view class="hero-orb orb-1"></view>
          <view class="hero-orb orb-2"></view>
        </view>
        <view class="hero-content">
          <view class="brand-pill">
            <text class="pill-icon">⚡</text>
            <text>易乐航 · KTS 智慧体教</text>
          </view>
          <text class="hero-title">青春向上 · 运动更快乐</text>
          <text class="hero-subtitle">专业教练 + 科学课时 + 智能陪练</text>
          <view class="hero-actions">
            <button class="cta secondary" @click="goIntro">平台介绍</button>
            <button class="cta primary" @click="goLogin">立即登录</button>
          </view>
        </view>
      </view>

      <view class="marketing-body">
        <view class="marketing-main">
          <view class="marketing-card">
            <text class="marketing-title">为什么选择易乐航</text>
            <text class="marketing-item">• 体育 + 辅导联动，让放学后两小时更高效</text>
            <text class="marketing-item">• 训练反馈可视化，进步看得见</text>
            <text class="marketing-item">• 家长、教练、商家协同，形成成长闭环</text>
            <view class="marketing-link" @click="goIntro">
              <text>查看完整平台介绍</text>
            </view>
          </view>

          <view class="marketing-grid">
            <view class="marketing-pill">家长：成长更确定</view>
            <view class="marketing-pill">教练：专业可沉淀</view>
            <view class="marketing-pill">商家：流量可复购</view>
          </view>
        </view>

        <view class="marketing-footer">
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
          @click="navigateTo(action.path)"
        >
          <view class="action-icon">{{ action.icon }}</view>
          <text class="action-label">{{ action.label }}</text>
        </view>
      </view>

      <!-- 今日课程 -->
      <view class="section" v-permission:role="['parent', 'student']">
        <view class="section-header">
          <text class="section-title">今日课程</text>
          <text class="section-more" @click="navigateTo('/pages/schedule/index')">查看全部</text>
        </view>
        <view v-if="todaySchedules.length === 0" class="empty-tip">
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
          <text class="section-more" @click="navigateTo('/pages/growth/index')">查看详情</text>
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
import { scheduleApi, energyApi } from '@/api'
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import RoleSwitcher from '@/components/RoleSwitcher.vue'

const userStore = useUserStore()
const permissionStore = usePermissionStore()
const tabBarRef = ref()

const todaySchedules = ref<any[]>([])
const growthData = ref({
  totalLessons: 0,
  thisMonth: 0,
  energy: 0,
})

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
    { icon: '📅', label: '约课', path: '/pages/booking/index', roles: ['parent'] },
    { icon: '📋', label: '课表', path: '/pages/schedule/index', roles: ['parent', 'student'] },
    { icon: '📈', label: '成长', path: '/pages/growth/index', roles: ['parent', 'student'] },
    { icon: '🏋️', label: '训练', path: '/pages/training/index', roles: ['student'] },
    { icon: '⚡', label: '能量', path: '/pages/energy/index', roles: ['student'] },
    { icon: '💬', label: '消息', path: '/pages/chat/index', roles: ['parent', 'student', 'coach'] },
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
  uni.navigateTo({ url: path })
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
  try {
    const today = new Date().toISOString().slice(0, 10)
    const res: any = await scheduleApi.list({ start_date: today, end_date: today })
    todaySchedules.value = res?.items || res || []
  } catch (e) {
    console.error('Load schedules failed:', e)
  }
}

async function loadGrowthData() {
  if (!userStore.isLoggedIn) return
  try {
    const res: any = await energyApi.getSummary()
    growthData.value = {
      totalLessons: res?.total_lessons || 0,
      thisMonth: res?.this_month_lessons || 0,
      energy: res?.energy_balance || 0,
    }
  } catch (e) {
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
}

/* 营销页样式 */
.marketing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: calc(28rpx + env(safe-area-inset-bottom));
}

.marketing .hero {
  height: 500rpx;
  background: linear-gradient(135deg, #ffb347 0%, #ff8800 100%);
  position: relative;
  overflow: hidden;
}

.marketing-body {
  flex: 1;
  margin-top: 18rpx;
  padding: 0 24rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 18rpx;
}

.marketing-main {
  display: flex;
  flex-direction: column;
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
}

.marketing-grid {
  margin-top: 18rpx;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12rpx;
}

.marketing-footer {
  display: block;
}

.marketing-btn {
  width: 100%;
  height: 80rpx;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
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
  padding: calc(env(safe-area-inset-top) + 60rpx) 40rpx;
  text-align: center;
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
}

.hero-title {
  display: block;
  margin-top: 32rpx;
  font-size: 44rpx;
  font-weight: 700;
  color: #fff;
}

.hero-subtitle {
  display: block;
  margin-top: 16rpx;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.hero-actions {
  margin-top: 40rpx;
  display: flex;
  justify-content: center;
  gap: 20rpx;
}

.cta {
  border: none;
  border-radius: 999rpx;
  font-size: 30rpx;
  font-weight: 600;
  min-width: 220rpx;
}

.cta::after {
  border: none;
}

.cta.primary {
  background: #fff;
  color: #ff8800;
  padding: 24rpx 56rpx;
}

.cta.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1rpx solid rgba(255, 255, 255, 0.65);
  padding: 24rpx 56rpx;
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
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  margin-bottom: 24rpx;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.action-icon {
  font-size: 48rpx;
}

.action-label {
  font-size: 24rpx;
  color: #666;
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
}

.empty-tip {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
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
