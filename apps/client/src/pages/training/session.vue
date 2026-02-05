<template>
  <view class="page">
    <!-- 鑷畾涔夊鑸爮 -->
    <view class="nav-bar">
      <view class="back" @click="goBack">
        <text>杩斿洖</text>
      </view>
      <text class="title">{{ exerciseName }}</text>
      <view class="timer">{{ formatDuration(duration) }}</view>
    </view>

    <!-- 瑙嗛鍖哄煙 -->
    <view class="video-container">
      <!-- H5浣跨敤video鏍囩 -->
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

      <!-- 灏忕▼搴忎娇鐢╟amera缁勪欢 -->
      <!-- #ifndef H5 -->
      <camera
        class="camera"
        device-position="front"
        flash="off"
        @error="onCameraError"
      />
      <!-- #endif -->

      <!-- 楠ㄩ缁樺埗灞?-->
      <canvas canvas-id="poseCanvas" class="pose-canvas" />

      <!-- 璁℃暟鏄剧ず -->
      <view class="count-display">
        <text class="count">{{ count }}</text>
        <text class="label">娆?/text>
      </view>

      <!-- 鍙嶉鎻愮ず -->
      <view class="feedback" :class="{ show: feedback }">
        <text>{{ feedback }}</text>
      </view>
    </view>

    <!-- 鎺у埗鍖哄煙 -->
    <view class="controls">
      <view class="stats">
        <view class="stat-item">
          <text class="value">{{ accuracy.toFixed(0) }}%</text>
          <text class="label">鍑嗙‘鐜?/text>
        </view>
        <view class="stat-item">
          <text class="value">{{ calories.toFixed(0) }}</text>
          <text class="label">鍗¤矾閲?/text>
        </view>
      </view>

      <view class="buttons">
        <button class="btn-pause" @click="togglePause" v-if="isTraining">
          {{ isPaused ? '缁х画' : '鏆傚仠' }}
        </button>
        <button class="btn-start" @click="startTraining" v-else>
          寮€濮嬭缁?        </button>
        <button class="btn-stop" @click="stopTraining" v-if="isTraining">
          缁撴潫璁粌
        </button>
      </view>
    </view>

    <!-- 缁撴灉寮圭獥 -->
    <view class="result-modal" v-if="showResult">
      <view class="result-content">
        <view class="result-icon">馃帀</view>
        <text class="result-title">璁粌瀹屾垚锛?/text>
        <view class="result-stats">
          <view class="result-item">
            <text class="value">{{ count }}</text>
            <text class="label">瀹屾垚娆℃暟</text>
          </view>
          <view class="result-item">
            <text class="value">{{ formatDuration(duration) }}</text>
            <text class="label">璁粌鏃堕暱</text>
          </view>
          <view class="result-item">
            <text class="value">{{ calories.toFixed(0) }}</text>
            <text class="label">娑堣€楀崱璺噷</text>
          </view>
          <view class="result-item">
            <text class="value">{{ accuracy.toFixed(0) }}%</text>
            <text class="label">鍔ㄤ綔鍑嗙‘鐜?/text>
          </view>
        </view>
        <view class="result-buttons">
          <button class="btn-again" @click="resetTraining">鍐嶆潵涓€娆?/button>
          <button class="btn-done" @click="saveAndExit">淇濆瓨閫€鍑?/button>
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

// 璺敱鍙傛暟
const exerciseType = ref('')
const exerciseName = ref('')

// 璁粌鐘舵€?const isTraining = ref(false)
const isPaused = ref(false)
const showResult = ref(false)

// 璁粌鏁版嵁
const count = ref(0)
const duration = ref(0)
const accuracy = ref(100)
const calories = ref(0)
const feedback = ref('')

// 璁℃椂鍣?let durationTimer: any = null

// 鍗¤矾閲岀郴鏁?const caloriesPerRep: Record<string, number> = {
  squat: 0.32,
  jumping_jack: 0.2,
  jump_rope: 0.1,
  high_knees: 0.15,
  pushup: 0.5,
  lunge: 0.35,
  plank: 0.05
}

onMounted(() => {
  // 鑾峰彇璺敱鍙傛暟
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.$page?.options || currentPage.options || {}

  exerciseType.value = options.type || 'squat'
  exerciseName.value = options.name || '娣辫共'

  // 鍒濆鍖栨憚鍍忓ご
  initCamera()
})

