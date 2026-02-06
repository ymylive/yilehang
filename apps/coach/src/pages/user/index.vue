<template>
  <view class="user-page">
    <view class="hero">
      <view class="hero-glow" aria-hidden="true"></view>

      <view class="hero-content">
        <view class="profile-row">
          <image :src="coachInfo?.avatar || '/static/default-avatar.png'" class="avatar" mode="aspectFill" />
          <view class="profile-text">
            <text class="name">{{ coachInfo?.name || t.coachDefault }}</text>
            <text class="coach-no">{{ t.coachNo }} {{ coachInfo?.coach_no || '--' }}</text>
          </view>
          <view class="status-pill">{{ t.online }}</view>
        </view>

        <view class="stats-card">
          <view class="stat-item">
            <text class="stat-value">{{ stats.totalStudents }}</text>
            <text class="stat-label">{{ t.students }}</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.totalLessons }}</text>
            <text class="stat-label">{{ t.totalLessons }}</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.avgRating.toFixed(1) }}</text>
            <text class="stat-label">{{ t.rating }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="content">
      <view class="menu-card">
        <view class="menu-head">
          <text class="menu-title">{{ t.commonFeatures }}</text>
        </view>

        <view class="menu-list">
          <view class="menu-item" @click="goTo('/pages/slots/manage')">
            <view class="menu-icon">{{ t.slotIcon }}</view>
            <text class="menu-label">{{ t.slotSetting }}</text>
            <text class="menu-arrow">&gt;</text>
          </view>

          <view class="menu-item" @click="goTo('/pages/income/index')">
            <view class="menu-icon">{{ t.incomeIcon }}</view>
            <text class="menu-label">{{ t.income }}</text>
            <text class="menu-arrow">&gt;</text>
          </view>

          <view class="menu-item" @click="goToReviews">
            <view class="menu-icon">{{ t.reviewIcon }}</view>
            <text class="menu-label">{{ t.myReviews }}</text>
            <text class="menu-arrow">&gt;</text>
          </view>

          <view class="menu-item" @click="goToSettings">
            <view class="menu-icon">{{ t.settingIcon }}</view>
            <text class="menu-label">{{ t.settings }}</text>
            <text class="menu-arrow">&gt;</text>
          </view>
        </view>
      </view>

      <view class="logout-wrap">
        <button class="logout-btn" @click="logout">{{ t.logout }}</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { coachApi } from '@/api/index'

interface CoachInfo {
  id: number
  name: string
  coach_no: string
  avatar: string | null
  total_students?: number
  total_lessons?: number
  avg_rating?: number
}

const t = {
  coachDefault: '\u6559\u7ec3',
  coachNo: '\u5de5\u53f7',
  online: '\u5728\u7ebf',
  students: '\u5b66\u5458\u6570',
  totalLessons: '\u7d2f\u8ba1\u8bfe\u65f6',
  rating: '\u8bc4\u5206',
  commonFeatures: '\u5e38\u7528\u529f\u80fd',
  slotIcon: '\u6392',
  slotSetting: '\u53ef\u7ea6\u65f6\u6bb5\u8bbe\u7f6e',
  incomeIcon: '\u6536',
  income: '\u6536\u5165\u7edf\u8ba1',
  reviewIcon: '\u8bc4',
  myReviews: '\u6211\u7684\u8bc4\u4ef7',
  settingIcon: '\u8bbe',
  settings: '\u8bbe\u7f6e',
  logout: '\u9000\u51fa\u767b\u5f55',
  settingPending: '\u529f\u80fd\u5f00\u53d1\u4e2d',
  tip: '\u63d0\u793a',
  confirmLogout: '\u786e\u5b9a\u8981\u9000\u51fa\u767b\u5f55\u5417\uff1f',
  loadProfileFailed: '\u52a0\u8f7d\u6559\u7ec3\u4fe1\u606f\u5931\u8d25'
} as const

const coachInfo = ref<CoachInfo | null>(null)
const stats = ref({
  totalStudents: 0,
  totalLessons: 0,
  avgRating: 0
})

function goTo(url: string) {
  uni.navigateTo({ url })
}

function goToReviews() {
  uni.navigateTo({ url: '/pages/reviews/index' })
}

function goToSettings() {
  uni.showToast({ title: t.settingPending, icon: 'none' })
}

function logout() {
  uni.showModal({
    title: t.tip,
    content: t.confirmLogout,
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('token')
        uni.reLaunch({ url: '/pages/user/login' })
      }
    }
  })
}

