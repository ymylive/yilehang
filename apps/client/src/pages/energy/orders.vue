<template>
  <view class="page">
    <!-- 状态筛选 -->
    <view class="status-tabs">
      <view
        :class="['tab', { active: currentStatus === '' }]"
        @click="currentStatus = ''"
      >全部</view>
      <view
        :class="['tab', { active: currentStatus === 'pending' }]"
        @click="currentStatus = 'pending'"
      >待使用</view>
      <view
        :class="['tab', { active: currentStatus === 'verified' }]"
        @click="currentStatus = 'verified'"
      >已使用</view>
      <view
        :class="['tab', { active: currentStatus === 'expired' }]"
        @click="currentStatus = 'expired'"
      >已过期</view>
    </view>

    <!-- 订单列表 -->
    <view class="order-list" v-if="orders.length">
      <view
        class="order-card"
        v-for="order in orders"
        :key="order.id"
        @click="showOrderDetail(order)"
      >
        <view class="order-header">
          <text class="order-merchant">{{ order.merchant_name }}</text>
          <text :class="['order-status', order.status]">{{ getStatusText(order.status) }}</text>
        </view>
        <view class="order-body">
          <view class="order-image">
            <image v-if="order.item_image" :src="order.item_image" mode="aspectFill" />
            <view v-else class="order-placeholder">🎁</view>
          </view>
          <view class="order-info">
            <text class="order-name">{{ order.item_name }}</text>
            <text class="order-cost">{{ order.energy_cost }} ⚡</text>
            <text class="order-time">{{ formatTime(order.created_at) }}</text>
          </view>
        </view>
        <view class="order-footer" v-if="order.status === 'pending'">
          <text class="order-expire">有效期至 {{ formatDate(order.expire_at) }}</text>
          <view class="order-code">
            <text class="code-label">核销码</text>
            <text class="code-value">{{ order.verify_code }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无兑换记录</text>
      <button class="empty-btn" @click="goToRedeem">去兑换</button>
    </view>

    <!-- 订单详情弹窗 -->
    <view class="detail-modal" v-if="selectedOrder" @click="selectedOrder = null">
      <view class="detail-card" @click.stop>
        <view class="detail-header">
          <text class="detail-title">兑换详情</text>
          <text class="detail-close" @click="selectedOrder = null">×</text>
        </view>
        <view class="detail-content">
          <view class="detail-item">
            <text class="detail-label">商品名称</text>
            <text class="detail-value">{{ selectedOrder.item_name }}</text>
          </view>
          <view class="detail-item">
            <text class="detail-label">商家</text>
            <text class="detail-value">{{ selectedOrder.merchant_name }}</text>
          </view>
          <view class="detail-item">
            <text class="detail-label">商家地址</text>
            <text class="detail-value">{{ selectedOrder.merchant_address || '暂无' }}</text>
          </view>
          <view class="detail-item">
            <text class="detail-label">消耗能量</text>
            <text class="detail-value">{{ selectedOrder.energy_cost }} ⚡</text>
          </view>
          <view class="detail-item">
            <text class="detail-label">订单号</text>
            <text class="detail-value">{{ selectedOrder.order_no }}</text>
          </view>
          <view class="detail-item">
            <text class="detail-label">兑换时间</text>
            <text class="detail-value">{{ formatDateTime(selectedOrder.created_at) }}</text>
          </view>
          <view class="detail-item" v-if="selectedOrder.status === 'pending'">
            <text class="detail-label">有效期至</text>
            <text class="detail-value">{{ formatDateTime(selectedOrder.expire_at) }}</text>
          </view>
          <view class="detail-item" v-if="selectedOrder.verified_at">
            <text class="detail-label">核销时间</text>
            <text class="detail-value">{{ formatDateTime(selectedOrder.verified_at) }}</text>
          </view>
        </view>

        <view class="qrcode-section" v-if="selectedOrder.status === 'pending'">
          <view class="qrcode-box">
            <text class="qrcode-code">{{ selectedOrder.verify_code }}</text>
            <text class="qrcode-hint">请向商家出示此核销码</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { merchantApi } from '@/api'

const orders = ref<any[]>([])
const currentStatus = ref('')
const selectedOrder = ref<any>(null)
const page = ref(1)
const hasMore = ref(true)

onMounted(() => {
  loadOrders()
})

watch(currentStatus, () => {
  page.value = 1
  orders.value = []
  loadOrders()
})

async function loadOrders() {
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (currentStatus.value) params.status = currentStatus.value

    const res = await merchantApi.getMyOrders(params)
    if (page.value === 1) {
      orders.value = res.items
    } else {
      orders.value.push(...res.items)
    }
    hasMore.value = orders.value.length < res.total
  } catch (error) {
    console.error('加载订单失败', error)
  }
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待使用',
    verified: '已使用',
    cancelled: '已取消',
    expired: '已过期'
  }
  return map[status] || status
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function formatDateTime(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function showOrderDetail(order: any) {
  selectedOrder.value = order
}

function goToRedeem() {
  uni.navigateTo({ url: '/pages/energy/redeem' })
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
}

.tab {
  flex: 1;
  text-align: center;
  padding: 16rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
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

.order-merchant {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.order-status {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
}

.order-status.pending {
  background: #FFF3E0;
  color: #FF8800;
}

.order-status.verified {
  background: #E8F5E9;
  color: #4CAF50;
}

.order-status.expired,
.order-status.cancelled {
  background: #F5F5F5;
  color: #999;
}

.order-body {
  display: flex;
  padding: 20rpx;
}

.order-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #FFF3E0;
}

.order-image image {
  width: 100%;
  height: 100%;
}

.order-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
}

.order-info {
  flex: 1;
  margin-left: 20rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.order-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.order-cost {
  font-size: 26rpx;
  color: #FF8800;
  font-weight: 600;
}

.order-time {
  font-size: 22rpx;
  color: #999;
}

.order-footer {
  padding: 20rpx;
  background: #FAFAFA;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-expire {
  font-size: 22rpx;
  color: #999;
}

.order-code {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.code-label {
  font-size: 22rpx;
  color: #999;
}

.code-value {
  font-size: 28rpx;
  font-weight: 700;
  color: #FF8800;
  letter-spacing: 2rpx;
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
  display: block;
  margin-bottom: 30rpx;
}

.empty-btn {
  display: inline-block;
  padding: 20rpx 60rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  color: #FFFFFF;
  font-size: 28rpx;
  border-radius: 999rpx;
  border: none;
}

.detail-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.detail-card {
  width: 85%;
  max-height: 80vh;
  background: #FFFFFF;
  border-radius: 24rpx;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 2rpx solid #F0F0F0;
}

.detail-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.detail-close {
  font-size: 40rpx;
  color: #999;
}

.detail-content {
  padding: 20rpx 30rpx;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 2rpx solid #F5F5F5;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 26rpx;
  color: #999;
}

.detail-value {
  font-size: 26rpx;
  color: #333;
  text-align: right;
  max-width: 60%;
}

.qrcode-section {
  padding: 30rpx;
  background: #FAFAFA;
}

.qrcode-box {
  text-align: center;
  padding: 30rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  border: 4rpx dashed #FF8800;
}

.qrcode-code {
  font-size: 48rpx;
  font-weight: 800;
  color: #FF8800;
  letter-spacing: 8rpx;
  display: block;
}

.qrcode-hint {
  font-size: 24rpx;
  color: #999;
  margin-top: 16rpx;
  display: block;
}
</style>