onUnmounted(() => {
  stopTimer()
  stopCamera()
})

// 鍒濆鍖栨憚鍍忓ご
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
    console.error('鎽勫儚澶村垵濮嬪寲澶辫触', error)
    uni.showToast({ title: '鏃犳硶璁块棶鎽勫儚澶?, icon: 'none' })
  }
  // #endif
}

// 鍋滄鎽勫儚澶?function stopCamera() {
  // #ifdef H5
  const video = document.getElementById('camera-video') as HTMLVideoElement
  if (video && video.srcObject) {
    const stream = video.srcObject as MediaStream
    stream.getTracks().forEach(track => track.stop())
  }
  // #endif
}

// 寮€濮嬭缁?function startTraining() {
  isTraining.value = true
  isPaused.value = false
  startTimer()
  startPoseDetection()
  feedback.value = '寮€濮嬭缁冿紒'
  setTimeout(() => { feedback.value = '' }, 2000)
}

// 鏆傚仠/缁х画
function togglePause() {
  isPaused.value = !isPaused.value
  if (isPaused.value) {
    stopTimer()
  } else {
    startTimer()
  }
}

// 鍋滄璁粌
function stopTraining() {
  isTraining.value = false
  stopTimer()
  stopPoseDetection()
  showResult.value = true
}

// 寮€濮嬭鏃?function startTimer() {
  durationTimer = setInterval(() => {
    duration.value++
  }, 1000)
}

// 鍋滄璁℃椂
function stopTimer() {
  if (durationTimer) {
    clearInterval(durationTimer)
    durationTimer = null
  }
}

// 寮€濮嬪Э鎬佹娴?function startPoseDetection() {
  // 棰勭暀濮挎€佹娴嬫帴鍏ヤ綅
  // 鐢变簬UniApp鐨勯檺鍒讹紝瀹屾暣濮挎€佹娴嬪缓璁湪H5绔疄鐜?  // 杩欓噷浣跨敤妯℃嫙鏁版嵁婕旂ず

  // #ifdef H5
  simulateTraining()
  // #endif
}

// 鍋滄濮挎€佹娴?function stopPoseDetection() {
  // 鍋滄妫€娴?}

// 妯℃嫙璁粌锛堟紨绀虹敤锛?function simulateTraining() {
  const interval = setInterval(() => {
    if (!isTraining.value || isPaused.value) {
      clearInterval(interval)
      return
    }

    // 妯℃嫙璁℃暟澧炲姞
    if (Math.random() > 0.7) {
      count.value++
      calories.value = count.value * (caloriesPerRep[exerciseType.value] || 0.3)
      feedback.value = `瀹屾垚绗?{count.value}涓紒`
      setTimeout(() => { feedback.value = '' }, 1500)
    }
  }, 2000)
}

// 鏍煎紡鍖栨椂闀?function formatDuration(seconds: number) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 閲嶇疆璁粌
function resetTraining() {
  count.value = 0
  duration.value = 0
  accuracy.value = 100
  calories.value = 0
  showResult.value = false
  isTraining.value = false
}

// 淇濆瓨骞堕€€鍑?async function saveAndExit() {
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

    uni.showToast({ title: '璁粌璁板綍宸蹭繚瀛?, icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    console.error('淇濆瓨澶辫触', error)
    uni.showToast({ title: '淇濆瓨澶辫触', icon: 'none' })
  }
}

// 杩斿洖
function goBack() {
  if (isTraining.value) {
    uni.showModal({
      title: '鎻愮ず',
      content: '璁粌杩涜涓紝纭畾瑕侀€€鍑哄悧锛?,
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

// 鎽勫儚澶撮敊璇?function onCameraError(e: any) {
  console.error('鎽勫儚澶撮敊璇?, e)
  uni.showToast({ title: '鎽勫儚澶村惎鍔ㄥけ璐?, icon: 'none' })
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
  color: #FF8800;
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
  background: #FF8800;
  color: #fff;
}

.btn-pause {
  background: #FF7A18;
  color: #fff;
}

.btn-stop {
  background: #f5f5f5;
  color: #666;
}

/* 缁撴灉寮圭獥 */
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
  color: #FF8800;
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
  background: #FF8800;
  color: #fff;
}
</style>
