<template>
  <view class="page">
    <view class="header">
      <text class="title">作业闯关</text>
      <text class="desc">完成作业获取积分奖励</text>
    </view>

    <!-- 积分卡片 -->
    <view class="points-card">
      <view class="points-info">
        <text class="label">我的积分</text>
        <text class="value">{{ totalPoints }}</text>
      </view>
      <view class="points-action" @click="goToShop">积分商城 ></view>
    </view>

    <!-- 作业列表 -->
    <view class="homework-list">
      <view class="section-title">待完成作业</view>
      <view class="homework-card" v-for="hw in pendingHomework" :key="hw.id" @click="startHomework(hw)">
        <view class="hw-icon">{{ getExerciseEmoji(hw.exercise_type) }}</view>
        <view class="hw-info">
          <text class="hw-title">{{ hw.title }}</text>
          <text class="hw-target">目标: {{ hw.target_reps }}次</text>
          <text class="hw-due">截止: {{ formatDate(hw.due_date) }}</text>
        </view>
        <view class="hw-points">+{{ hw.points }}分</view>
      </view>
      <view class="empty" v-if="!pendingHomework.length">
        <text>暂无待完成作业</text>
      </view>
    </view>

    <view class="homework-list">
      <view class="section-title">已完成作业</view>
      <view class="homework-card completed" v-for="hw in completedHomework" :key="hw.id">
        <view class="hw-icon">{{ getExerciseEmoji(hw.exercise_type) }}</view>
        <view class="hw-info">
          <text class="hw-title">{{ hw.title }}</text>
          <text class="hw-result">完成: {{ hw.reps_completed }}次</text>
          <text class="hw-score">得分: {{ hw.score }}</text>
        </view>
        <view class="hw-points earned">+{{ hw.points_earned }}分</view>
      </view>
      <view class="empty" v-if="!completedHomework.length">
        <text>暂无已完成作业</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const totalPoints = ref(0)
const pendingHomework = ref<any[]>([])
const completedHomework = ref<any[]>([])

onMounted(() => {
  loadHomework()
})

function loadHomework() {
  // 模拟数据
  pendingHomework.value = [
    { id: 1, title: '深蹲挑战', exercise_type: 'squat', target_reps: 30, points: 20, due_date: '2024-02-10' },
    { id: 2, title: '开合跳训练', exercise_type: 'jumping_jack', target_reps: 50, points: 15, due_date: '2024-02-12' }
  ]
  completedHomework.value = [
    { id: 3, title: '高抬腿练习', exercise_type: 'high_knees', reps_completed: 40, score: 95, points_earned: 18 }
  ]
  totalPoints.value = 158
}

function getExerciseEmoji(type: string) {
  const map: Record<string, string> = {
    squat: '🏋️',
    jumping_jack: '🤸',
    high_knees: '🏃',
    pushup: '💪',
    lunge: '🦵'
  }
  return map[type] || '🏃'
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function startHomework(hw: any) {
  uni.navigateTo({
    url: `/pages/training/session?type=${hw.exercise_type}&name=${hw.title}&target=${hw.target_reps}`
  })
}

function goToShop() {
  uni.showToast({ title: '积分商城开发中', icon: 'none' })
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
  background: linear-gradient(135deg, #FF9800, #FFB74D);
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

.points-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  margin: -30rpx 20rpx 20rpx;
  padding: 30rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.points-info .label {
  font-size: 26rpx;
  color: #999;
  display: block;
}

.points-info .value {
  font-size: 56rpx;
  font-weight: bold;
  color: #FF9800;
}

.points-action {
  font-size: 28rpx;
  color: #FF9800;
}

.homework-list {
  padding: 0 20rpx;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.homework-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.homework-card.completed {
  opacity: 0.8;
}

.hw-icon {
  width: 80rpx;
  height: 80rpx;
  background: #FFF3E0;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}

.hw-info {
  flex: 1;
  margin-left: 24rpx;
}

.hw-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.hw-target,
.hw-due,
.hw-result,
.hw-score {
  font-size: 24rpx;
  color: #999;
  margin-right: 20rpx;
}

.hw-points {
  font-size: 32rpx;
  font-weight: bold;
  color: #FF9800;
}

.hw-points.earned {
  color: #4CAF50;
}

.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  background: #fff;
  border-radius: 20rpx;
}
</style>
