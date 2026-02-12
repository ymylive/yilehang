<template>
  <view class="page">
    <!-- 基本信息 -->
    <view class="info-card">
      <view class="info-header">
        <text class="title">体测详情</text>
        <text class="date">{{ formatDate(testData?.test_date) }}</text>
      </view>
      <view class="info-body">
        <view class="student-info">
          <image class="avatar" :src="student?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <view class="info">
            <text class="name">{{ student?.name || '学员' }}</text>
            <text class="no">学号: {{ student?.student_no || '-' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 身体指标 -->
    <view class="section">
      <view class="section-title">身体指标</view>
      <view class="metrics-grid">
        <view class="metric-card">
          <text class="label">身高</text>
          <text class="value">{{ testData?.height || '-' }}<text class="unit">cm</text></text>
          <view class="change" :class="getChangeClass(heightChange)">
            {{ formatChange(heightChange, 'cm') }}
          </view>
        </view>
        <view class="metric-card">
          <text class="label">体重</text>
          <text class="value">{{ testData?.weight || '-' }}<text class="unit">kg</text></text>
          <view class="change" :class="getChangeClass(weightChange)">
            {{ formatChange(weightChange, 'kg') }}
          </view>
        </view>
        <view class="metric-card">
          <text class="label">BMI</text>
          <text class="value">{{ testData?.bmi || '-' }}</text>
          <view class="change" :class="getChangeClass(bmiChange)">
            {{ formatChange(bmiChange) }}
          </view>
        </view>
      </view>
    </view>

    <!-- 体能指标 -->
    <view class="section">
      <view class="section-title">体能指标</view>
      <view class="metrics-list">
        <view class="metric-item">
          <view class="metric-info">
            <text class="label">肺活量</text>
            <text class="value">{{ testData?.vital_capacity || '-' }} ml</text>
          </view>
          <view class="progress-bar">
            <view class="progress" :style="{ width: getProgressWidth(testData?.vital_capacity, 3000) }"></view>
          </view>
        </view>
        <view class="metric-item">
          <view class="metric-info">
            <text class="label">50米跑</text>
            <text class="value">{{ testData?.sprint_50m || '-' }} 秒</text>
          </view>
          <view class="progress-bar">
            <view class="progress" :style="{ width: getSprintProgress(testData?.sprint_50m) }"></view>
          </view>
        </view>
        <view class="metric-item">
          <view class="metric-info">
            <text class="label">立定跳远</text>
            <text class="value">{{ testData?.standing_jump || '-' }} cm</text>
          </view>
          <view class="progress-bar">
            <view class="progress" :style="{ width: getProgressWidth(testData?.standing_jump, 200) }"></view>
          </view>
        </view>
        <view class="metric-item">
          <view class="metric-info">
            <text class="label">跳绳(1分钟)</text>
            <text class="value">{{ testData?.jump_rope || '-' }} 个</text>
          </view>
          <view class="progress-bar">
            <view class="progress" :style="{ width: getProgressWidth(testData?.jump_rope, 180) }"></view>
          </view>
        </view>
        <view class="metric-item">
          <view class="metric-info">
            <text class="label">坐位体前屈</text>
            <text class="value">{{ testData?.sit_and_reach || '-' }} cm</text>
          </view>
          <view class="progress-bar">
            <view class="progress" :style="{ width: getProgressWidth(testData?.sit_and_reach, 25) }"></view>
          </view>
        </view>
        <view class="metric-item">
          <view class="metric-info">
            <text class="label">仰卧起坐(1分钟)</text>
            <text class="value">{{ testData?.sit_ups || '-' }} 个</text>
          </view>
          <view class="progress-bar">
            <view class="progress" :style="{ width: getProgressWidth(testData?.sit_ups, 50) }"></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 与上次对比 -->
    <view class="section" v-if="previousTest">
      <view class="section-title">与上次对比</view>
      <view class="compare-card">
        <view class="compare-header">
          <text class="current">本次 ({{ formatDate(testData?.test_date) }})</text>
          <text class="vs">VS</text>
          <text class="previous">上次 ({{ formatDate(previousTest?.test_date) }})</text>
        </view>
        <view class="compare-list">
          <view class="compare-item" v-for="item in compareItems" :key="item.key">
            <text class="label">{{ item.label }}</text>
            <view class="values">
              <text class="current-value">{{ testData?.[item.key] || '-' }}</text>
              <text class="arrow" :class="getCompareClass(testData?.[item.key], previousTest?.[item.key], item.reverse)">
                {{ getCompareArrow(testData?.[item.key], previousTest?.[item.key]) }}
              </text>
              <text class="previous-value">{{ previousTest?.[item.key] || '-' }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 教练评语 -->
    <view class="section" v-if="testData?.coach_comment">
      <view class="section-title">教练评语</view>
      <view class="comment-card">
        <text class="comment">{{ testData.coach_comment }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { growthApi, studentApi } from '@/api'

const userStore = useUserStore()

const testData = ref<any>(null)
const previousTest = ref<any>(null)
const student = ref<any>(null)

const compareItems = [
  { key: 'height', label: '身高(cm)', reverse: false },
  { key: 'weight', label: '体重(kg)', reverse: true },
  { key: 'vital_capacity', label: '肺活量(ml)', reverse: false },
  { key: 'sprint_50m', label: '50米跑(秒)', reverse: true },
  { key: 'standing_jump', label: '立定跳远(cm)', reverse: false },
  { key: 'jump_rope', label: '跳绳(个)', reverse: false },
]

const heightChange = computed(() => {
  if (!testData.value || !previousTest.value) return null
  return testData.value.height - previousTest.value.height
})

const weightChange = computed(() => {
  if (!testData.value || !previousTest.value) return null
  return testData.value.weight - previousTest.value.weight
})

const bmiChange = computed(() => {
  if (!testData.value || !previousTest.value) return null
  return testData.value.bmi - previousTest.value.bmi
})

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const testId = (currentPage as any).options?.id

  if (!testId) {
    uni.showToast({ title: '参数错误', icon: 'none' })
    return
  }

  await loadData(parseInt(testId))
})

async function loadData(testId: number) {
  if (!userStore.currentStudent) {
    uni.showToast({ title: '请先选择学员', icon: 'none' })
    return
  }

  try {
    // 获取学员信息
    student.value = await studentApi.get(userStore.currentStudent.id)

    // 获取体测历史
    const history: any = await growthApi.getFitnessHistory(userStore.currentStudent.id, 0, 20)
    const items = Array.isArray(history) ? history : (Array.isArray(history?.items) ? history.items : [])

    // 找到当前记录和上一条记录
    const currentIndex = items.findIndex((item: any) => item.id === testId)
    if (currentIndex >= 0) {
      testData.value = items[currentIndex]
      if (currentIndex < items.length - 1) {
        previousTest.value = items[currentIndex + 1]
      }
    } else if (items.length > 0) {
      // 如果找不到指定ID，显示最新的
      testData.value = items[0]
      if (items.length > 1) {
        previousTest.value = items[1]
      }
    }
  } catch (error) {
    console.error('加载体测详情失败', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function formatDate(dateStr: string | undefined) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

function getChangeClass(change: number | null) {
  if (change === null) return ''
  if (change > 0) return 'up'
  if (change < 0) return 'down'
  return 'same'
}

function formatChange(change: number | null, unit = '') {
  if (change === null) return '暂无对比'
  if (change === 0) return '持平'
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}${unit}`
}

function getProgressWidth(value: number | undefined, max: number) {
  if (!value) return '0%'
  return `${Math.min(100, (value / max) * 100)}%`
}

function getSprintProgress(time: number | undefined) {
  if (!time) return '0%'
  // 50米跑，时间越短越好，假设最佳7秒，最差15秒
  const progress = Math.max(0, Math.min(100, ((15 - time) / 8) * 100))
  return `${progress}%`
}

function getCompareClass(current: number | undefined, previous: number | undefined, reverse: boolean) {
  if (!current || !previous) return ''
  const diff = current - previous
  if (diff === 0) return 'same'
  if (reverse) {
    return diff < 0 ? 'better' : 'worse'
  }
  return diff > 0 ? 'better' : 'worse'
}

function getCompareArrow(current: number | undefined, previous: number | undefined) {
  if (!current || !previous) return '-'
  if (current > previous) return '↑'
  if (current < previous) return '↓'
  return '='
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

.info-card {
  background: linear-gradient(135deg, #FF8800, #FFB347);
  margin: 20rpx;
  border-radius: 16rpx;
  color: #fff;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.2);
}

.info-header .title {
  font-size: 32rpx;
  font-weight: 600;
}

.info-header .date {
  font-size: 26rpx;
  opacity: 0.9;
}

.info-body {
  padding: 24rpx 30rpx;
}

.student-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 2rpx solid rgba(255, 255, 255, 0.5);
}

.student-info .info {
  margin-left: 20rpx;
}

.student-info .name {
  font-size: 30rpx;
  font-weight: 600;
  display: block;
}

.student-info .no {
  font-size: 24rpx;
  opacity: 0.9;
  margin-top: 4rpx;
}

.section {
  margin: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx 30rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.metric-card {
  background: #f8f8f8;
  border-radius: 12rpx;
  padding: 20rpx;
  text-align: center;
}

.metric-card .label {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.metric-card .value {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.metric-card .unit {
  font-size: 22rpx;
  font-weight: normal;
  color: #666;
}

.metric-card .change {
  font-size: 22rpx;
  margin-top: 8rpx;
}

.change.up {
  color: #4CAF50;
}

.change.down {
  color: #F44336;
}

.change.same {
  color: #999;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.metric-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-info .label {
  font-size: 26rpx;
  color: #666;
}

.metric-info .value {
  font-size: 26rpx;
  color: #333;
  font-weight: 600;
}

.progress-bar {
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #FF8800, #FFB347);
  border-radius: 6rpx;
  transition: width 0.3s ease;
}

.compare-card {
  background: #f8f8f8;
  border-radius: 12rpx;
  overflow: hidden;
}

.compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
}

.compare-header .current,
.compare-header .previous {
  font-size: 24rpx;
  color: #666;
}

.compare-header .vs {
  font-size: 24rpx;
  color: #FF8800;
  font-weight: 600;
}

.compare-list {
  padding: 20rpx;
}

.compare-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.compare-item:last-child {
  border-bottom: none;
}

.compare-item .label {
  font-size: 26rpx;
  color: #666;
}

.compare-item .values {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.current-value,
.previous-value {
  font-size: 26rpx;
  color: #333;
  font-weight: 600;
}

.arrow {
  font-size: 24rpx;
}

.arrow.better {
  color: #4CAF50;
}

.arrow.worse {
  color: #F44336;
}

.arrow.same {
  color: #999;
}

.comment-card {
  background: #f8f8f8;
  border-radius: 12rpx;
  padding: 20rpx;
}

.comment {
  font-size: 26rpx;
  color: #666;
  line-height: 1.8;
}
</style>
