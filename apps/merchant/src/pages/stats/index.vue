<template>
  <view class="page">
    <!-- 时间筛选 -->
    <view class="time-filter">
      <view
        :class="['filter-item', { active: activeFilter === 'today' }]"
        @click="activeFilter = 'today'"
      >
        <text>今日</text>
      </view>
      <view
        :class="['filter-item', { active: activeFilter === 'week' }]"
        @click="activeFilter = 'week'"
      >
        <text>本周</text>
      </view>
      <view
        :class="['filter-item', { active: activeFilter === 'month' }]"
        @click="activeFilter = 'month'"
      >
        <text>本月</text>
      </view>
      <view
        :class="['filter-item', { active: activeFilter === 'custom' }]"
        @click="showDatePicker"
      >
        <text>自定义</text>
      </view>
    </view>

    <!-- 日期范围显示 -->
    <view class="date-range" v-if="activeFilter === 'custom' && customRange.start">
      <text>{{ customRange.start }} 至 {{ customRange.end }}</text>
    </view>

    <!-- 核心数据卡片 -->
    <view class="stats-card main">
      <view class="card-header">
        <text class="card-title">核销概览</text>
      </view>
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value">{{ stats.total_orders }}</text>
          <text class="stat-label">核销订单</text>
        </view>
        <view class="stat-item">
          <text class="stat-value energy">{{ stats.total_energy }}</text>
          <text class="stat-label">能量消耗</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.unique_students }}</text>
          <text class="stat-label">服务学员</text>
        </view>
      </view>
    </view>

    <!-- 订单状态分布 -->
    <view class="stats-card">
      <view class="card-header">
        <text class="card-title">订单状态</text>
      </view>
      <view class="status-list">
        <view class="status-item">
          <view class="status-info">
            <view class="status-dot pending"></view>
            <text class="status-name">待核销</text>
          </view>
          <view class="status-data">
            <text class="status-count">{{ stats.pending_count }}</text>
            <text class="status-percent">{{ getPercent(stats.pending_count) }}%</text>
          </view>
        </view>
        <view class="status-item">
          <view class="status-info">
            <view class="status-dot completed"></view>
            <text class="status-name">已核销</text>
          </view>
          <view class="status-data">
            <text class="status-count">{{ stats.completed_count }}</text>
            <text class="status-percent">{{ getPercent(stats.completed_count) }}%</text>
          </view>
        </view>
        <view class="status-item">
          <view class="status-info">
            <view class="status-dot cancelled"></view>
            <text class="status-name">已取消</text>
          </view>
          <view class="status-data">
            <text class="status-count">{{ stats.cancelled_count }}</text>
            <text class="status-percent">{{ getPercent(stats.cancelled_count) }}%</text>
          </view>
        </view>
        <view class="status-item">
          <view class="status-info">
            <view class="status-dot expired"></view>
            <text class="status-name">已过期</text>
          </view>
          <view class="status-data">
            <text class="status-count">{{ stats.expired_count }}</text>
            <text class="status-percent">{{ getPercent(stats.expired_count) }}%</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 趋势图表 -->
    <view class="stats-card">
      <view class="card-header">
        <text class="card-title">核销趋势</text>
      </view>
      <view class="chart-area">
        <view class="chart-bars">
          <view
            class="bar-item"
            v-for="(item, index) in trendData"
            :key="index"
          >
            <view class="bar-wrapper">
              <view
                class="bar"
                :style="{ height: getBarHeight(item.count) + '%' }"
              ></view>
            </view>
            <text class="bar-label">{{ item.label }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 热门商品 -->
    <view class="stats-card">
      <view class="card-header">
        <text class="card-title">热门商品</text>
      </view>
      <view class="product-list">
        <view
          class="product-item"
          v-for="(product, index) in topProducts"
          :key="product.id"
        >
          <view class="product-rank" :class="{ top: index < 3 }">
            <text>{{ index + 1 }}</text>
          </view>
          <view class="product-info">
            <text class="product-name">{{ product.name }}</text>
            <text class="product-count">{{ product.count }} 次核销</text>
          </view>
          <text class="product-energy">{{ product.energy }} 能量</text>
        </view>
      </view>
      <view class="empty-hint" v-if="topProducts.length === 0">
        <text>暂无数据</text>
      </view>
    </view>

    <!-- 底部安全区 -->
    <view class="safe-bottom"></view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { statsApi } from '@/api'

// 时间筛选
const activeFilter = ref<'today' | 'week' | 'month' | 'custom'>('today')
const customRange = ref({
  start: '',
  end: ''
})

// 统计数据
const stats = ref({
  total_orders: 0,
  total_energy: 0,
  unique_students: 0,
  pending_count: 0,
  completed_count: 0,
  cancelled_count: 0,
  expired_count: 0
})

// 趋势数据
const trendData = ref<{ label: string; count: number }[]>([])

// 热门商品
const topProducts = ref<{ id: number; name: string; count: number; energy: number }[]>([])

// 计算总订单数
const totalCount = computed(() => {
  return stats.value.pending_count +
    stats.value.completed_count +
    stats.value.cancelled_count +
    stats.value.expired_count
})

// 计算百分比
function getPercent(count: number): string {
  if (totalCount.value === 0) return '0'
  return ((count / totalCount.value) * 100).toFixed(1)
}

// 计算柱状图高度
function getBarHeight(count: number): number {
  const max = Math.max(...trendData.value.map(d => d.count), 1)
  return (count / max) * 100
}

// 监听筛选变化
watch(activeFilter, () => {
  if (activeFilter.value !== 'custom') {
    loadStats()
  }
})

// 显示日期选择器
function showDatePicker() {
  // 简化处理：使用 uni.showModal 模拟
  uni.showModal({
    title: '选择日期范围',
    content: '自定义日期范围功能开发中',
    showCancel: false
  })
}

// 加载统计数据
async function loadStats() {
  try {
    let res: any

    switch (activeFilter.value) {
      case 'today':
        res = await statsApi.getToday()
        break
      case 'week':
        res = await statsApi.getWeek()
        break
      case 'month':
        res = await statsApi.getMonth()
        break
      default:
        res = await statsApi.getSummary()
    }

    stats.value = {
      total_orders: res.total_orders || res.completed_count || 0,
      total_energy: res.total_energy || res.energy_consumed || 0,
      unique_students: res.unique_students || 0,
      pending_count: res.pending_count || 0,
      completed_count: res.completed_count || 0,
      cancelled_count: res.cancelled_count || 0,
      expired_count: res.expired_count || 0
    }

    // 加载趋势数据
    loadTrendData()

    // 加载热门商品
    loadTopProducts()
  } catch (error) {
    console.error('加载统计失败', error)
    // 使用模拟数据
    loadMockData()
  }
}

// 加载趋势数据
function loadTrendData() {
  // 根据筛选类型生成不同的趋势数据
  const data: { label: string; count: number }[] = []

  if (activeFilter.value === 'today') {
    // 今日按小时
    const hours = ['9时', '10时', '11时', '12时', '14时', '15时', '16时', '17时']
    hours.forEach(h => {
      data.push({ label: h, count: Math.floor(Math.random() * 10) })
    })
  } else if (activeFilter.value === 'week') {
    // 本周按天
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    days.forEach(d => {
      data.push({ label: d, count: Math.floor(Math.random() * 20) })
    })
  } else {
    // 本月按周
    const weeks = ['第1周', '第2周', '第3周', '第4周']
    weeks.forEach(w => {
      data.push({ label: w, count: Math.floor(Math.random() * 50) })
    })
  }

  trendData.value = data
}

// 加载热门商品
function loadTopProducts() {
  // 模拟数据
  topProducts.value = [
    { id: 1, name: '篮球体验课', count: 28, energy: 1400 },
    { id: 2, name: '运动水杯', count: 22, energy: 660 },
    { id: 3, name: '跳绳', count: 18, energy: 360 },
    { id: 4, name: '护腕', count: 15, energy: 225 },
    { id: 5, name: '运动毛巾', count: 12, energy: 300 }
  ]
}

// 加载模拟数据
function loadMockData() {
  if (activeFilter.value === 'today') {
    stats.value = {
      total_orders: 12,
      total_energy: 580,
      unique_students: 10,
      pending_count: 3,
      completed_count: 12,
      cancelled_count: 1,
      expired_count: 0
    }
  } else if (activeFilter.value === 'week') {
    stats.value = {
      total_orders: 45,
      total_energy: 2350,
      unique_students: 28,
      pending_count: 5,
      completed_count: 45,
      cancelled_count: 3,
      expired_count: 2
    }
  } else {
    stats.value = {
      total_orders: 186,
      total_energy: 9800,
      unique_students: 89,
      pending_count: 8,
      completed_count: 186,
      cancelled_count: 12,
      expired_count: 5
    }
  }

  loadTrendData()
  loadTopProducts()
}

// 初始化
onShow(() => {
  loadStats()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: 120rpx;
}

/* 时间筛选 */
.time-filter {
  display: flex;
  background: #FFFFFF;
  padding: 20rpx;
  gap: 16rpx;
}

.filter-item {
  flex: 1;
  height: 70rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #666;
  background: #F5F5F5;
}

.filter-item.active {
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #FFFFFF;
  font-weight: 600;
}

/* 日期范围 */
.date-range {
  background: #FFFFFF;
  padding: 16rpx 20rpx;
  text-align: center;
  font-size: 26rpx;
  color: #FF8800;
  border-top: 2rpx solid #F5F5F5;
}

/* 统计卡片 */
.stats-card {
  margin: 20rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.stats-card.main {
  background: linear-gradient(135deg, #FF8800, #FFB347);
}

.stats-card.main .card-title {
  color: #FFFFFF;
}

.card-header {
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #333;
}

/* 核心数据网格 */
.stats-grid {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 48rpx;
  font-weight: 800;
  color: #FFFFFF;
  display: block;
  line-height: 1.2;
}

.stat-value.energy {
  color: #FFE082;
}

.stat-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 8rpx;
}

/* 状态列表 */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx;
  background: #FAFAFA;
  border-radius: 12rpx;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.status-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}

.status-dot.pending {
  background: #FF8800;
}

.status-dot.completed {
  background: #4CAF50;
}

.status-dot.cancelled {
  background: #F44336;
}

.status-dot.expired {
  background: #9E9E9E;
}

.status-name {
  font-size: 28rpx;
  color: #333;
}

.status-data {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.status-count {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.status-percent {
  font-size: 24rpx;
  color: #999;
  min-width: 80rpx;
  text-align: right;
}

/* 图表区域 */
.chart-area {
  padding: 20rpx 0;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 300rpx;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.bar-wrapper {
  width: 40rpx;
  height: 240rpx;
  background: #F5F5F5;
  border-radius: 8rpx;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.bar {
  width: 100%;
  background: linear-gradient(180deg, #FF8800, #FFB347);
  border-radius: 8rpx 8rpx 0 0;
  transition: height 0.3s ease;
}

.bar-label {
  font-size: 22rpx;
  color: #999;
  margin-top: 12rpx;
}

/* 商品列表 */
.product-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: #FAFAFA;
  border-radius: 12rpx;
}

.product-rank {
  width: 48rpx;
  height: 48rpx;
  background: #E0E0E0;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
  color: #666;
}

.product-rank.top {
  background: linear-gradient(135deg, #FFB347, #FF8800);
  color: #FFFFFF;
}

.product-info {
  flex: 1;
}

.product-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  display: block;
}

.product-count {
  font-size: 24rpx;
  color: #999;
  margin-top: 4rpx;
}

.product-energy {
  font-size: 28rpx;
  font-weight: 600;
  color: #FF8800;
}

/* 空提示 */
.empty-hint {
  text-align: center;
  padding: 40rpx;
  font-size: 28rpx;
  color: #999;
}

/* 底部安全区 */
.safe-bottom {
  height: 40rpx;
}
</style>
