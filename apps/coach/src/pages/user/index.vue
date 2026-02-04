<template>
  <view class="user-page">
    <!-- 用户信息 -->
    <view class="user-header">
      <image :src="coachInfo?.avatar || '/static/default-avatar.png'" class="avatar" />
      <view class="user-info">
        <view class="name">{{ coachInfo?.name || '教练' }}</view>
        <view class="coach-no">工号：{{ coachInfo?.coach_no }}</view>
      </view>
    </view>

    <!-- 数据统计 -->
    <view class="stats-card">
      <view class="stat-item">
        <view class="stat-value">{{ stats.totalStudents }}</view>
        <view class="stat-label">学员数</view>
      </view>
      <view class="stat-item">
        <view class="stat-value">{{ stats.totalLessons }}</view>
        <view class="stat-label">总课时</view>
      </view>
      <view class="stat-item">
        <view class="stat-value">{{ stats.avgRating.toFixed(1) }}</view>
        <view class="stat-label">评分</view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-list">
      <view class="menu-item" @click="goTo('/pages/slots/manage')">
        <text class="icon">📅</text>
        <text class="label">可约时段设置</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/income/index')">
        <text class="icon">💰</text>
        <text class="label">收入统计</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goToReviews">
        <text class="icon">⭐</text>
        <text class="label">我的评价</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goToSettings">
        <text class="icon">⚙️</text>
        <text class="label">设置</text>
        <text class="arrow">></text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-btn" @click="logout">
      退出登录
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface CoachInfo {
  id: number
  name: string
  coach_no: string
  avatar: string | null
}

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
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToSettings() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function logout() {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('token')
        uni.reLaunch({ url: '/pages/user/login' })
      }
    }
  })
}

onMounted(() => {
  coachInfo.value = {
    id: 1,
    name: '张教练',
    coach_no: 'C001',
    avatar: null
  }

  stats.value = {
    totalStudents: 25,
    totalLessons: 156,
    avgRating: 4.8
  }
})
</script>

<style lang="scss" scoped>
.user-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 40rpx;
}

.user-header {
  display: flex;
  align-items: center;
  padding: 60rpx 30rpx 40rpx;
  background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
  color: #fff;

  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    border: 4rpx solid rgba(255, 255, 255, 0.5);
  }

  .user-info {
    margin-left: 24rpx;

    .name {
      font-size: 40rpx;
      font-weight: 600;
    }

    .coach-no {
      font-size: 26rpx;
      opacity: 0.9;
      margin-top: 8rpx;
    }
  }
}

.stats-card {
  display: flex;
  justify-content: space-around;
  background-color: #fff;
  margin: -20rpx 20rpx 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 40rpx;
      font-weight: 600;
      color: #2196F3;
    }

    .stat-label {
      font-size: 24rpx;
      color: #999;
      margin-top: 8rpx;
    }
  }
}

.menu-list {
  background-color: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;

  .menu-item {
    display: flex;
    align-items: center;
    padding: 30rpx;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .icon {
      font-size: 40rpx;
      margin-right: 20rpx;
    }

    .label {
      flex: 1;
      font-size: 30rpx;
      color: #333;
    }

    .arrow {
      color: #ccc;
      font-size: 28rpx;
    }
  }
}

.logout-btn {
  margin: 40rpx 20rpx;
  padding: 30rpx;
  background-color: #fff;
  border-radius: 16rpx;
  text-align: center;
  font-size: 32rpx;
  color: #F44336;
}
</style>
