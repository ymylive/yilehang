<template>
  <view class="page">
    <!-- 页面标题 -->
    <view class="header">
      <text class="title">AI运动训练</text>
      <text class="desc">选择训练项目，AI将辅助记录动作与训练数据。</text>
    </view>

    <!-- 训练项目列表 -->
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

    <!-- 最近记录 -->
    <view class="section" v-if="recentSessions.length">
      <view class="section-header">
        <text class="title">最近记录</text>
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

    <!-- 训练小贴士 -->
    <view class="tips">
      <view class="tip-title">训练小贴士</view>
      <view class="tip-item">1. 运动前热身3-5分钟，避免拉伤。</view>
      <view class="tip-item">2. 训练强度循序渐进，保持节奏与呼吸。</view>
      <view class="tip-item">3. 训练后拉伸放松，促进恢复。</view>
      <view class="tip-item">4. 结合饮食与休息，效果更佳。</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { trainingApi } from '@/api'

const userStore = useUserStore()

const exercises = ref([
  { id: 'jump_rope', name: '跳绳', description: '节奏训练 + 心肺提升', emoji: '绳', difficulty: 'normal' },
  { id: 'squat', name: '深蹲', description: '标准深蹲动作', emoji: '蹲', difficulty: 'normal' },
  { id: 'jumping_jack', name: '开合跳', description: '全身有氧运动', emoji: '跳', difficulty: 'easy' },
  { id: 'high_knees', name: '高抬腿', description: '原地高抬腿跑', emoji: '腿', difficulty: 'normal' },
  { id: 'pushup', name: '俯卧撑', description: '标准俯卧撑', emoji: '撑', difficulty: 'hard' },
  { id: 'lunge', name: '弓步蹲', description: '左右交替弓步蹲', emoji: '弓', difficulty: 'normal' },
  { id: 'plank', name: '平板支撑', description: '核心力量训练', emoji: '板', difficulty: 'hard' }
])

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
    uni.showToast({ title: '请先登录或选择学员', icon: 'none' })
    return
  }

  uni.navigateTo({
    url: `/pages/training/session?type=${exercise.id}&name=${exercise.name}`
  })
}

function getDifficultyText(difficulty: string) {
  const map: Record<string, string> = {
    easy: '入门',
    normal: '适中',
    hard: '挑战'
  }
  return map[difficulty] || difficulty
}

function getExerciseEmoji(type: string) {
  const exercise = exercises.value.find(e => e.id === type)
  return exercise?.emoji || '动'
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
  background: #FFFBF5;
  padding-bottom: 120rpx;
}

.header {
  padding: 60rpx 30rpx 40rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  color: #fff;
  animation: fadeUp 0.3s ease-out;
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
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  animation: fadeUp 0.4s ease-out;
  animation-fill-mode: both;
  transition: all 0.2s ease;
}

.exercise-card:nth-child(1) { animation-delay: 0.05s; }
.exercise-card:nth-child(2) { animation-delay: 0.1s; }
.exercise-card:nth-child(3) { animation-delay: 0.15s; }
.exercise-card:nth-child(4) { animation-delay: 0.2s; }
.exercise-card:nth-child(5) { animation-delay: 0.25s; }
.exercise-card:nth-child(6) { animation-delay: 0.3s; }
.exercise-card:nth-child(7) { animation-delay: 0.35s; }

.exercise-card:active {
  transform: scale(0.99);
}

.exercise-card .icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 50rpx;
  background: #FFF3E0;
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
  background: #FFF3E0;
  color: #FF8800;
}

.difficulty.normal {
  background: #FFE0B2;
  color: #FF7A18;
}

.difficulty.hard {
  background: #FFD7CC;
  color: #E65100;
}

.section {
  margin: 20rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  animation: fadeUp 0.4s ease-out 0.3s both;
}

.section-header {
  margin-bottom: 20rpx;
}

.section-header .title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #FFF7ED;
  padding: 20rpx;
  border-radius: 16rpx;
}

.session-icon {
  width: 60rpx;
  height: 60rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFF3E0;
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
  margin-top: 6rpx;
}

.session-stats {
  text-align: right;
  font-size: 24rpx;
  color: #666;
}

.tips {
  margin: 20rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  font-size: 24rpx;
  color: #666;
  line-height: 1.8;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  animation: fadeUp 0.4s ease-out 0.35s both;
}

.tip-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 12rpx;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
