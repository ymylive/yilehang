<template>
  <view class="page">
    <!-- 时间筛选 -->
    <view class="period-tabs">
      <view
        :class="['tab', { active: period === 'today' }]"
        @click="period = 'today'"
      >今日</view>
      <view
        :class="['tab', { active: period === 'week' }]"
        @click="period = 'week'"
      >本周</view>
      <view
        :class="['tab', { active: period === 'month' }]"
        @click="period = 'month'"
      >本月</view>
    </view>

    <!-- 核销概览 -->
    <view class="overview-card">
      <view class="overview-item">
        <text class="overview-value">{{ stats.total_verified }}</text>
        <text class="overview-label">核销订单</text>
      </view>
      <view class="overview-divider"></view>
      <view class="overview-item">
        <text class="overview-value">{{ stats.total_energy_consumed }}</text>
        <text class="overview-label">能量消耗</text>
      </view>
      <view class="overview-divider"></view>
      <view class="overview-item">
        <text class="overview-value">{{ stats.today_pending }}</text>
        <text class="overview-label">待核销</text>
      </view>
    </view>

    <!-- 统计详情 -->
    <view class="section">
      <view class="section-title">核销统计</view>
      <view class="stat-list">
        <view class="stat-row">
          <text class="stat-label">今日核销</text>
          <text class="stat-value">{{ stats.today_verified }} 单</text>
        </view>
        <view class="stat-row">
          <text class="stat-label">本周核销</text>
          <text class="stat-value">{{ stats.week_verified }} 单</text>
        </view>
        <view class="stat-row">
          <text class="stat-label">本月核销</text>
          <text class="stat-value">{{ stats.month_verified }} 单</text>
        </view>
        <view class="stat-row">
          <text class="stat-label">累计核销</text>
          <text class="stat-value">{{ stats.total_verified }} 单</text>
        </view>
        <view class="stat-row">
          <text class="stat-label">累计能量消耗</text>
          <text class="stat-value highlight">{{ stats.total_energy_consumed }} ⚡</text>
        </view>
      </view>
    </view>

    <!-- 提示 -->
    <view class="tip-card">
      <text class="tip-icon">💡</text>
      <text class="tip-text">更多详细统计功能正在开发中，敬请期待</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { merchantApi } from '@/api'

const period = ref('today')

const stats = ref({
  today_pending: 0,
  today_verified: 0,
  week_verified: 0,
  month_verified: 0,
  total_verified: 0,
  total_energy_consumed: 0
})

onMounted(() => {
  loadStats()
})

watch(period, () => {
  loadStats()
})

async function loadStats() {
  try {
    const res = await merchantApi.getStats()
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding: 20rpx;
}

.period-tabs {
  display: flex;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 10rpx;
  margin-bottom: 20rpx;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #666;
}

.tab.active {
  background: #FF8800;
  color: #FFFFFF;
  font-weight: 600;
}

.overview-card {
  display: flex;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  border-radius: 24rpx;
  padding: 40rpx 20rpx;
  margin-bottom: 20rpx;
}

.overview-item {
  flex: 1;
  text-align: center;
}

.overview-value {
  font-size: 48rpx;
  font-weight: 800;
  color: #FFFFFF;
  display: block;
}

.overview-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 8rpx;
}

.overview-divider {
  width: 2rpx;
  background: rgba(255, 255, 255, 0.3);
  margin: 10rpx 0;
}

.section {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 24rpx;
}

.stat-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 2rpx solid #F5F5F5;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 28rpx;
  color: #666;
}

.stat-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 600;
}

.stat-value.highlight {
  color: #FF8800;
  font-size: 32rpx;
}

.tip-card {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #FFF8E1;
  border-radius: 16rpx;
  padding: 24rpx;
}

.tip-icon {
  font-size: 32rpx;
}

.tip-text {
  font-size: 26rpx;
  color: #666;
}
</style>
