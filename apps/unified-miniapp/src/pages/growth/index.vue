<template>
  <view class="page">
    <!-- 学员信息 -->
    <view class="profile-card">
      <image class="avatar" :src="student?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
      <view class="info">
        <text class="name">{{ student?.name || '小朋友' }}</text>
        <text class="no">学号: {{ student?.student_no || '-' }}</text>
      </view>
    </view>

    <!-- 体测雷达 -->
    <view class="section">
      <view class="section-header">
        <text class="title">体测雷达</text>
        <text class="date" v-if="latestTest">{{ formatDate(latestTest.test_date) }}</text>
      </view>
      <view class="radar-container">
        <canvas canvas-id="radarChart" class="radar-canvas" />
      </view>
      <view class="radar-legend">
        <view class="legend-item" v-for="item in radarItems" :key="item.key">
          <view class="dot" :style="{ background: item.color }"></view>
          <text class="label">{{ item.label }}</text>
          <text class="value">{{ growthData?.current_radar?.[item.key] || 0 }}</text>
        </view>
      </view>
    </view>

    <!-- 体测记录 -->
    <view class="section">
      <view class="section-header">
        <text class="title">体测记录</text>
        <text class="more" @click="viewAllTests">查看全部 ></text>
      </view>
      <view class="test-list" v-if="fitnessTests.length">
        <view class="test-item" v-for="test in fitnessTests" :key="test.id" @click="viewTestDetail(test)">
          <view class="test-date">{{ formatDate(test.test_date) }}</view>
          <view class="test-info">
            <text class="bmi">BMI: {{ test.bmi || '-' }}</text>
            <text class="hw">身高: {{ test.height }}cm / 体重: {{ test.weight }}kg</text>
          </view>
          <view class="arrow">></view>
        </view>
      </view>
      <view class="empty" v-else>
        <text>暂无体测记录</text>
      </view>
    </view>

    <!-- 成长统计 -->
    <view class="section">
      <view class="section-header">
        <text class="title">成长统计</text>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="value">{{ growthData?.total_training_sessions || 0 }}</text>
          <text class="label">训练次数</text>
        </view>
        <view class="stat-card">
          <text class="value">{{ formatHours(growthData?.total_training_hours || 0) }}</text>
          <text class="label">训练时长</text>
        </view>
        <view class="stat-card">
          <text class="value">{{ growthData?.fitness_tests_count || 0 }}</text>
          <text class="label">体测次数</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { studentApi, growthApi } from '@/api'

const userStore = useUserStore()

const student = ref<any>(null)
const growthData = ref<any>(null)
const fitnessTests = ref<any[]>([])
const latestTest = ref<any>(null)

const radarItems = [
  { key: 'speed', label: '速度', color: '#FF6384' },
  { key: 'agility', label: '敏捷', color: '#36A2EB' },
  { key: 'endurance', label: '耐力', color: '#FFCE56' },
  { key: 'strength', label: '力量', color: '#4BC0C0' },
  { key: 'flexibility', label: '柔韧', color: '#9966FF' }
]

onMounted(async () => {
  await loadData()
  await nextTick()
  drawRadarChart()
})

async function loadData() {
  if (!userStore.currentStudent) return

  const studentId = userStore.currentStudent.id

  try {
    student.value = await studentApi.get(studentId)
    growthData.value = await studentApi.getGrowth(studentId)
    fitnessTests.value = await growthApi.getFitnessHistory(studentId, 0, 5)
    if (fitnessTests.value.length) {
      latestTest.value = fitnessTests.value[0]
    }
  } catch (error) {
    console.error('加载成长数据失败', error)
  }
}

