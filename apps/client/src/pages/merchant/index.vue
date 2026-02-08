<template>
  <view class="page">
    <!-- 顶部商家信息 -->
    <view class="merchant-header">
      <view class="header-bg">
        <view class="bg-orb orb-1"></view>
        <view class="bg-orb orb-2"></view>
      </view>
      <view class="header-content">
        <view class="merchant-info">
          <view class="merchant-avatar">
            <text class="avatar-text">{{ merchantName.charAt(0) }}</text>
          </view>
          <view class="merchant-text">
            <text class="merchant-name">{{ merchantName }}</text>
            <text class="merchant-status">营业中</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 今日统计卡片 -->
    <view class="stats-card">
      <view class="stats-header">
        <text class="stats-title">今日数据</text>
        <text class="stats-date">{{ formatDate(new Date()) }}</text>
      </view>
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value pending">{{ stats.today_pending }}</text>
          <text class="stat-label">待核销</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value completed">{{ stats.today_verified }}</text>
          <text class="stat-label">已核销</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value energy">{{ stats.total_energy_consumed }}</text>
          <text class="stat-label">能量消耗</text>
        </view>
      </view>
    </view>

    <!-- 扫码核销大按钮 -->
    <view class="scan-section">
      <view class="scan-btn" @click="goToVerify">
        <view class="scan-icon-wrap">
          <text class="scan-icon">📷</text>
        </view>
        <view class="scan-text">
          <text class="scan-title">扫码核销</text>
          <text class="scan-desc">扫描学员能量支票核销码</text>
        </view>
        <text class="scan-arrow">→</text>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view class="quick-section">
      <view class="quick-grid">
        <view class="quick-item" @click="goToOrders('pending')">
          <view class="quick-icon-wrap pending">
            <text class="quick-icon">📋</text>
          </view>
          <text class="quick-name">待核销</text>
          <text class="quick-count" v-if="stats.today_pending > 0">{{ stats.today_pending }}</text>
        </view>
        <view class="quick-item" @click="goToOrders('verified')">
          <view class="quick-icon-wrap completed">
            <text class="quick-icon">✅</text>
          </view>
          <text class="quick-name">已核销</text>
        </view>
        <view class="quick-item" @click="goToStats">
          <view class="quick-icon-wrap stats">
            <text class="quick-icon">📊</text>
          </view>
          <text class="quick-name">数据统计</text>
        </view>
        <view class="quick-item" @click="goToProducts">
          <view class="quick-icon-wrap products">
            <text class="quick-icon">🎁</text>
          </view>
          <text class="quick-name">商品管理</text>
        </view>
      </view>
    </view>

    <!-- 本周/本月统计 -->
    <view class="period-stats">
      <view class="period-tabs">
        <text
          :class="['period-tab', { active: activePeriod === 'week' }]"
          @click="activePeriod = 'week'"
        >本周</text>
        <text
          :class="['period-tab', { active: activePeriod === 'month' }]"
          @click="activePeriod = 'month'"
        >本月</text>
      </view>
      <view class="period-content">
        <view class="period-item">
          <text class="period-label">核销订单</text>
          <text class="period-value">{{ activePeriod === 'week' ? stats.week_verified : stats.month_verified }}</text>
        </view>
        <view class="period-item">
          <text class="period-label">能量消耗</text>
          <text class="period-value">{{ stats.total_energy_consumed }}</text>
        </view>
        <view class="period-item">
          <text class="period-label">总核销</text>
          <text class="period-value">{{ stats.total_verified }}</text>
        </view>
      </view>
    </view>

    <!-- 最近订单 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">最近订单</text>
        <view class="section-more" @click="goToOrders()">
          <text>查看全部</text>
          <text class="more-arrow">→</text>
        </view>
      </view>

      <view class="order-list" v-if="recentOrders.length > 0">
        <view
          class="order-item"
          v-for="order in recentOrders"
          :key="order.id"
        >
          <view class="order-product">
            <view class="product-icon">🎁</view>
            <view class="product-info">
              <text class="product-name">{{ order.item_name }}</text>
              <text class="order-time">{{ formatTime(order.created_at) }}</text>
            </view>
          </view>
          <view class="order-right">
            <text class="order-energy">{{ order.energy_cost }} ⚡</text>
            <view :class="['order-status', order.status]">
              <text>{{ getStatusText(order.status) }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-icon">📦</text>
        <text class="empty-text">暂无订单</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { merchantApi } from '@/api'

const userStore = useUserStore()

const merchantName = ref('我的商家')
const activePeriod = ref<'week' | 'month'>('week')

const stats = ref({
  today_pending: 0,
  today_verified: 0,
  week_verified: 0,
  month_verified: 0,
  total_verified: 0,
  total_energy_consumed: 0
})

const recentOrders = ref<any[]>([])

onMounted(async () => {
  merchantName.value = userStore.user?.nickname || '我的商家'
  await Promise.all([loadStats(), loadRecentOrders()])
})

async function loadStats() {
  try {
    const res = await merchantApi.getStats()
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

async function loadRecentOrders() {
  try {
    const res = await merchantApi.getOrders({ page: 1, page_size: 5 })
    recentOrders.value = res.items || []
  } catch (error) {
    console.error('加载订单失败', error)
  }
}

function formatDate(date: Date): string {
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${month}月${day}日 ${weekdays[date.getDay()]}`
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待核销',
    verified: '已核销',
    cancelled: '已取消',
    expired: '已过期'
  }
  return map[status] || status
}

function goToVerify() {
  uni.navigateTo({ url: '/pages/merchant/verify' })
}

function goToOrders(status?: string) {
  const url = status ? `/pages/merchant/orders?status=${status}` : '/pages/merchant/orders'
  uni.navigateTo({ url })
}

function goToStats() {
  uni.navigateTo({ url: '/pages/merchant/stats' })
}

function goToProducts() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: 40rpx;
}

.merchant-header {
  position: relative;
  padding: 60rpx 30rpx 40rpx;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
  border-radius: 0 0 60rpx 60rpx;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.orb-1 { width: 200rpx; height: 200rpx; top: -50rpx; right: -30rpx; }
.orb-2 { width: 150rpx; height: 150rpx; bottom: 20rpx; left: -40rpx; }

.header-content {
  position: relative;
  z-index: 1;
}

.merchant-info {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.merchant-avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 48rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.merchant-text {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.merchant-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.merchant-status {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  padding: 6rpx 16rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999rpx;
  width: fit-content;
}

.stats-card {
  margin: -20rpx 24rpx 24rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 12rpx 30rpx rgba(255, 136, 0, 0.15);
  position: relative;
  z-index: 10;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.stats-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #333;
}

.stats-date {
  font-size: 24rpx;
  color: #999;
}

.stats-grid {
  display: flex;
  align-items: center;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 48rpx;
  font-weight: 800;
  display: block;
  line-height: 1.2;
}

.stat-value.pending { color: #FF8800; }
.stat-value.completed { color: #4CAF50; }
.stat-value.energy { color: #4FA4F3; }

.stat-label {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.stat-divider {
  width: 2rpx;
  height: 60rpx;
  background: #EEE;
}

.scan-section {
  padding: 0 24rpx;
  margin-bottom: 24rpx;
}

.scan-btn {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #FF8800 0%, #FFB347 100%);
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 12rpx 30rpx rgba(255, 136, 0, 0.3);
}

.scan-icon-wrap {
  width: 100rpx;
  height: 100rpx;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.scan-icon {
  font-size: 50rpx;
}

.scan-text {
  flex: 1;
}

.scan-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #FFFFFF;
  display: block;
}

.scan-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 8rpx;
}

.scan-arrow {
  font-size: 40rpx;
  color: #FFFFFF;
}

.quick-section {
  padding: 0 24rpx;
  margin-bottom: 24rpx;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  position: relative;
}

.quick-icon-wrap {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-icon-wrap.pending { background: linear-gradient(135deg, #FFF3E0, #FFE0B2); }
.quick-icon-wrap.completed { background: linear-gradient(135deg, #E8F5E9, #C8E6C9); }
.quick-icon-wrap.stats { background: linear-gradient(135deg, #E3F2FD, #BBDEFB); }
.quick-icon-wrap.products { background: linear-gradient(135deg, #FFF8E1, #FFECB3); }

.quick-icon {
  font-size: 36rpx;
}

.quick-name {
  font-size: 24rpx;
  color: #666;
}

.quick-count {
  position: absolute;
  top: -8rpx;
  right: 10rpx;
  min-width: 36rpx;
  height: 36rpx;
  background: #FF8800;
  border-radius: 999rpx;
  font-size: 22rpx;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
}

.period-stats {
  margin: 0 24rpx 24rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.period-tabs {
  display: flex;
  gap: 24rpx;
  margin-bottom: 20rpx;
}

.period-tab {
  font-size: 28rpx;
  color: #999;
  padding-bottom: 12rpx;
  border-bottom: 4rpx solid transparent;
}

.period-tab.active {
  color: #FF8800;
  font-weight: 600;
  border-bottom-color: #FF8800;
}

.period-content {
  display: flex;
  justify-content: space-around;
}

.period-item {
  text-align: center;
}

.period-label {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 8rpx;
}

.period-value {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
}

.section {
  margin: 0 24rpx 24rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #333;
}

.section-more {
  display: flex;
  align-items: center;
  font-size: 26rpx;
  color: #999;
}

.more-arrow {
  margin-left: 8rpx;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #FAFAFA;
  border-radius: 16rpx;
}

.order-product {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.product-icon {
  width: 60rpx;
  height: 60rpx;
  background: #FFF3E0;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.product-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.order-time {
  font-size: 22rpx;
  color: #999;
}

.order-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
}

.order-energy {
  font-size: 26rpx;
  font-weight: 600;
  color: #FF8800;
}

.order-status {
  font-size: 22rpx;
  padding: 6rpx 12rpx;
  border-radius: 999rpx;
}

.order-status.pending { background: #FFF3E0; color: #FF8800; }
.order-status.verified { background: #E8F5E9; color: #4CAF50; }
.order-status.cancelled { background: #FFEBEE; color: #F44336; }

.empty-state {
  text-align: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 60rpx;
  display: block;
  margin-bottom: 16rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}
</style>
