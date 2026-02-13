<template>
  <view class="page">
    <!-- 筛选栏 -->
    <view class="filter-bar">
      <picker mode="date" :value="startDate" @change="onStartDateChange">
        <view class="date-picker">
          <text>{{ startDate || '开始日期' }}</text>
          <image :src="chevronDownIcon" class="picker-icon" mode="aspectFit" />
        </view>
      </picker>
      <text class="separator">至</text>
      <picker mode="date" :value="endDate" @change="onEndDateChange">
        <view class="date-picker">
          <text>{{ endDate || '结束日期' }}</text>
          <image :src="chevronDownIcon" class="picker-icon" mode="aspectFit" />
        </view>
      </picker>
      <view class="reset-btn" @click="resetFilter">重置</view>
    </view>

    <!-- 体测列表 -->
    <view class="test-list">
      <view
        v-for="test in fitnessTests"
        :key="test.id"
        class="test-card"
        @click="viewDetail(test)"
      >
        <view class="test-header">
          <text class="test-date">{{ formatDate(test.test_date) }}</text>
          <view class="test-badge" v-if="test.is_latest">最新</view>
        </view>
        <view class="test-body">
          <view class="metric-row">
            <view class="metric">
              <text class="label">身高</text>
              <text class="value">{{ test.height || '-' }}<text class="unit">cm</text></text>
            </view>
            <view class="metric">
              <text class="label">体重</text>
              <text class="value">{{ test.weight || '-' }}<text class="unit">kg</text></text>
            </view>
            <view class="metric">
              <text class="label">BMI</text>
              <text class="value">{{ test.bmi || '-' }}</text>
            </view>
          </view>
          <view class="metric-row">
            <view class="metric">
              <text class="label">肺活量</text>
              <text class="value">{{ test.vital_capacity || '-' }}<text class="unit">ml</text></text>
            </view>
            <view class="metric">
              <text class="label">50米跑</text>
              <text class="value">{{ test.sprint_50m || '-' }}<text class="unit">秒</text></text>
            </view>
            <view class="metric">
              <text class="label">跳绳</text>
              <text class="value">{{ test.jump_rope || '-' }}<text class="unit">个/分</text></text>
            </view>
          </view>
        </view>
        <view class="test-footer">
          <view class="view-detail">
            <text>查看详情</text>
            <image :src="detailChevronRightIcon" class="detail-arrow-icon" mode="aspectFit" />
          </view>
        </view>
      </view>

      <view v-if="fitnessTests.length === 0 && !loading" class="empty-state">
        <image :src="emptyIcon" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无体测记录</text>
      </view>

      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>

      <view v-if="hasMore && !loading" class="load-more" @click="loadMore">
        <text>加载更多</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { growthApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

const userStore = useUserStore()

const fitnessTests = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const skip = ref(0)
const limit = 10

const startDate = ref('')
const endDate = ref('')
const emptyIcon = getSemanticIcon('growth-history-empty')
const chevronDownIcon = getSemanticIcon('icon-chevron-down')
const detailChevronRightIcon = getSemanticIcon('icon-growth-chevron-right')

const hasMore = computed(() => fitnessTests.value.length < total.value)

onMounted(() => {
  loadData()
})

async function loadData(reset = true) {
  if (!userStore.currentStudent) {
    uni.showToast({ title: '请先选择学员', icon: 'none' })
    return
  }

  if (reset) {
    skip.value = 0
    fitnessTests.value = []
  }

  loading.value = true
  try {
    const res = await growthApi.getFitnessHistory(
      userStore.currentStudent.id,
      skip.value,
      limit
    )

    // API 返回数组或对象
    const items = Array.isArray(res) ? res : (Array.isArray((res as any)?.items) ? (res as any).items : [])
    total.value = Array.isArray(res) ? items.length : Number((res as any)?.total || items.length)

    // 标记最新记录
    if (reset && items.length > 0) {
      items[0].is_latest = true
    }

    if (reset) {
      fitnessTests.value = items
    } else {
      fitnessTests.value.push(...items)
    }
  } catch (error) {
    console.error('加载体测历史失败', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function loadMore() {
  skip.value += limit
  loadData(false)
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

function viewDetail(test: any) {
  uni.navigateTo({ url: `/pages/growth/detail?id=${test.id}` })
}

function onStartDateChange(e: any) {
  startDate.value = e.detail.value
  loadData()
}

function onEndDateChange(e: any) {
  endDate.value = e.detail.value
  loadData()
}

function resetFilter() {
  startDate.value = ''
  endDate.value = ''
  loadData()
}

// 下拉刷新
onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

.filter-bar {
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
  background: #fff;
  gap: 16rpx;
}

.date-picker {
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #333;
}

.date-picker .picker-icon {
  margin-left: 8rpx;
  width: 20rpx;
  height: 20rpx;
}

.separator {
  font-size: 26rpx;
  color: #666;
}

.reset-btn {
  margin-left: auto;
  padding: 16rpx 24rpx;
  font-size: 26rpx;
  color: #FF8800;
}

.test-list {
  padding: 20rpx;
}

.test-card {
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.test-date {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.test-badge {
  padding: 6rpx 16rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #fff;
  font-size: 22rpx;
  border-radius: 20rpx;
}

.test-body {
  padding: 24rpx 30rpx;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.metric-row:last-child {
  margin-bottom: 0;
}

.metric {
  flex: 1;
  text-align: center;
}

.metric .label {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.metric .value {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.metric .unit {
  font-size: 22rpx;
  font-weight: normal;
  color: #666;
  margin-left: 4rpx;
}

.test-footer {
  padding: 20rpx 30rpx;
  border-top: 1rpx solid #f0f0f0;
  text-align: right;
}

.view-detail {
  font-size: 26rpx;
  color: #FF8800;
  display: inline-flex;
  align-items: center;
  gap: 4rpx;
}

.detail-arrow-icon {
  width: 20rpx;
  height: 20rpx;
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
}

.empty-image {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  color: #999;
  font-size: 26rpx;
}

.loading-state {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
}

.load-more {
  text-align: center;
  padding: 30rpx 0;
  color: #FF8800;
  font-size: 26rpx;
}
</style>
