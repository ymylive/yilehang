<template>
  <view class="page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="back" @click="goBack">
        <text>返回</text>
      </view>
      <text class="title">{{ exerciseName }}</text>
      <view class="timer">{{ formatDuration(duration) }}</view>
    </view>

    <!-- 训练画面 -->
    <view class="video-container">
      <!-- H5 使用 video -->
      <!-- #ifdef H5 -->
      <video
        ref="videoRef"
        id="camera-video"
        class="camera-video"
        autoplay
        playsinline
        muted
      />
      <!-- #endif -->

      <!-- 小程序使用 camera -->
      <!-- #ifndef H5 -->
      <camera
        class="camera"
        device-position="front"
        flash="off"
        @error="onCameraError"
      />
      <!-- #endif -->

      <!-- 姿态渲染 -->
      <canvas canvas-id="poseCanvas" class="pose-canvas" />

      <!-- 计数器 -->
      <view class="count-display">
        <text class="count">{{ count }}</text>
        <text class="label">次</text>
      </view>

      <!-- 反馈提示 -->
      <view class="feedback" :class="{ show: feedback }">
        <text>{{ feedback }}</text>
      </view>
    </view>

    <!-- 控制区 -->
    <view class="controls">
      <view class="stats">
        <view class="stat-item">
          <text class="value">{{ accuracy.toFixed(0) }}%</text>
          <text class="label">准确率</text>
        </view>
        <view class="stat-item">
          <text class="value">{{ calories.toFixed(0) }}</text>
          <text class="label">消耗卡路里</text>
        </view>
      </view>

      <view class="buttons">
        <button class="btn-pause" @click="togglePause" v-if="isTraining">
          {{ isPaused ? '继续' : '暂停' }}
        </button>
        <button class="btn-start" @click="startTraining" v-else>
          开始训练
        </button>
        <button class="btn-stop" @click="stopTraining" v-if="isTraining">
          结束训练
        </button>
      </view>
    </view>

    <!-- 结果弹窗 -->
    <view class="result-modal" v-if="showResult">
      <view class="result-content">
        <view class="result-icon">🎉</view>
        <text class="result-title">训练完成</text>
        <view class="result-stats">
          <view class="result-item">
            <text class="value">{{ count }}</text>
            <text class="label">完成次数</text>
          </view>
          <view class="result-item">
            <text class="value">{{ formatDuration(duration) }}</text>
            <text class="label">训练时长</text>
          </view>
          <view class="result-item">
            <text class="value">{{ calories.toFixed(0) }}</text>
            <text class="label">消耗卡路里</text>
          </view>
          <view class="result-item">
            <text class="value">{{ accuracy.toFixed(0) }}%</text>
            <text class="label">动作准确率</text>
          </view>
        </view>
        <view class="result-buttons">
          <button class="btn-again" @click="resetTraining">再来一次</button>
          <button class="btn-done" @click="saveAndExit">保存并退出</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { trainingApi } from '@/api'

const userStore = useUserStore()

const exerciseType = ref('')
const exerciseName = ref('')

const isTraining = ref(false)
const isPaused = ref(false)
const showResult = ref(false)

const count = ref(0)
const duration = ref(0)
const accuracy = ref(100)
const calories = ref(0)
const feedback = ref('')

let durationTimer: any = null

const caloriesPerRep: Record<string, number> = {
  squat: 0.32,
  jumping_jack: 0.2,
  jump_rope: 0.1,
  high_knees: 0.15,
  pushup: 0.5,
  lunge: 0.35,
  plank: 0.05
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.$page?.options || currentPage.options || {}

  exerciseType.value = options.type || 'squat'
  exerciseName.value = options.name || '深蹲'

  initCamera()
})

onUnmounted(() => {
  stopTimer()
  stopCamera()
})

async function initCamera() {
  // #ifdef H5
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 640, height: 480 }
    })
    const video = document.getElementById('camera-video') as HTMLVideoElement
    if (video) {
      video.srcObject = stream
    }
  } catch (error) {
    console.error('摄像头启动失败', error)
    uni.showToast({ title: '无法使用摄像头', icon: 'none' })
  }
  // #endif
}

function stopCamera() {
  // #ifdef H5
  const video = document.getElementById('camera-video') as HTMLVideoElement
  if (video && video.srcObject) {
    const stream = video.srcObject as MediaStream
    stream.getTracks().forEach(track => track.stop())
  }
  // #endif
}

function startTraining() {
  isTraining.value = true
  isPaused.value = false
  startTimer()
  startPoseDetection()
  feedback.value = '开始训练，加油！'
  setTimeout(() => { feedback.value = '' }, 2000)
}

