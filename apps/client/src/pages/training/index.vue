<template>
  <view class="page">
    <!-- 顶部介绍 -->
    <view class="header">
      <text class="title">AI智能陪练</text>
      <text class="desc">选择运动类型，开始你的训练吧！</text>
    </view>

    <!-- 运动类型列表 -->
    <view class="exercise-grid">
      <view
        class="exercise-card"
        v-for="exercise in exercises"
        :key="exercise.id"
        @click="selectExercise(exercise)"
      >
        <view class="icon" :class="exercise.id">{{ exercise.emoji }}</view>
        <view class="info">
          <text class="name">{{ exercise.name }}</text>
          <text class="desc">{{ exercise.description }}</text>
        </view>
        <view class="difficulty" :class="exercise.difficulty">
          {{ getDifficultyText(exercise.difficulty) }}
        </view>
      </view>
    </view>

    <!-- 最近训练 -->
    <view class="section" v-if="recentSessions.length">
      <view class="section-header">
        <text class="title">最近训练</text>
      </view>
      <view class="session-list">
        <view class="session-item" v-for="session in recentSessions" :key="session.id">
          <view class="session-icon">{{ getExerciseEmoji(session.exercise_type) }}</view>
          <view class="session-info">
            <text class="type">{{ getExerciseName(session.exercise_type) }}</text>
            <text class="time">{{ formatTime(session.created_at) }}</text>
          </view>
          <view class="session-stats">
            <text class="reps">{{ session.reps_count }}次</text>
            <text class="calories">{{ session.calories_burned?.toFixed(0) || 0 }}卡</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 训练提示 -->
    <view class="tips">
      <view class="tip-title">训练小贴士</view>
      <view class="tip-item">1. 确保摄像头能拍摄到全身</view>
      <view class="tip-item">2. 保持2-3米的适当距离</view>
      <view class="tip-item">3. 确保光线充足</view>
      <view class="tip-item">4. 穿着舒适的运动服装</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { trainingApi } from '@/api'

const userStore = useUserStore()

// 运动类型
const exercises = ref([
  { id: 'squat', name: '深蹲', description: '标准深蹲动作', emoji: '🏋️', difficulty: 'normal' },
  { id: 'jumping_jack', name: '开合跳', description: '全身有氧运动', emoji: '🤸', difficulty: 'easy' },
  { id: 'high_knees', name: '高抬腿', description: '原地高抬腿跑', emoji: '🏃', difficulty: 'normal' },
  { id: 'pushup', name: '俯卧撑', description: '标准俯卧撑', emoji: '💪', difficulty: 'hard' },
  { id: 'lunge', name: '弓步蹲', description: '交替弓步蹲', emoji: '🦵', difficulty: 'normal' },
  { id: 'plank', name: '平板支撑', description: '核心力量训练', emoji: '🧘', difficulty: 'hard' }
])

// 最近训练记录
const recentSessions = ref<any[]>([])

onMounted(async () => {
  await loadRecentSessions()
})

async function loadRecentSessions() {
  if (!userStore.currentStudent) return

  try {
    const res = await trainingApi.getHistory(userStore.currentStudent.id, 0, 5)
    recentSessions.value = res || []
  } catch (error) {
    console.error('加载训练记录失败', error)
  }
}

function selectExercise(exercise: any) {
  if (!userStore.currentStudent) {
    uni.showToast({ title: '请先绑定学员', icon: 'none' })
    return
  }

  uni.navigateTo({
    url: `/pages/training/session?type=${exercise.id}&name=${exercise.name}`
  })
}

function getDifficultyText(difficulty: string) {
  const map: Record<string, string> = {
    easy: '简单',
    normal: '中等',
    hard: '困难'
  }
  return map[difficulty] || difficulty
}

function getExerciseEmoji(type: string) {
  const exercise = exercises.value.find(e => e.id === type)
  return exercise?.emoji || '🏃'
}

function getExerciseName(type: string) {
  const exercise = exercises.value.find(e => e.id === type)
  return exercise?.name || type
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.header {
  padding: 60rpx 30rpx 40rpx;
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: #fff;
}

.header .title {
  font-size: 44rpx;
  font-weight: bold;
  display: block;
}

.header .desc {
  font-size: 28rpx;
  opacity: 0.9;
  margin-top: 12rpx;
}

.exercise-grid {
  padding: 20rpx;
}

.exercise-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.exercise-card .icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 50rpx;
  background: #E8F5E9;
}

.exercise-card .info {
  flex: 1;
  margin-left: 24rpx;
}

.exercise-card .name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.exercise-card .desc {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.difficulty {
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.difficulty.easy {
  background: #E8F5E9;
  color: #4CAF50;
}

.difficulty.normal {
  background: #FFF3E0;
  color: #FF9800;
}

.difficulty.hard {
  background: #FFEBEE;
  color: #F44336;
}

.section {
  margin: 20rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.section-header {
  margin-bottom: 20rpx;
}

.section-header .title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.session-item:last-child {
  border-bottom: none;
}

.session-icon {
  width: 60rpx;
  height: 60rpx;
  background: #f5f5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
}

.session-info {
  flex: 1;
  margin-left: 20rpx;
}

.session-info .type {
  font-size: 28rpx;
  color: #333;
  display: block;
}

.session-info .time {
  font-size: 22rpx;
  color: #999;
}

.session-stats {
  text-align: right;
}

.session-stats .reps {
  font-size: 28rpx;
  color: #4CAF50;
  font-weight: bold;
  display: block;
}

.session-stats .calories {
  font-size: 22rpx;
  color: #999;
}

.tips {
  margin: 20rpx;
  background: #FFF8E1;
  border-radius: 20rpx;
  padding: 30rpx;
}

.tip-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #FF9800;
  margin-bottom: 16rpx;
}

.tip-item {
  font-size: 24rpx;
  color: #666;
  line-height: 1.8;
}
</style>
