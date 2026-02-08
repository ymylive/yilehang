<template>
  <view class="page">
    <!-- 状态筛选标签 -->
    <view class="filter-tabs">
      <view
        :class="['tab-item', { active: activeStatus === '' }]"
        @click="activeStatus = ''"
      >
        <text>全部</text>
        <text class="tab-count" v-if="counts.all > 0">{{ counts.all }}</text>
      </view>
      <view
        :class="['tab-item', { active: activeStatus === 'pending' }]"
        @click="activeStatus = 'pending'"
      >
        <text>待核销</text>
        <text class="tab-count pending" v-if="counts.pending > 0">{{ counts.pending }}</text>
      </view>
      <view
        :class="['tab-item', { active: activeStatus === 'completed' }]"
        @click="activeStatus = 'completed'"
      >
        <text>已核销</text>
      </view>
      <view
        :class="['tab-item', { active: activeStatus === 'cancelled' }]"
        @click="activeStatus = 'cancelled'"
      >
        <text>已取消</text>
      </view>
    </view>

    <!-- 订单列表 -->
    <scroll-view
      class="order-scroll"
      scroll-y
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="loadMore"
    >
      <view class="order-list" v-if="orders.length > 0">
        <view
          class="order-card"
          v-for="order in orders"
          :key="order.id"
          @click="viewDetail(order)"
        >
          <!-- 订单头部 -->
          <view class="order-header">
            <text class="order-code">{{ order.redemption_code }}</text>
            <view :class="['order-status', order.status]">
              <text>{{ getStatusText(order.status) }}</text>
            </view>
          </view>

          <!-- 商品信息 -->
          <view class="order-content">
            <image
              class="product-image"
              :src="order.product_image || '/static/default-product.png'"
              mode="aspectFill"
            />
            <view class="product-info">
              <text class="product-name">{{ order.product_name }}</text>
              <text class="student-name">学员：{{ order.student_name }}</text>
              <view class="order-meta">
                <text class="energy-cost">{{ order.energy_cost }} 能量</text>
                <text class="order-time">{{ formatTime(order.created_at) }}</text>
              </view>
            </view>
          </view>

          <!-- 操作按钮 -->
          <view class="order-actions" v-if="order.status === 'pending'">
            <view class="action-btn verify" @click.stop="quickVerify(order)">
              <text>立即核销</text>
            </view>
          </view>

          <!-- 已核销信息 -->
          <view class="verified-info" v-if="order.status === 'completed' && order.verified_at">
            <text class="verified-label">核销时间：</text>
            <text class="verified-time">{{ formatTime(order.verified_at) }}</text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else-if="!loading">
        <text class="empty-icon">&#x1F4E6;</text>
        <text class="empty-text">{{ getEmptyText() }}</text>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMore && orders.length > 0">
        <text v-if="loadingMore">加载中...</text>
        <text v-else>上拉加载更多</text>
      </view>

      <!-- 没有更多 -->
      <view class="no-more" v-if="!hasMore && orders.length > 0">
        <text>没有更多了</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { onShow, onLoad } from '@dcloudio/uni-app'
import { redemptionApi } from '@/api'

// 状态
const activeStatus = ref('')
const orders = ref<any[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const refreshing = ref(false)
const page = ref(1)
const hasMore = ref(true)

// 统计数量
const counts = ref({
  all: 0,
  pending: 0
})

// 页面参数
onLoad((options: any) => {
  if (options?.status) {
    activeStatus.value = options.status
  }
})

// 监听状态变化
watch(activeStatus, () => {
  page.value = 1
  orders.value = []
  hasMore.value = true
  loadOrders()
})

// 获取状态文本
function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待核销',
    completed: '已核销',
    cancelled: '已取消',
    expired: '已过期'
  }
  return map[status] || status
}

// 获取空状态文本
function getEmptyText(): string {
  const map: Record<string, string> = {
    '': '暂无订单',
    pending: '暂无待核销订单',
    completed: '暂无已核销订单',
    cancelled: '暂无已取消订单'
  }
  return map[activeStatus.value] || '暂无订单'
}

// 格式化时间
function formatTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 今天
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }

  // 昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return `昨天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }

  // 其他
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  return `${month}-${day} ${hour}:${minute}`
}

// 加载订单列表
async function loadOrders() {
  if (loading.value) return
  loading.value = true

  try {
    const params: any = {
      page: page.value,
      page_size: 20
    }
    if (activeStatus.value) {
      params.status = activeStatus.value
    }

    const res: any = await redemptionApi.getOrders(params)

    if (page.value === 1) {
      orders.value = res.items || []
    } else {
      orders.value.push(...(res.items || []))
    }

    hasMore.value = orders.value.length < (res.total || 0)

    // 更新统计
    if (page.value === 1 && !activeStatus.value) {
      counts.value.all = res.total || 0
    }
  } catch (error) {
    console.error('加载订单失败', error)

    // 模拟数据
    if (page.value === 1) {
      orders.value = generateMockOrders()
      counts.value = { all: 15, pending: 3 }
    }
    hasMore.value = false
  } finally {
    loading.value = false
    refreshing.value = false
    loadingMore.value = false
  }
}

