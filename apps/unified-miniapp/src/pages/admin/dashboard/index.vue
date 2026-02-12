<template>
  <view class="admin-dashboard">
    <view class="header">
      <text class="title">数据看板</text>
    </view>
    <view class="stats-grid">
      <view class="stat-card">
        <text class="stat-value">{{ stats.totalUsers }}</text>
        <text class="stat-label">总用户数</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ stats.totalCoaches }}</text>
        <text class="stat-label">教练数</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ stats.totalBookings }}</text>
        <text class="stat-label">今日预约</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ stats.totalRevenue }}</text>
        <text class="stat-label">本月收入</text>
      </view>
    </view>
    <view class="section">
      <text class="section-title">快捷操作</text>
      <view class="action-list">
        <view class="action-item" @click="navigateTo('/pages/admin/users/index')">
          <text>用户管理</text>
          <text class="arrow">›</text>
        </view>
        <view class="action-item" @click="navigateTo('/pages/admin/analytics/index')">
          <text>数据分析</text>
          <text class="arrow">›</text>
        </view>
      </view>
    </view>
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, onMounted } from 'vue'

const stats = ref({
  totalUsers: 0,
  totalCoaches: 0,
  totalBookings: 0,
  totalRevenue: '¥0'
})

function navigateTo(url: string) {
  uni.navigateTo({ url })
}

onMounted(() => {
  // 模拟数据
  stats.value = {
    totalUsers: 1280,
    totalCoaches: 25,
    totalBookings: 48,
    totalRevenue: '¥12,580'
  }
})
</script>

<style lang="scss" scoped>
.admin-dashboard {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20rpx;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
}

.header {
  padding: 30rpx;
  .title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.stat-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  text-align: center;

  .stat-value {
    display: block;
    font-size: 40rpx;
    font-weight: bold;
    color: #ff8800;
    margin-bottom: 10rpx;
  }

  .stat-label {
    font-size: 24rpx;
    color: #999;
  }
}

.section {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;

  .section-title {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 20rpx;
  }
}

.action-list {
  .action-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .arrow {
      color: #ccc;
      font-size: 32rpx;
    }
  }
}
</style>
