<template>
  <view class="workbench-page">
    <!-- 用户信息 -->
    <view class="user-header">
      <image :src="coachInfo?.avatar || '/static/default-avatar.png'" class="avatar" />
      <view class="user-info">
        <view class="greeting">{{ getGreeting() }}，{{ coachInfo?.name || '教练' }}</view>
        <view class="date">{{ formatDate(new Date()) }}</view>
      </view>
    </view>

    <!-- 今日概览 -->
    <view class="overview-card">
      <view class="overview-title">今日概览</view>
      <view class="overview-stats">
        <view class="stat-item">
          <view class="stat-value">{{ todayStats.totalLessons }}</view>
          <view class="stat-label">课程数</view>
        </view>
        <view class="stat-item">
          <view class="stat-value">{{ todayStats.completedLessons }}</view>
          <view class="stat-label">已完成</view>
        </view>
        <view class="stat-item">
          <view class="stat-value">{{ todayStats.totalStudents }}</view>
          <view class="stat-label">学员数</view>
        </view>
      </view>
    </view>

    <!-- 今日课程 -->
    <view class="section">
      <view class="section-header">
        <view class="section-title">今日课程</view>
        <view class="section-more" @click="goToSchedule">查看全部 ></view>
      </view>

      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>

      <view v-else-if="todayLessons.length > 0" class="lesson-list">
        <view
          v-for="lesson in todayLessons"
          :key="lesson.id"
          class="lesson-card"
          @click="goToLessonDetail(lesson.id)"
        >
          <view class="lesson-time">
            <text class="time-text">{{ lesson.start_time }}</text>
            <text class="time-divider">-</text>
            <text class="time-text">{{ lesson.end_time }}</text>
          </view>
          <view class="lesson-info">
            <view class="lesson-name">{{ lesson.student_name }}</view>
            <view class="lesson-type">私教课</view>
          </view>
          <view :class="['lesson-status', lesson.status]">
            {{ getStatusText(lesson.status) }}
          </view>
        </view>
      </view>

      <view v-else class="empty-lessons">
        <text>今日暂无课程安排</text>
      </view>
    </view>

    <!-- 快捷操作 -->
    <view class="section">
      <view class="section-title">快捷操作</view>
      <view class="quick-actions">
        <view class="action-item" @click="goToSlots">
          <view class="action-icon">📅</view>
          <view class="action-label">设置时段</view>
        </view>
        <view class="action-item" @click="goToStudents">
          <view class="action-icon">👥</view>
          <view class="action-label">我的学员</view>
        </view>
        <view class="action-item" @click="goToIncome">
          <view class="action-icon">💰</view>
          <view class="action-label">收入统计</view>
        </view>
        <view class="action-item" @click="goToReviews">
          <view class="action-icon">⭐</view>
          <view class="action-label">我的评价</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { coachApi, scheduleApi } from '@/api/index'

interface CoachInfo {
  id: number
  name: string
  avatar: string | null
  total_students: number
  total_lessons: number
  avg_rating: number
}

interface Lesson {
  id: number
  student_name: string
  start_time: string
  end_time: string
  status: string
  booking_date: string
}

const coachInfo = ref<CoachInfo | null>(null)
const todayStats = ref({
  totalLessons: 0,
  completedLessons: 0,
  totalStudents: 0
})
const todayLessons = ref<Lesson[]>([])
const loading = ref(false)

function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
}