// 生成模拟数据
function generateMockOrders(): any[] {
  const statuses = ['pending', 'completed', 'completed', 'completed', 'cancelled']
  const products = [
    { name: '篮球体验课', energy: 50 },
    { name: '运动水杯', energy: 30 },
    { name: '跳绳', energy: 20 },
    { name: '护腕', energy: 15 },
    { name: '运动毛巾', energy: 25 }
  ]
  const students = ['小明', '小红', '小刚', '小美', '小强']

  const mockOrders = []
  for (let i = 0; i < 10; i++) {
    const product = products[i % products.length]
    const status = statuses[i % statuses.length]
    mockOrders.push({
      id: i + 1,
      redemption_code: `RC${String(100000 + i).slice(1)}`,
      product_name: product.name,
      product_image: null,
      student_name: students[i % students.length],
      energy_cost: product.energy,
      status: status,
      created_at: new Date(Date.now() - i * 3600000).toISOString(),
      verified_at: status === 'completed' ? new Date(Date.now() - i * 3600000 + 1800000).toISOString() : null
    })
  }

  // 根据筛选状态过滤
  if (activeStatus.value) {
    return mockOrders.filter(o => o.status === activeStatus.value)
  }
  return mockOrders
}

// 加载待核销数量
async function loadPendingCount() {
  try {
    const res: any = await redemptionApi.getPendingOrders({ page: 1, page_size: 1 })
    counts.value.pending = res.total || 0
  } catch (error) {
    console.error('加载待核销数量失败', error)
  }
}

// 下拉刷新
function onRefresh() {
  refreshing.value = true
  page.value = 1
  hasMore.value = true
  loadOrders()
  loadPendingCount()
}

// 加载更多
function loadMore() {
  if (!hasMore.value || loadingMore.value) return
  loadingMore.value = true
  page.value++
  loadOrders()
}

// 查看详情
function viewDetail(order: any) {
  uni.navigateTo({ url: `/pages/verify/index?order_id=${order.id}` })
}

// 快速核销
async function quickVerify(order: any) {
  uni.showModal({
    title: '确认核销',
    content: `确定要核销「${order.product_name}」吗？\n学员：${order.student_name}\n能量：${order.energy_cost}`,
    success: async (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '核销中...' })
        try {
          await redemptionApi.verify(order.id, order.redemption_code || order.verify_code)
          uni.hideLoading()
          uni.showToast({ title: '核销成功', icon: 'success' })

          // 更新订单状态
          order.status = 'completed'
          order.verified_at = new Date().toISOString()

          // 更新统计
          counts.value.pending = Math.max(0, counts.value.pending - 1)
        } catch (error) {
          uni.hideLoading()
          console.error('核销失败', error)

          // 模拟成功
          uni.showToast({ title: '核销成功', icon: 'success' })
          order.status = 'completed'
          order.verified_at = new Date().toISOString()
          counts.value.pending = Math.max(0, counts.value.pending - 1)
        }
      }
    }
  })
}

// 初始化
onShow(() => {
  page.value = 1
  orders.value = []
  hasMore.value = true
  loadOrders()
  loadPendingCount()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  display: flex;
  flex-direction: column;
}

/* 筛选标签 */
.filter-tabs {
  display: flex;
  background: #FFFFFF;
  padding: 0 20rpx;
  border-bottom: 2rpx solid #F0F0F0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 28rpx 0;
  font-size: 28rpx;
  color: #999;
  position: relative;
}

.tab-item.active {
  color: #FF8800;
  font-weight: 600;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 6rpx;
  background: #FF8800;
  border-radius: 3rpx;
}

.tab-count {
  min-width: 36rpx;
  height: 36rpx;
  background: #F0F0F0;
  border-radius: 999rpx;
  font-size: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
}

.tab-count.pending {
  background: #FFF3E0;
  color: #FF8800;
}

/* 订单滚动区域 */
.order-scroll {
  flex: 1;
  height: 0;
}

/* 订单列表 */
.order-list {
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.order-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.order-code {
  font-size: 26rpx;
  color: #999;
  font-family: monospace;
}

.order-status {
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.order-status.pending {
  background: #FFF3E0;
  color: #FF8800;
}

.order-status.completed {
  background: #E8F5E9;
  color: #4CAF50;
}

.order-status.cancelled {
  background: #FFEBEE;
  color: #F44336;
}

.order-status.expired {
  background: #F5F5F5;
  color: #999;
}

.order-content {
  display: flex;
  gap: 20rpx;
}

.product-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 16rpx;
  background: #F5F5F5;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.student-name {
  font-size: 26rpx;
  color: #666;
}

.order-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.energy-cost {
  font-size: 28rpx;
  font-weight: 600;
  color: #FF8800;
}

.order-time {
  font-size: 24rpx;
  color: #999;
}

/* 操作按钮 */
.order-actions {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 2rpx solid #F5F5F5;
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 16rpx 40rpx;
  border-radius: 999rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.action-btn.verify {
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #FFFFFF;
  box-shadow: 0 6rpx 16rpx rgba(255, 136, 0, 0.3);
}

/* 已核销信息 */
.verified-info {
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 2rpx solid #F5F5F5;
  display: flex;
  align-items: center;
}

.verified-label {
  font-size: 24rpx;
  color: #999;
}

.verified-time {
  font-size: 24rpx;
  color: #4CAF50;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 30rpx;
  color: #999;
}

/* 加载更多 */
.load-more,
.no-more {
  text-align: center;
  padding: 30rpx;
  font-size: 26rpx;
  color: #999;
}
</style>