function drawRadarChart() {
  const ctx = uni.createCanvasContext('radarChart')
  const centerX = 150
  const centerY = 150
  const radius = 100
  const sides = 5
  const angleStep = (Math.PI * 2) / sides

  ctx.setStrokeStyle('#e0e0e0')
  ctx.setLineWidth(1)

  for (let level = 1; level <= 5; level++) {
    const r = (radius / 5) * level
    ctx.beginPath()
    for (let i = 0; i <= sides; i++) {
      const angle = i * angleStep - Math.PI / 2
      const x = centerX + r * Math.cos(angle)
      const y = centerY + r * Math.sin(angle)
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    }
    ctx.closePath()
    ctx.stroke()
  }

  for (let i = 0; i < sides; i++) {
    const angle = i * angleStep - Math.PI / 2
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.lineTo(centerX + radius * Math.cos(angle), centerY + radius * Math.sin(angle))
    ctx.stroke()
  }

  const data = growthData.value?.current_radar || {}
  const values = [
    (data.speed || 0) / 100,
    (data.agility || 0) / 100,
    (data.endurance || 0) / 100,
    (data.strength || 0) / 100,
    (data.flexibility || 0) / 100
  ]

  ctx.beginPath()
  ctx.setFillStyle('rgba(76, 175, 80, 0.3)')
  ctx.setStrokeStyle('#FF8800')
  ctx.setLineWidth(2)

  for (let i = 0; i <= sides; i++) {
    const idx = i % sides
    const angle = idx * angleStep - Math.PI / 2
    const r = radius * values[idx]
    const x = centerX + r * Math.cos(angle)
    const y = centerY + r * Math.sin(angle)
    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  }
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  ctx.setFillStyle('#FF8800')
  for (let i = 0; i < sides; i++) {
    const angle = i * angleStep - Math.PI / 2
    const r = radius * values[i]
    const x = centerX + r * Math.cos(angle)
    const y = centerY + r * Math.sin(angle)
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()
  }

  ctx.setFillStyle('#333')
  ctx.setFontSize(12)
  const labels = radarItems.map(item => item.label)
  for (let i = 0; i < sides; i++) {
    const angle = i * angleStep - Math.PI / 2
    const x = centerX + (radius + 20) * Math.cos(angle)
    const y = centerY + (radius + 20) * Math.sin(angle)
    ctx.setTextAlign('center')
    ctx.fillText(labels[i], x, y + 4)
  }

  ctx.draw()
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

function formatHours(hours: number) {
  if (hours < 1) {
    return `${Math.round(hours * 60)}分钟`
  }
  return `${hours.toFixed(1)}小时`
}

function viewAllTests() {
  uni.navigateTo({ url: '/pages/growth/history' })
}

function viewTestDetail(test: any) {
  uni.navigateTo({ url: `/pages/growth/detail?id=${test.id}` })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: 120rpx;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 40rpx 30rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #fff;
  animation: fadeUp 0.4s ease-out;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.5);
}

.info {
  margin-left: 30rpx;
}

.name {
  font-size: 40rpx;
  font-weight: bold;
  display: block;
}

.no {
  font-size: 26rpx;
  opacity: 0.9;
  margin-top: 8rpx;
}

.section {
  margin: 20rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  animation: fadeUp 0.4s ease-out;

  &:nth-of-type(1) { animation-delay: 0.1s; animation-fill-mode: both; }
  &:nth-of-type(2) { animation-delay: 0.15s; animation-fill-mode: both; }
  &:nth-of-type(3) { animation-delay: 0.2s; animation-fill-mode: both; }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-header .title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.section-header .date,
.section-header .more {
  font-size: 24rpx;
  color: #999;
}

.radar-container {
  display: flex;
  justify-content: center;
  padding: 20rpx 0;
}

.radar-canvas {
  width: 300px;
  height: 300px;
}

.radar-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20rpx;
  margin-top: 20rpx;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #666;
}

.legend-item .dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
}

.test-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.test-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  border-radius: 16rpx;
  background: #FFF7ED;
  transition: all 0.2s ease;
}

.test-item:active {
  transform: scale(0.99);
}

.test-date {
  font-size: 26rpx;
  color: #333;
  font-weight: 600;
}

.test-info {
  flex: 1;
  margin-left: 20rpx;
  color: #666;
  font-size: 24rpx;
}

.arrow {
  font-size: 28rpx;
  color: #bbb;
}

.empty {
  text-align: center;
  color: #999;
  padding: 20rpx 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.stat-card {
  background: #FFF7ED;
  border-radius: 16rpx;
  padding: 20rpx;
  text-align: center;
}

.stat-card .value {
  font-size: 32rpx;
  font-weight: bold;
  color: #FF8800;
}

.stat-card .label {
  font-size: 24rpx;
  color: #666;
  margin-top: 8rpx;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
