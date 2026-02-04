<template>
  <view class="page">
    <!-- 顶部用户信息 -->
    <view class="header">
      <view class="user-info" @click="goToUser">
        <image class="avatar" :src="userStore.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
        <view class="info">
          <text class="name">{{ currentStudentName }}</text>
          <text class="lessons">剩余课时: {{ userStore.currentStudent?.remaining_lessons || 0 }}</text>
        </view>
      </view>
      <view class="actions">
        <view class="action-btn" @click="scanQRCode">
          <text class="iconfont">扫码</text>
        </view>
      </view>
    </view>

    <!-- 功能入口 -->
    <view class="feature-grid">
      <view class="feature-item" @click="goTo('/pages/growth/index')">
        <view class="icon growth-icon">📊</view>
        <text class="label">成长档案</text>
      </view>
      <view class="feature-item" @click="goTo('/pages/training/index')">
        <view class="icon training-icon">🏃</view>
        <text class="label">AI陪练</text>
      </view>
      <view class="feature-item" @click="goTo('/pages/homework/index')">
        <view class="icon homework-icon">📝</view>
        <text class="label">作业闯关</text>
      </view>
      <view class="feature-item" @click="goTo('/pages/moments/index')">
        <view class="icon moments-icon">📸</view>
        <text class="label">精彩瞬间</text>
      </view>
    </view>

    <!-- 今日课程 -->
    <view class="section">
      <view class="section-header">
        <text class="title">今日课程</text>
        <text class="more" @click="goTo('/pages/schedule/index')">查看全部 ></text>
      </view>
      <view class="course-list" v-if="todayCourses.length">
        <view class="course-card" v-for="course in todayCourses" :key="course.id">
          <view class="course-time">
            <text class="time">{{ formatTime(course.start_time) }}</text>
            <text class="duration">{{ course.duration }}分钟</text>
          </view>
          <view class="course-info">
            <text class="course-name">{{ course.name }}</text>
            <text class="coach">教练: {{ course.coach_name }}</text>
          </view>
          <view class="course-status" :class="course.status">
            {{ getStatusText(course.status) }}
          </view>
        </view>
      </view>
      <view class="empty" v-else>
        <text>今日暂无课程安排</text>
      </view>
    </view>

    <!-- 训练统计 -->
    <view class="section">
      <view class="section-header">
        <text class="title">本周训练</text>
      </view>
      <view class="stats-card">
        <view class="stat-item">
          <text class="value">{{ weekStats.sessions }}</text>
          <text class="label">训练次数</text>
        </view>
        <view class="stat-item">
          <text class="value">{{ weekStats.duration }}</text>
          <text class="label">训练时长(分)</text>
        </view>
        <view class="stat-item">
          <text class="value">{{ weekStats.calories }}</text>
          <text class="label">消耗卡路里</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { scheduleApi, trainingApi } from '@/api'

const userStore = useUserStore()

// 当前学员名称
const currentStudentName = computed(() => {
  return userStore.currentStudent?.name || userStore.user?.nickname || '未绑定学员'
})

// 今日课程
const todayCourses = ref<any[]>([])

// 本周统计
const weekStats = ref({
  sessions: 0,
  duration: 0,
  calories: 0
})

// 加载数据
onMounted(async () => {
  await loadTodayCourses()
  await loadWeekStats()
})

// 加载今日课程
async function loadTodayCourses() {
  try {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    const res = await scheduleApi.list({
      start_date: today.toISOString(),
      end_date: tomorrow.toISOString()
    })
    todayCourses.value = res || []
  } catch (error) {
    console.error('加载课程失败', error)
  }
}

// 加载本周统计
async function loadWeekStats() {
  if (!userStore.currentStudent) return

  try {
    const history = await trainingApi.getHistory(userStore.currentStudent.id, 0, 100)
    // 计算本周数据
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)

    const weekData = (history || []).filter((item: any) =>
      new Date(item.created_at) >= weekAgo
    )

    weekStats.value = {
      sessions: weekData.length,
      duration: Math.round(weekData.reduce((sum: number, item: any) => sum + item.duration, 0) / 60),
      calories: Math.round(weekData.reduce((sum: number, item: any) => sum + (item.calories_burned || 0), 0))
    }
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

// 格式化时间
function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 获取状态文本
function getStatusText(status: string) {
  const map: Record<string, string> = {
    scheduled: '待上课',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 页面跳转
function goTo(url: string) {
  uni.navigateTo({ url })
}

function goToUser() {
  uni.switchTab({ url: '/pages/user/index' })
}

// 扫码签到
function scanQRCode() {
  uni.scanCode({
    success: (res) => {
      console.log('扫码结果', res)
      // 处理签到逻辑
    }
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #4CAF50 0%, #f5f5f5 30%);
  padding-bottom: 120rpx;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 30rpx;
  color: #fff;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.5);
}

.info {
  margin-left: 20rpx;
}

.name {
  font-size: 36rpx;
  font-weight: bold;
  display: block;
}

.lessons {
  font-size: 24rpx;
  opacity: 0.9;
}

.action-btn {
  padding: 16rpx 24rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 30rpx;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
  padding: 30rpx;
  background: #fff;
  margin: 0 20rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
}

.icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-bottom: 12rpx;
}

.growth-icon { background: #E3F2FD; }
.training-icon { background: #E8F5E9; }
.homework-icon { background: #FFF3E0; }
.moments-icon { background: #FCE4EC; }

.label {
  font-size: 24rpx;
  color: #666;
}

.section {
  margin: 30rpx 20rpx;
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

.section-header .more {
  font-size: 24rpx;
  color: #999;
}

.course-card {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.course-card:last-child {
  border-bottom: none;
}

.course-time {
  width: 120rpx;
}

.course-time .time {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.course-time .duration {
  font-size: 22rpx;
  color: #999;
}

.course-info {
  flex: 1;
  margin-left: 20rpx;
}

.course-name {
  font-size: 28rpx;
  color: #333;
  display: block;
}

.coach {
  font-size: 24rpx;
  color: #999;
}

.course-status {
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.course-status.scheduled {
  background: #E8F5E9;
  color: #4CAF50;
}

.course-status.ongoing {
  background: #FFF3E0;
  color: #FF9800;
}

.course-status.completed {
  background: #E3F2FD;
  color: #2196F3;
}

.stats-card {
  display: flex;
  justify-content: space-around;
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

.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
