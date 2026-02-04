<template>
  <view class="page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar">
      <view class="back" @click="goBack">
        <text>返回</text>
      </view>
      <text class="title">{{ exerciseName }}</text>
      <view class="timer">{{ formatDuration(duration) }}</view>
    </view>

    <!-- 视频区域 -->
    <view class="video-container">
      <!-- H5使用video标签 -->
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

      <!-- 小程序使用camera组件 -->
      <!-- #ifndef H5 -->
      <camera
        class="camera"
        device-position="front"
        flash="off"
        @error="onCameraError"
      />
      <!-- #endif -->

      <!-- 骨骼绘制层 -->
      <canvas canvas-id="poseCanvas" class="pose-canvas" />

      <!-- 计数显示 -->
      <view class="count-display">
        <text class="count">{{ count }}</text>
        <text class="label">次</text>
      </view>

      <!-- 反馈提示 -->
      <view class="feedback" :class="{ show: feedback }">
        <text>{{ feedback }}</text>
      </view>
    </view>

    <!-- 控制区域 -->
    <view class="controls">
      <view class="stats">
        <view class="stat-item">
          <text class="value">{{ accuracy.toFixed(0) }}%</text>
          <text class="label">准确率</text>
        </view>
        <view class="stat-item">
          <text class="value">{{ calories.toFixed(0) }}</text>
          <text class="label">卡路里</text>
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
        <text class="result-title">训练完成！</text>
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
          <button class="btn-done" @click="saveAndExit">保存退出</button>
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

// 路由参数
const exerciseType = ref('')
const exerciseName = ref('')

// 训练状态
const isTraining = ref(false)
const isPaused = ref(false)
const showResult = ref(false)

// 训练数据
const count = ref(0)
const duration = ref(0)
const accuracy = ref(100)
const calories = ref(0)
const feedback = ref('')

// 计时器
let durationTimer: any = null

// 卡路里系数
const caloriesPerRep: Record<string, number> = {
  squat: 0.32,
  jumping_jack: 0.2,
  high_knees: 0.15,
  pushup: 0.5,
  lunge: 0.35,
  plank: 0.05
}

onMounted(() => {
  // 获取路由参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.$page?.options || currentPage.options || {}

  exerciseType.value = options.type || 'squat'
  exerciseName.value = options.name || '深蹲'

  // 初始化摄像头
  initCamera()
})

onUnmounted(() => {
  stopTimer()
  stopCamera()
})

// 初始化摄像头
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
    console.error('摄像头初始化失败', error)
    uni.showToast({ title: '无法访问摄像头', icon: 'none' })
  }
  // #endif
}

// 停止摄像头
function stopCamera() {
  // #ifdef H5
  const video = document.getElementById('camera-video') as HTMLVideoElement
  if (video && video.srcObject) {
    const stream = video.srcObject as MediaStream
    stream.getTracks().forEach(track => track.stop())
  }
  // #endif
}

// 开始训练
function startTraining() {
  isTraining.value = true
  isPaused.value = false
  startTimer()
  startPoseDetection()
  feedback.value = '开始训练！'
  setTimeout(() => { feedback.value = '' }, 2000)
}

// 暂停/继续
function togglePause() {
  isPaused.value = !isPaused.value
  if (isPaused.value) {
    stopTimer()
  } else {
    startTimer()
  }
}

// 停止训练
function stopTraining() {
  isTraining.value = false
  stopTimer()
  stopPoseDetection()
  showResult.value = true
}

// 开始计时
function startTimer() {
  durationTimer = setInterval(() => {
    duration.value++
  }, 1000)
}

// 停止计时
function stopTimer() {
  if (durationTimer) {
    clearInterval(durationTimer)
    durationTimer = null
  }
}

// 开始姿态检测
function startPoseDetection() {
  // 这里应该集成MediaPipe进行实时姿态检测
  // 由于UniApp的限制，完整的MediaPipe集成需要在H5端实现
  // 这里使用模拟数据演示

  // #ifdef H5
  simulateTraining()
  // #endif
}

// 停止姿态检测
function stopPoseDetection() {
  // 停止检测
}

// 模拟训练（演示用）
function simulateTraining() {
  const interval = setInterval(() => {
    if (!isTraining.value || isPaused.value) {
      clearInterval(interval)
      return
    }

    // 模拟计数增加
    if (Math.random() > 0.7) {
      count.value++
      calories.value = count.value * (caloriesPerRep[exerciseType.value] || 0.3)
      feedback.value = `完成第${count.value}个！`
      setTimeout(() => { feedback.value = '' }, 1500)
    }
  }, 2000)
}

// 格式化时长
function formatDuration(seconds: number) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 重置训练
function resetTraining() {
  count.value = 0
  duration.value = 0
  accuracy.value = 100
  calories.value = 0
  showResult.value = false
  isTraining.value = false
}

// 保存并退出
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

// 返回
function goBack() {
  if (isTraining.value) {
    uni.showModal({
      title: '提示',
      content: '训练进行中，确定要退出吗？',
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

// 摄像头错误
function onCameraError(e: any) {
  console.error('摄像头错误', e)
  uni.showToast({ title: '摄像头启动失败', icon: 'none' })
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
  color: rgba(255, 255, 255, 0.9);
}

.feedback {
  position: absolute;
  bottom: 200rpx;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  padding: 20rpx 40rpx;
  border-radius: 40rpx;
  opacity: 0;
  transition: opacity 0.3s;
}

.feedback.show {
  opacity: 1;
}

.feedback text {
  color: #fff;
  font-size: 32rpx;
}

.controls {
  background: #fff;
  padding: 30rpx;
  border-radius: 40rpx 40rpx 0 0;
}

.stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30rpx;
}

.stat-item {
  text-align: center;
}

.stat-item .value {
  font-size: 48rpx;
  font-weight: bold;
  color: #4CAF50;
  display: block;
}

.stat-item .label {
  font-size: 24rpx;
  color: #999;
}

.buttons {
  display: flex;
  gap: 20rpx;
}

.btn-start,
.btn-pause,
.btn-stop {
  flex: 1;
  padding: 24rpx;
  border-radius: 50rpx;
  font-size: 32rpx;
  border: none;
}

.btn-start {
  background: #4CAF50;
  color: #fff;
}

.btn-pause {
  background: #FF9800;
  color: #fff;
}

.btn-stop {
  background: #f5f5f5;
  color: #666;
}

/* 结果弹窗 */
.result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.result-content {
  background: #fff;
  border-radius: 30rpx;
  padding: 60rpx 40rpx;
  width: 80%;
  text-align: center;
}

.result-icon {
  font-size: 100rpx;
}

.result-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin: 20rpx 0;
  display: block;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30rpx;
  margin: 40rpx 0;
}

.result-item {
  text-align: center;
}

.result-item .value {
  font-size: 44rpx;
  font-weight: bold;
  color: #4CAF50;
  display: block;
}

.result-item .label {
  font-size: 24rpx;
  color: #999;
}

.result-buttons {
  display: flex;
  gap: 20rpx;
  margin-top: 30rpx;
}

.btn-again,
.btn-done {
  flex: 1;
  padding: 24rpx;
  border-radius: 50rpx;
  font-size: 28rpx;
  border: none;
}

.btn-again {
  background: #f5f5f5;
  color: #666;
}

.btn-done {
  background: #4CAF50;
  color: #fff;
}
</style>
