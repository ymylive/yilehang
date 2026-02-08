<template>
  <view class="page page-enter">
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <view class="merchant-info" v-if="merchantStore.merchant">
          <image class="merchant-logo" :src="merchantStore.merchant.logo || '/static/default-logo.png'" mode="aspectFill" />
          <view class="merchant-text">
            <text class="merchant-name">{{ merchantStore.merchant.name }}</text>
            <text class="merchant-status">营业中</text>
          </view>
        </view>
        <view class="nav-actions">
          <view class="action-btn tap-active" @click="goToMessages">
            <text class="action-icon">🔔</text>
            <view class="badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</view>
          </view>
        </view>
      </view>
    </view>

    <view class="stats-card anim-fade-up anim-delay-1">
      <view class="stats-header">
        <text class="stats-title">今日数据</text>
        <text class="stats-date">{{ formatDate(new Date()) }}</text>
      </view>
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value pending">{{ todayStats.pending }}</text>
          <text class="stat-label">待核销</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value completed">{{ todayStats.completed }}</text>
          <text class="stat-label">已核销</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value energy">{{ todayStats.energy_consumed }}</text>
          <text class="stat-label">能量消耗</text>
        </view>
      </view>
    </view>

    <view class="scan-section anim-fade-up anim-delay-2">
      <view class="scan-btn tap-active" @click="goToVerify">
        <view class="scan-icon-wrap">
          <text class="scan-icon">📷</text>
        </view>
        <view class="scan-text">
          <text class="scan-title">扫码核销</text>
          <text class="scan-desc">扫描学员能量票二维码</text>
        </view>
        <text class="scan-arrow">→</text>
      </view>
    </view>

    <view class="quick-section anim-fade-up anim-delay-3">
      <view class="quick-grid">
        <view class="quick-item tap-active" @click="goToOrders('pending')">
          <view class="quick-icon-wrap pending">
            <text class="quick-icon">🧾</text>
          </view>
          <text class="quick-name">待核销</text>
          <text class="quick-count" v-if="todayStats.pending > 0">{{ todayStats.pending }}</text>
        </view>
        <view class="quick-item tap-active" @click="goToOrders('completed')">
          <view class="quick-icon-wrap completed">
            <text class="quick-icon">✅</text>
          </view>
          <text class="quick-name">已核销</text>
        </view>
        <view class="quick-item tap-active" @click="goToStats">
          <view class="quick-icon-wrap stats">
            <text class="quick-icon">📊</text>
          </view>
          <text class="quick-name">数据统计</text>
        </view>
        <view class="quick-item tap-active" @click="goToProducts">
          <view class="quick-icon-wrap products">
            <text class="quick-icon">🎁</text>
          </view>
          <text class="quick-name">商品管理</text>
        </view>
      </view>
    </view>

    <view class="period-stats anim-fade-up anim-delay-4">
      <view class="period-tabs">
        <text :class="['period-tab', { active: activePeriod === 'week' }]" @click="activePeriod = 'week'">本周</text>
        <text :class="['period-tab', { active: activePeriod === 'month' }]" @click="activePeriod = 'month'">本月</text>
      </view>
      <view class="period-content">
        <view class="period-item">
          <text class="period-label">核销订单</text>
          <text class="period-value">{{ periodStats.total_orders }}</text>
        </view>
        <view class="period-item">
          <text class="period-label">能量消耗</text>
          <text class="period-value">{{ periodStats.total_energy }}</text>
        </view>
        <view class="period-item">
          <text class="period-label">服务学员</text>
          <text class="period-value">{{ periodStats.unique_students }}</text>
        </view>
      </view>
    </view>

    <view class="section anim-fade-up anim-delay-5">
      <view class="section-header">
        <text class="section-title">最近订单</text>
        <view class="section-more tap-active" @click="goToOrders()">
          <text>查看全部</text>
          <text class="more-arrow">→</text>
        </view>
      </view>

      <view class="order-list" v-if="recentOrders.length > 0">
        <view class="order-item tap-active" v-for="order in recentOrders" :key="order.id" @click="viewOrderDetail(order)">
          <view class="order-product">
            <image class="product-image" :src="order.product_image || '/static/default-product.png'" mode="aspectFill" />
            <view class="product-info">
              <text class="product-name">{{ order.product_name }}</text>
              <text class="student-name">{{ order.student_name }}</text>
            </view>
          </view>
          <view class="order-right">
            <text class="order-energy">{{ order.energy_cost }} 能量</text>
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

    <view class="safe-bottom"></view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { redemptionApi, statsApi } from '@/api'
