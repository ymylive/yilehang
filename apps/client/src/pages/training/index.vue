<template>
  <view class="page">
    <!-- 椤堕儴浠嬬粛 -->
    <view class="header">
      <text class="title">AI鏅鸿兘闄粌</text>
      <text class="desc">閫夋嫨杩愬姩绫诲瀷锛屽紑濮嬩綘鐨勮缁冨惂锛?/text>
    </view>

    <!-- 杩愬姩绫诲瀷鍒楄〃 -->
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

    <!-- 鏈€杩戣缁?-->
    <view class="section" v-if="recentSessions.length">
      <view class="section-header">
        <text class="title">鏈€杩戣缁?/text>
      </view>
      <view class="session-list">
        <view class="session-item" v-for="session in recentSessions" :key="session.id">
          <view class="session-icon">{{ getExerciseEmoji(session.exercise_type) }}</view>
          <view class="session-info">
            <text class="type">{{ getExerciseName(session.exercise_type) }}</text>
            <text class="time">{{ formatTime(session.created_at) }}</text>
          </view>
          <view class="session-stats">
            <text class="reps">{{ session.reps_count }}娆?/text>
            <text class="calories">{{ session.calories_burned?.toFixed(0) || 0 }}鍗?/text>
          </view>
        </view>
      </view>
    </view>

    <!-- 璁粌鎻愮ず -->
    <view class="tips">
      <view class="tip-title">璁粌灏忚创澹?/view>
      <view class="tip-item">1. 纭繚鎽勫儚澶磋兘鎷嶆憚鍒板叏韬?/view>
      <view class="tip-item">2. 淇濇寔2-3绫崇殑閫傚綋璺濈</view>
      <view class="tip-item">3. 纭繚鍏夌嚎鍏呰冻</view>
      <view class="tip-item">4. 绌跨潃鑸掗€傜殑杩愬姩鏈嶈</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { trainingApi } from '@/api'

const userStore = useUserStore()

// 杩愬姩绫诲瀷
const exercises = ref([
  { id: 'jump_rope', name: '跳绳', description: '节奏训练 + 心肺提升', emoji: '跳', difficulty: 'normal' },
  { id: 'squat', name: '娣辫共', description: '鏍囧噯娣辫共鍔ㄤ綔', emoji: '馃弸锔?, difficulty: 'normal' },
  { id: 'jumping_jack', name: '寮€鍚堣烦', description: '鍏ㄨ韩鏈夋哀杩愬姩', emoji: '馃じ', difficulty: 'easy' },
  { id: 'high_knees', name: '楂樻姮鑵?, description: '鍘熷湴楂樻姮鑵胯窇', emoji: '馃弮', difficulty: 'normal' },
  { id: 'pushup', name: '淇崸鎾?, description: '鏍囧噯淇崸鎾?, emoji: '馃挭', difficulty: 'hard' },
  { id: 'lunge', name: '寮撴韫?, description: '浜ゆ浛寮撴韫?, emoji: '馃Φ', difficulty: 'normal' },
  { id: 'plank', name: '骞虫澘鏀拺', description: '鏍稿績鍔涢噺璁粌', emoji: '馃', difficulty: 'hard' }
])

// 鏈€杩戣缁冭褰?const recentSessions = ref<any[]>([])

onMounted(async () => {
  await loadRecentSessions()
})

async function loadRecentSessions() {
  if (!userStore.currentStudent) return

  try {
    const res = await trainingApi.getHistory(userStore.currentStudent.id, 0, 5)
    recentSessions.value = res || []
  } catch (error) {
    console.error('鍔犺浇璁粌璁板綍澶辫触', error)
  }
}

function selectExercise(exercise: any) {
  if (!userStore.currentStudent) {
    uni.showToast({ title: '璇峰厛缁戝畾瀛﹀憳', icon: 'none' })
    return
  }

  uni.navigateTo({
    url: `/pages/training/session?type=${exercise.id}&name=${exercise.name}`
  })
}

function getDifficultyText(difficulty: string) {
  const map: Record<string, string> = {
    easy: '绠€鍗?,
    normal: '涓瓑',
    hard: '鍥伴毦'
  }
  return map[difficulty] || difficulty
}

function getExerciseEmoji(type: string) {
  const exercise = exercises.value.find(e => e.id === type)
  return exercise?.emoji || '馃弮'
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

  if (minutes < 60) return `${minutes}鍒嗛挓鍓峘
  if (hours < 24) return `${hours}灏忔椂鍓峘
  if (days < 7) return `${days}澶╁墠`
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
  background: linear-gradient(135deg, #FFB347, #FF8800);
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
  color: #FF8800;
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
  color: #FF8800;
  margin-bottom: 16rpx;
}

.tip-item {
  font-size: 24rpx;
  color: #666;
  line-height: 1.8;
}
</style>
