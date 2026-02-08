<template>
  <view class="page">
    <!-- 状态筛选 -->
    <view class="status-tabs">
      <view
        :class="['tab', { active: currentStatus === '' }]"
        @click="changeStatus('')"
      >全部</view>
      <view
        :class="['tab', { active: currentStatus === 'pending' }]"
        @click="changeStatus('pending')"
      >待核销</view>
      <view
        :class="['tab', { active: currentStatus === 'verified' }]"
        @click="changeStatus('verified')"
      >已核销</view>
    </view>

    <!-- 订单列表 -->
    <view class="order-list" v-if="orders.length">
      <view
        class="order-card"
        v-for="order in orders"
        :key="order.id"
      >
        <view class="order-header">
          <text class="order-no">订单号: {{ order.order_no }}</text>
          <view :class="['order-status', order.status]">
            <text>{{ getStatusText(order.status) }}</text>
          </view>
        </view>
        <view class="order-body">
          <view class="order-icon">🎁</view>
          <view class="order-info">
            <text class="order-name">{{ order.item_name }}</text>
            <text class="order-time">{{ formatTime(order.created_at) }}</text>
          </view>
          <view class="order-right">
            <text class="order-energy">{{ order.energy_cost }} ⚡</text>
          </view>
        </view>
        <view class="order-footer" v-if="order.status === 'pending'">
          <text class="order-code">核销码: {{ order.verify_code }}</text>
          <view class="verify-btn" @click="quickVerify(order)">
            <text>核销</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无订单</text>
    </view>

    <!-- 加载更多 -->
    <view class="load-more" v-if="hasMore" @click="loadMore">
      <text>加载更多</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { merchantApi } from '@/api'

const orders = ref<any[]>([])
const currentStatus = ref('')
const page = ref(1)
const hasMore = ref(true)

onLoad((options: any) => {
  if (options?.status) {
    currentStatus.value = options.status
  }
})

onMounted(() => {
  loadOrders()
})

function changeStatus(status: string) {
  currentStatus.value = status
  page.value = 1
  orders.value = []
  loadOrders()
}

async function loadOrders() {
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (currentStatus.value) params.status = currentStatus.value

    const res = await merchantApi.getOrders(params)
    if (page.value === 1) {
      orders.value = res.items || []
    } else {
      orders.value.push(...(res.items || []))
    }
    hasMore.value = orders.value.length < res.total
  } catch (error) {
    console.error('加载订单失败', error)
  }
}

function loadMore() {
  page.value++
  loadOrders()
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

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
}

async function quickVerify(order: any) {
  uni.showModal({
    title: '确认核销',
    content: `确定核销「${order.item_name}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          uni.showLoading({ title: '核销中...' })
          await merchantApi.verifyOrder(order.id, order.verify_code)
          uni.hideLoading()
          uni.showToast({ title: '核销成功', icon: 'success' })
          // 刷新列表
          page.value = 1
          loadOrders()
        } catch (error: any) {
          uni.hideLoading()
          uni.showToast({ title: error.message || '核销失败', icon: 'none' })
        }
      }
    }
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
}

.status-tabs {
  display: flex;
  background: #FFFFFF;
  padding: 20rpx;
  gap: 16rpx;
  position: sticky;
  top: 0;
  z-index: 10;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #666;
  background: #F5F5F5;
}

.tab.active {
  background: #FF8800;
  color: #FFFFFF;
}

.order-list {
  padding: 20rpx;
}

.order-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  border-bottom: 2rpx solid #F5F5F5;
}

.order-no {
  font-size: 24rpx;
  color: #999;
}

.order-status {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
}

.order-status.pending { background: #FFF3E0; color: #FF8800; }
.order-status.verified { background: #E8F5E9; color: #4CAF50; }
.order-status.cancelled { background: #FFEBEE; color: #F44336; }
.order-status.expired { background: #F5F5F5; color: #999; }

.order-body {
  display: flex;
  align-items: center;
  padding: 20rpx;
}

.order-icon {
  width: 80rpx;
  height: 80rpx;
  background: #FFF3E0;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}

.order-info {
  flex: 1;
  margin-left: 20rpx;
}

.order-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  display: block;
}

.order-time {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.order-right {
  text-align: right;
}

.order-energy {
  font-size: 32rpx;
  font-weight: 700;
  color: #FF8800;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #FAFAFA;
}

.order-code {
  font-size: 26rpx;
  color: #666;
  font-family: monospace;
}

.verify-btn {
  padding: 12rpx 32rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  border-radius: 999rpx;
  color: #FFFFFF;
  font-size: 26rpx;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.load-more {
  text-align: center;
  padding: 30rpx;
  color: #FF8800;
  font-size: 28rpx;
}
</style>