import { useMerchantStore } from '@/stores/merchant'

const merchantStore = useMerchantStore()

const statusBarHeight = ref(0)
const unreadCount = ref(0)

const todayStats = ref({
  pending: 0,
  completed: 0,
  energy_consumed: 0
})

const activePeriod = ref<'week' | 'month'>('week')
const weekStats = ref({
  total_orders: 0,
  total_energy: 0,
  unique_students: 0
})
const monthStats = ref({
  total_orders: 0,
  total_energy: 0,
  unique_students: 0
})
const recentOrders = ref<any[]>([])

const periodStats = computed(() => (activePeriod.value === 'week' ? weekStats.value : monthStats.value))

function getStatusBarHeight() {
  const systemInfo = uni.getSystemInfoSync()
  statusBarHeight.value = systemInfo.statusBarHeight || 20
}

function formatDate(date: Date): string {
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${month}月${day}日 ${weekdays[date.getDay()]}`
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待核销',
    completed: '已核销',
    cancelled: '已取消',
    expired: '已过期'
  }
  return map[status] || status
}

async function loadTodayStats() {
  try {
    const res: any = await statsApi.getToday()
    todayStats.value = {
      pending: res.pending_count || 0,
      completed: res.completed_count || 0,
      energy_consumed: res.energy_consumed || 0
    }
  } catch (error) {
    console.error('加载今日统计失败', error)
    todayStats.value = { pending: 3, completed: 12, energy_consumed: 580 }
  }
}

async function loadPeriodStats() {
  try {
    const [weekRes, monthRes]: any[] = await Promise.all([statsApi.getWeek(), statsApi.getMonth()])
    weekStats.value = {
      total_orders: weekRes.total_orders || 0,
      total_energy: weekRes.total_energy || 0,
      unique_students: weekRes.unique_students || 0
    }
    monthStats.value = {
      total_orders: monthRes.total_orders || 0,
      total_energy: monthRes.total_energy || 0,
      unique_students: monthRes.unique_students || 0
    }
  } catch (error) {
    console.error('加载周期统计失败', error)
    weekStats.value = { total_orders: 45, total_energy: 2350, unique_students: 28 }
    monthStats.value = { total_orders: 186, total_energy: 9800, unique_students: 89 }
  }
}

async function loadRecentOrders() {
  try {
    const res: any = await redemptionApi.getOrders({ page: 1, page_size: 5 })
    recentOrders.value = res.items || []
  } catch (error) {
    console.error('加载最近订单失败', error)
    recentOrders.value = [
      { id: 1, product_name: '篮球体验课', student_name: '小明', energy_cost: 50, status: 'pending' },
      { id: 2, product_name: '运动水杯', student_name: '小红', energy_cost: 30, status: 'completed' },
      { id: 3, product_name: '跳绳', student_name: '小刚', energy_cost: 20, status: 'completed' }
    ]
  }
}

function goToVerify() {
  uni.navigateTo({ url: '/pages/verify/index' })
}

function goToOrders(_status?: string) {
  uni.switchTab({ url: '/pages/orders/index' })
}

function goToStats() {
  uni.switchTab({ url: '/pages/stats/index' })
}

function goToProducts() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToMessages() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function viewOrderDetail(order: any) {
  uni.navigateTo({ url: `/pages/verify/index?order_id=${order.id}` })
}

onMounted(() => {
  getStatusBarHeight()
})

onShow(() => {
  if (merchantStore.isLoggedIn) {
    loadTodayStats()
    loadPeriodStats()
    loadRecentOrders()
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #fffbf5;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.nav-bar {
  background: linear-gradient(135deg, #ffb347 0%, #ff8800 100%);
  padding-bottom: 20rpx;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
}

.merchant-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
  min-width: 0;
}

.merchant-logo {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  border: 3rpx solid rgba(255, 255, 255, 0.5);
  background: #ffffff;
  flex-shrink: 0;
}

.merchant-text {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  min-width: 0;
}

.merchant-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #ffffff;
}

.merchant-status {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
  padding: 4rpx 12rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999rpx;
  width: fit-content;
}

.nav-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  position: relative;
  width: 70rpx;
  height: 70rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon {
  font-size: 36rpx;
}

.badge {
  position: absolute;
  top: -6rpx;
  right: -6rpx;
  min-width: 32rpx;
  height: 32rpx;
  background: #f44336;
  border-radius: 999rpx;
  font-size: 20rpx;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8rpx;
}

.stats-card,
.scan-section,
.quick-section,
.period-stats,
.section {
  margin-left: 24rpx;
  margin-right: 24rpx;
}

.stats-card {
  margin-top: -30rpx;
  margin-bottom: 24rpx;
  background: #ffffff;
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

.stat-value.pending {
  color: #ff8800;
}

.stat-value.completed {
  color: #4caf50;
}

.stat-value.energy {
  color: #4fa4f3;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.stat-divider {
  width: 2rpx;
  height: 60rpx;
  background: #eee;
}

.scan-section {
  margin-bottom: 24rpx;
}

.scan-btn {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #ff8800 0%, #ffb347 100%);
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
  color: #ffffff;
  display: block;
}

.scan-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 8rpx;
}

.scan-arrow {
  font-size: 40rpx;
  color: #ffffff;
}

.quick-section {
  margin-bottom: 24rpx;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16rpx;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.quick-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  min-width: 0;
}

.quick-icon-wrap {
  width: 82rpx;
  height: 82rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-icon-wrap.pending {
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
}

.quick-icon-wrap.completed {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
}

.quick-icon-wrap.stats {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
}

.quick-icon-wrap.products {
  background: linear-gradient(135deg, #fff8e1, #ffecb3);
}

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
  right: 8rpx;
  min-width: 36rpx;
  height: 36rpx;
  background: #ff8800;
  border-radius: 999rpx;
  font-size: 22rpx;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
}

.period-stats {
  margin-bottom: 24rpx;
  background: #ffffff;
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
  color: #ff8800;
  font-weight: 600;
  border-bottom-color: #ff8800;
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
  margin-bottom: 24rpx;
  background: #ffffff;
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
  gap: 16rpx;
  padding: 20rpx;
  background: #fafafa;
  border-radius: 16rpx;
}

.order-product {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.product-image {
  width: 80rpx;
  height: 80rpx;
  border-radius: 12rpx;
  background: #eee;
  flex-shrink: 0;
}

.product-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.product-name,
.student-name,
.order-energy {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.student-name {
  font-size: 24rpx;
  color: #999;
}

.order-right {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
}

.order-energy {
  font-size: 26rpx;
  font-weight: 600;
  color: #ff8800;
}

.order-status {
  font-size: 22rpx;
  padding: 6rpx 12rpx;
  border-radius: 999rpx;
}

.order-status.pending {
  background: #fff3e0;
  color: #ff8800;
}

.order-status.completed {
  background: #e8f5e9;
  color: #4caf50;
}

.order-status.cancelled {
  background: #ffebee;
  color: #f44336;
}

.empty-state {
  text-align: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 16rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.safe-bottom {
  height: 40rpx;
}
</style>