function togglePause() {
  isPaused.value = !isPaused.value
  if (isPaused.value) {
    stopTimer()
  } else {
    startTimer()
  }
}

function stopTraining() {
  isTraining.value = false
  stopTimer()
  stopPoseDetection()
  showResult.value = true
}

function startTimer() {
  durationTimer = setInterval(() => {
    duration.value++
  }, 1000)
}

function stopTimer() {
  if (durationTimer) {
    clearInterval(durationTimer)
    durationTimer = null
  }
}

function startPoseDetection() {
  // 这里接入姿态识别与动作计数（当前使用模拟）
  // #ifdef H5
  simulateTraining()
  // #endif
}

function stopPoseDetection() {
  // 预留停止姿态识别的逻辑
}

function simulateTraining() {
  const interval = setInterval(() => {
    if (!isTraining.value || isPaused.value) {
      clearInterval(interval)
      return
    }

    if (Math.random() > 0.7) {
      count.value++
      calories.value = count.value * (caloriesPerRep[exerciseType.value] || 0.3)
      feedback.value = `已完成 ${count.value} 次`
      setTimeout(() => { feedback.value = '' }, 1500)
    }
  }, 2000)
}

function formatDuration(seconds: number) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function resetTraining() {
  count.value = 0
  duration.value = 0
  accuracy.value = 100
  calories.value = 0
  showResult.value = false
  isTraining.value = false
}

async function saveAndExit() {
  if (!userStore.currentStudent) {
    uni.navigateBack()
    return
  }

  try {
    await trainingApi.complete({
      student_id: userStore.currentStudent.id,
      exercise_type: exerciseType.value,
      duration: duration.value,
      reps_count: count.value,
      accuracy_score: accuracy.value,
      calories_burned: calories.value
    })

    uni.showToast({ title: '训练记录已保存', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    console.error('保存失败', error)
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

function goBack() {
  if (isTraining.value) {
    uni.showModal({
      title: '提示',
      content: '训练进行中，确定要退出吗？记录将不会保存。',
      success: (res) => {
        if (res.confirm) {
          stopTraining()
          uni.navigateBack()
        }
      }
    })
  } else {
    uni.navigateBack()
  }
}

function onCameraError(e: any) {
  console.error('摄像头错误', e)
  uni.showToast({ title: '摄像头不可用，请检查权限', icon: 'none' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #000;
  display: flex;
  flex-direction: column;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60rpx 30rpx 20rpx;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.nav-bar .back {
  padding: 10rpx 20rpx;
}

.nav-bar .title {
  font-size: 32rpx;
  font-weight: bold;
}

.nav-bar .timer {
  font-size: 32rpx;
  font-family: monospace;
}

.video-container {
  flex: 1;
  position: relative;
  margin-top: 120rpx;
}

.camera-video,
.camera {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pose-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.count-display {
  position: absolute;
  top: 40rpx;
  right: 40rpx;
  background: rgba(76, 175, 80, 0.9);
  padding: 30rpx 50rpx;
  border-radius: 20rpx;
  text-align: center;
}

.count-display .count {
  font-size: 80rpx;
  font-weight: bold;
  color: #fff;
  display: block;
}

.count-display .label {
  font-size: 28rpx;
  color: #fff;
}

.feedback {
  position: absolute;
  bottom: 180rpx;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 16rpx 30rpx;
  border-radius: 30rpx;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feedback.show {
  opacity: 1;
}

.controls {
  background: #111;
  padding: 30rpx;
}

.stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20rpx;
  color: #fff;
}

.stat-item .value {
  font-size: 32rpx;
  font-weight: bold;
  display: block;
}

.stat-item .label {
  font-size: 24rpx;
  opacity: 0.8;
}

.buttons {
  display: flex;
  justify-content: center;
  gap: 20rpx;
}

.btn-start,
.btn-pause,
.btn-stop {
  height: 80rpx;
  padding: 0 40rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  color: #fff;
  background: #FF8800;
}

.btn-stop {
  background: #FF5722;
}

.result-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.result-content {
  width: 80%;
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  text-align: center;
}

.result-icon {
  font-size: 60rpx;
  margin-bottom: 16rpx;
}

.result-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.result-item .value {
  font-size: 28rpx;
  font-weight: bold;
  color: #FF8800;
}

.result-item .label {
  font-size: 22rpx;
  color: #666;
  margin-top: 4rpx;
}

.result-buttons {
  display: flex;
  justify-content: center;
  gap: 20rpx;
}

.btn-again,
.btn-done {
  height: 70rpx;
  padding: 0 30rpx;
  border-radius: 35rpx;
  font-size: 26rpx;
  color: #fff;
  background: #FF8800;
}

.btn-done {
  background: #4CAF50;
}
</style>