async function loadProfile() {
  try {
    const data: any = await coachApi.getProfile()
    coachInfo.value = {
      id: Number(data?.id || 0),
      name: String(data?.name || t.coachDefault),
      coach_no: String(data?.coach_no || ''),
      avatar: data?.avatar || null,
      total_students: Number(data?.total_students || 0),
      total_lessons: Number(data?.total_lessons || 0),
      avg_rating: Number(data?.avg_rating || 0)
    }

    stats.value = {
      totalStudents: Number(data?.total_students || 0),
      totalLessons: Number(data?.total_lessons || 0),
      avgRating: Number(data?.avg_rating || 0)
    }
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadProfileFailed, icon: 'none' })
  }
}

onMounted(async () => {
  await loadProfile()
})
</script>

<style lang="scss" scoped>
.user-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding-bottom: calc(120rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #ffbc47 0%, #ff8d1f 72%);
  border-radius: 0 0 44rpx 44rpx;
  padding: 36rpx 30rpx 108rpx;
}

.hero-glow {
  position: absolute;
  top: -150rpx;
  right: -120rpx;
  width: 420rpx;
  height: 420rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 244, 214, 0.88) 0%, rgba(255, 187, 80, 0.35) 48%, rgba(255, 146, 23, 0.02) 78%);
}

.hero-content {
  position: relative;
  z-index: 2;
}

.profile-row {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.avatar {
  width: 98rpx;
  height: 98rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.8);
  background: #fff;
  box-shadow: 0 8rpx 18rpx rgba(255, 141, 31, 0.2);
}

.profile-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.name {
  font-size: 36rpx;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 4rpx 14rpx rgba(0, 0, 0, 0.14);
}

.coach-no {
  display: inline-flex;
  width: fit-content;
  border-radius: 999rpx;
  padding: 6rpx 14rpx;
  font-size: 21rpx;
  color: rgba(255, 255, 255, 0.92);
  background: rgba(255, 255, 255, 0.22);
  border: 1rpx solid rgba(255, 255, 255, 0.28);
}

.status-pill {
  border-radius: 999rpx;
  padding: 8rpx 14rpx;
  font-size: 21rpx;
  color: #d47000;
  background: rgba(255, 255, 255, 0.92);
  font-weight: 700;
}

.stats-card {
  margin-top: 24rpx;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 24rpx;
  box-shadow: 0 16rpx 28rpx rgba(120, 72, 0, 0.16);
  display: flex;
  align-items: center;
  padding: 22rpx 0;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 42rpx;
  line-height: 1.1;
  font-weight: 800;
  color: #1f2533;
}

.stat-label {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #8790a4;
}

.stat-divider {
  width: 2rpx;
  height: 44rpx;
  background: #edf0f4;
}

.content {
  margin-top: -56rpx;
  position: relative;
  z-index: 3;
  padding: 0 24rpx;
}

.menu-card {
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 12rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 22rpx;
}

.menu-head {
  margin-bottom: 8rpx;
}

.menu-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2533;
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.menu-item {
  height: 98rpx;
  display: flex;
  align-items: center;
  gap: 14rpx;
  border-radius: 16rpx;
  background: #f7f8fb;
  padding: 0 12rpx;
  transition: all 0.2s ease;
}

.menu-item:active {
  background: #fff4e4;
  transform: scale(0.99);
}

.menu-icon {
  width: 66rpx;
  height: 66rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #fff7e8, #ffe4c2);
  color: #ff8f1f;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
}

.menu-label {
  flex: 1;
  font-size: 28rpx;
  color: #2b3448;
}

.menu-arrow {
  font-size: 22rpx;
  color: #9aa2b5;
}

.logout-wrap {
  margin-top: 16rpx;
}

.logout-btn {
  width: 100%;
  border: none;
  border-radius: 22rpx;
  height: 92rpx;
  line-height: 92rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #d95b4a;
  background: #fff;
  box-shadow: 0 12rpx 24rpx rgba(31, 37, 51, 0.05);
}

.logout-btn::after {
  border: none;
}
</style>
