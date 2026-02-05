<template>
  <view class="page">
    <!-- 瀛﹀憳淇℃伅鍗＄墖 -->
    <view class="profile-card">
      <image class="avatar" :src="student?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
      <view class="info">
        <text class="name">{{ student?.name || '鏈粦瀹氬鍛? }}</text>
        <text class="no">瀛﹀彿: {{ student?.student_no || '-' }}</text>
      </view>
    </view>

    <!-- 浜旂淮闆疯揪鍥?-->
    <view class="section">
      <view class="section-header">
        <text class="title">杩愬姩鑳藉姏璇勪及</text>
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

    <!-- 浣撴祴鍘嗗彶 -->
    <view class="section">
      <view class="section-header">
        <text class="title">浣撴祴璁板綍</text>
        <text class="more" @click="viewAllTests">鏌ョ湅鍏ㄩ儴 ></text>
      </view>
      <view class="test-list" v-if="fitnessTests.length">
        <view class="test-item" v-for="test in fitnessTests" :key="test.id" @click="viewTestDetail(test)">
          <view class="test-date">{{ formatDate(test.test_date) }}</view>
          <view class="test-info">
            <text class="bmi">BMI: {{ test.bmi || '-' }}</text>
            <text class="hw">韬珮: {{ test.height }}cm / 浣撻噸: {{ test.weight }}kg</text>
          </view>
          <view class="arrow">></view>
        </view>
      </view>
      <view class="empty" v-else>
        <text>鏆傛棤浣撴祴璁板綍</text>
      </view>
    </view>

    <!-- 璁粌缁熻 -->
    <view class="section">
      <view class="section-header">
        <text class="title">璁粌缁熻</text>
      </view>
      <view class="stats-grid">
        <view class="stat-card">
          <text class="value">{{ growthData?.total_training_sessions || 0 }}</text>
          <text class="label">鎬昏缁冩鏁?/text>
        </view>
        <view class="stat-card">
          <text class="value">{{ formatHours(growthData?.total_training_hours || 0) }}</text>
          <text class="label">鎬昏缁冩椂闀?/text>
        </view>
        <view class="stat-card">
          <text class="value">{{ growthData?.fitness_tests_count || 0 }}</text>
          <text class="label">浣撴祴娆℃暟</text>
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

// 闆疯揪鍥鹃厤缃?const radarItems = [
  { key: 'speed', label: '閫熷害', color: '#FF6384' },
  { key: 'agility', label: '鐏垫晱', color: '#36A2EB' },
  { key: 'endurance', label: '鑰愬姏', color: '#FFCE56' },
  { key: 'strength', label: '鍔涢噺', color: '#4BC0C0' },
  { key: 'flexibility', label: '鏌旈煣', color: '#9966FF' }
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
    // 鍔犺浇瀛﹀憳淇℃伅
    student.value = await studentApi.get(studentId)

    // 鍔犺浇鎴愰暱妗ｆ
    growthData.value = await studentApi.getGrowth(studentId)

    // 鍔犺浇浣撴祴鍘嗗彶
    fitnessTests.value = await growthApi.getFitnessHistory(studentId, 0, 5)
    if (fitnessTests.value.length) {
      latestTest.value = fitnessTests.value[0]
    }
  } catch (error) {
    console.error('鍔犺浇鏁版嵁澶辫触', error)
  }
}

// 缁樺埗闆疯揪鍥?function drawRadarChart() {
  const ctx = uni.createCanvasContext('radarChart')
  const centerX = 150
  const centerY = 150
  const radius = 100
  const sides = 5
  const angleStep = (Math.PI * 2) / sides

  // 缁樺埗鑳屾櫙缃戞牸
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

  // 缁樺埗杞寸嚎
  for (let i = 0; i < sides; i++) {
    const angle = i * angleStep - Math.PI / 2
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.lineTo(centerX + radius * Math.cos(angle), centerY + radius * Math.sin(angle))
    ctx.stroke()
  }

  // 缁樺埗鏁版嵁鍖哄煙
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

  // 缁樺埗鏁版嵁鐐?  ctx.setFillStyle('#FF8800')
  for (let i = 0; i < sides; i++) {
    const angle = i * angleStep - Math.PI / 2
    const r = radius * values[i]
    const x = centerX + r * Math.cos(angle)
    const y = centerY + r * Math.sin(angle)
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()
  }

  // 缁樺埗鏍囩
  ctx.setFillStyle('#333')
  ctx.setFontSize(12)
  const labels = ['閫熷害', '鐏垫晱', '鑰愬姏', '鍔涢噺', '鏌旈煣']
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
    return `${Math.round(hours * 60)}鍒嗛挓`
  }
  return `${hours.toFixed(1)}灏忔椂`
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
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 40rpx 30rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #fff;
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
  border-radius: 20rpx;
  padding: 30rpx;
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
}

.dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}

.legend-item .label {
  font-size: 24rpx;
  color: #666;
}

.legend-item .value {
  font-size: 24rpx;
  color: #333;
  font-weight: bold;
}

.test-list {
  margin-top: 10rpx;
}

.test-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.test-item:last-child {
  border-bottom: none;
}

.test-date {
  font-size: 28rpx;
  color: #333;
  width: 180rpx;
}

.test-info {
  flex: 1;
}

.test-info .bmi {
  font-size: 28rpx;
  color: #FF8800;
  display: block;
}

.test-info .hw {
  font-size: 24rpx;
  color: #999;
}

.arrow {
  color: #ccc;
  font-size: 28rpx;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.stat-card {
  text-align: center;
  padding: 20rpx;
  background: #f9f9f9;
  border-radius: 12rpx;
}

.stat-card .value {
  font-size: 40rpx;
  font-weight: bold;
  color: #FF8800;
  display: block;
}

.stat-card .label {
  font-size: 22rpx;
  color: #999;
  margin-top: 8rpx;
}

.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