function formatDate(date: Date): string {
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${date.getMonth() + 1}月${date.getDate()}日 周${weekdays[date.getDay()]}`
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
    no_show: '未到'
  }
  return map[status] || status
}

async function loadCoachInfo() {
  try {
    const data = await coachApi.getProfile()
    coachInfo.value = data
    todayStats.value.totalStudents = data.total_students || 0
  } catch (error: any) {
    console.error('获取教练信息失败:', error)
  }
}

async function loadTodaySchedule() {
  loading.value = true
  try {
    const today = new Date().toISOString().split('T')[0]
    const data = await scheduleApi.getSchedule({
      start_date: today,
      end_date: today
    })

    todayLessons.value = data.items || []

    // 计算统计
    todayStats.value.totalLessons = todayLessons.value.length
    todayStats.value.completedLessons = todayLessons.value.filter(
      l => l.status === 'completed'
    ).length
  } catch (error: any) {
    console.error('获取课表失败:', error)
    todayLessons.value = []
  } finally {
    loading.value = false
  }
}

function goToSchedule() {
  uni.switchTab({ url: '/pages/schedule/index' })
}

function goToLessonDetail(id: number) {
  uni.navigateTo({ url: `/pages/schedule/detail?id=${id}` })
}

function goToSlots() {
  uni.navigateTo({ url: '/pages/slots/manage' })
}

function goToStudents() {
  uni.switchTab({ url: '/pages/students/index' })
}

function goToIncome() {
  uni.navigateTo({ url: '/pages/income/index' })
}

function goToReviews() {
  uni.navigateTo({ url: '/pages/reviews/index' })
}

onMounted(() => {
  loadCoachInfo()
  loadTodaySchedule()
})
</script>

<style lang="scss" scoped>
.workbench-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
}

.user-header {
  display: flex;
  align-items: center;
  padding: 40rpx 30rpx;
  background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
  color: #fff;

  .avatar {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;
    border: 4rpx solid rgba(255, 255, 255, 0.5);
    background-color: #e0e0e0;
  }

  .user-info {
    margin-left: 24rpx;

    .greeting {
      font-size: 36rpx;
      font-weight: 600;
    }

    .date {
      font-size: 26rpx;
      opacity: 0.9;
      margin-top: 8rpx;
    }
  }
}

.overview-card {
  background-color: #fff;
  margin: -30rpx 20rpx 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);

  .overview-title {
    font-size: 28rpx;
    color: #666;
    margin-bottom: 24rpx;
  }

  .overview-stats {
    display: flex;
    justify-content: space-around;

    .stat-item {
      text-align: center;

      .stat-value {
        font-size: 48rpx;
        font-weight: 600;
        color: #2196F3;
      }

      .stat-label {
        font-size: 24rpx;
        color: #999;
        margin-top: 8rpx;
      }
    }
  }
}

.section {
  background-color: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
  }

  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
  }

  .section-more {
    font-size: 26rpx;
    color: #999;
  }
}

.loading-state {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 28rpx;
}

.lesson-list {
  .lesson-card {
    display: flex;
    align-items: center;
    padding: 20rpx;
    background-color: #f9f9f9;
    border-radius: 12rpx;
    margin-bottom: 16rpx;

    &:last-child {
      margin-bottom: 0;
    }

    .lesson-time {
      width: 140rpx;
      text-align: center;

      .time-text {
        font-size: 28rpx;
        color: #333;
        font-weight: 500;
      }

      .time-divider {
        font-size: 24rpx;
        color: #999;
        margin: 0 4rpx;
      }
    }

    .lesson-info {
      flex: 1;
      margin-left: 20rpx;

      .lesson-name {
        font-size: 30rpx;
        color: #333;
        font-weight: 500;
      }

      .lesson-type {
        font-size: 24rpx;
        color: #999;
        margin-top: 4rpx;
      }
    }

    .lesson-status {
      padding: 8rpx 16rpx;
      border-radius: 20rpx;
      font-size: 24rpx;

      &.pending {
        background-color: #fff3e0;
        color: #ff9800;
      }

      &.confirmed {
        background-color: #e3f2fd;
        color: #2196F3;
      }

      &.completed {
        background-color: #e8f5e9;
        color: #4caf50;
      }

      &.cancelled {
        background-color: #ffebee;
        color: #f44336;
      }

      &.no_show {
        background-color: #fce4ec;
        color: #e91e63;
      }
    }
  }
}

.empty-lessons {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 28rpx;
}

.quick-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 20rpx;

  .action-item {
    display: flex;
    flex-direction: column;
    align-items: center;

    .action-icon {
      width: 100rpx;
      height: 100rpx;
      background-color: #f5f5f5;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40rpx;
    }

    .action-label {
      font-size: 26rpx;
      color: #666;
      margin-top: 12rpx;
    }
  }
}
</style>
