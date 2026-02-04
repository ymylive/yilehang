<template>
  <view class="student-detail-page">
    <!-- 学员基本信息 -->
    <view class="student-header">
      <image :src="student?.avatar || '/static/default-avatar.png'" class="avatar" />
      <view class="student-info">
        <view class="name">{{ student?.name }}</view>
        <view class="meta">
          <text>{{ student?.age }}岁</text>
          <text class="divider">|</text>
          <text>{{ student?.gender === 'male' ? '男' : '女' }}</text>
        </view>
      </view>
    </view>

    <!-- 课时信息 -->
    <view class="stats-card">
      <view class="stat-item">
        <view class="stat-value">{{ student?.remaining_times || 0 }}</view>
        <view class="stat-label">剩余课时</view>
      </view>
      <view class="stat-item">
        <view class="stat-value">{{ student?.total_lessons || 0 }}</view>
        <view class="stat-label">已上课时</view>
      </view>
      <view class="stat-item">
        <view class="stat-value">{{ student?.attendance_rate || 0 }}%</view>
        <view class="stat-label">出勤率</view>
      </view>
    </view>

    <!-- 联系方式 -->
    <view class="section">
      <view class="section-title">联系方式</view>
      <view class="contact-card">
        <view class="contact-item" @click="callPhone">
          <text class="icon">📞</text>
          <text class="label">电话</text>
          <text class="value">{{ student?.phone || '未填写' }}</text>
          <text class="arrow">></text>
        </view>
        <view class="contact-item">
          <text class="icon">👤</text>
          <text class="label">家长</text>
          <text class="value">{{ student?.parent_name || '未填写' }}</text>
        </view>
      </view>
    </view>

    <!-- 上课记录 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">上课记录</text>
        <text class="view-all" @click="viewAllLessons">查看全部</text>
      </view>
      <view class="lesson-list">
        <view v-for="lesson in recentLessons" :key="lesson.id" class="lesson-item">
          <view class="lesson-date">{{ formatDate(lesson.booking_date) }}</view>
          <view class="lesson-info">
            <view class="lesson-time">{{ formatTime(lesson.start_time) }} - {{ formatTime(lesson.end_time) }}</view>
            <view :class="['lesson-status', lesson.status]">{{ getStatusText(lesson.status) }}</view>
          </view>
        </view>
        <view v-if="recentLessons.length === 0" class="empty-state">
          <text>暂无上课记录</text>
        </view>
      </view>
    </view>

    <!-- 学习反馈 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">学习反馈</text>
        <text class="view-all" @click="viewAllFeedbacks">查看全部</text>
      </view>
      <view class="feedback-list">
        <view v-for="feedback in recentFeedbacks" :key="feedback.id" class="feedback-item">
          <view class="feedback-header">
            <text class="feedback-date">{{ formatDate(feedback.created_at) }}</text>
            <view class="rating">
              <text v-for="i in 5" :key="i" :class="['star', { active: i <= feedback.performance_rating }]">★</text>
            </view>
          </view>
          <view class="feedback-content">{{ feedback.content }}</view>
        </view>
        <view v-if="recentFeedbacks.length === 0" class="empty-state">
          <text>暂无学习反馈</text>
        </view>
      </view>
    </view>

    <!-- 底部操作 -->
    <view class="bottom-actions">
      <wd-button type="primary" block @click="goToFeedback">写学习反馈</wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Student {
  id: number
  name: string
  avatar: string | null
  age: number
  gender: string
  phone: string
  parent_name: string
  remaining_times: number
  total_lessons: number
  attendance_rate: number
}

interface Lesson {
  id: number
  booking_date: string
  start_time: string
  end_time: string
  status: string
}

interface Feedback {
  id: number
  created_at: string
  performance_rating: number
  content: string
}

const studentId = ref(0)
const student = ref<Student | null>(null)
const recentLessons = ref<Lesson[]>([])
const recentFeedbacks = ref<Feedback[]>([])

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function formatTime(timeStr: string): string {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
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

function callPhone() {
  if (student.value?.phone) {
    uni.makePhoneCall({
      phoneNumber: student.value.phone
    })
  }
}

function viewAllLessons() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function viewAllFeedbacks() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToFeedback() {
  if (!student.value) return
  uni.navigateTo({
    url: `/pages/students/feedback?studentId=${student.value.id}&studentName=${encodeURIComponent(student.value.name)}`
  })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}
  studentId.value = parseInt(options.id) || 0

  // 模拟数据
  student.value = {
    id: studentId.value,
    name: '小明',
    avatar: null,
    age: 10,
    gender: 'male',
    phone: '13800138000',
    parent_name: '张先生',
    remaining_times: 15,
    total_lessons: 25,
    attendance_rate: 96
  }

  const today = new Date()
  recentLessons.value = [
    { id: 1, booking_date: today.toISOString(), start_time: '09:00:00', end_time: '10:00:00', status: 'completed' },
    { id: 2, booking_date: new Date(today.getTime() - 86400000 * 3).toISOString(), start_time: '09:00:00', end_time: '10:00:00', status: 'completed' },
    { id: 3, booking_date: new Date(today.getTime() - 86400000 * 7).toISOString(), start_time: '14:00:00', end_time: '15:00:00', status: 'completed' }
  ]

  recentFeedbacks.value = [
    { id: 1, created_at: today.toISOString(), performance_rating: 5, content: '今天表现很好，动作标准度有明显提升，继续保持！' },
    { id: 2, created_at: new Date(today.getTime() - 86400000 * 7).toISOString(), performance_rating: 4, content: '基本功练习认真，但体能方面还需加强。' }
  ]
})
</script>

<style lang="scss" scoped>
.student-detail-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 140rpx;
}

.student-header {
  display: flex;
  align-items: center;
  padding: 40rpx 30rpx;
  background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
  color: #fff;

  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    border: 4rpx solid rgba(255, 255, 255, 0.5);
  }

  .student-info {
    margin-left: 24rpx;

    .name {
      font-size: 40rpx;
      font-weight: 600;
    }

    .meta {
      font-size: 26rpx;
      opacity: 0.9;
      margin-top: 8rpx;

      .divider {
        margin: 0 12rpx;
      }
    }
  }
}

.stats-card {
  display: flex;
  justify-content: space-around;
  background-color: #fff;
  margin: -20rpx 20rpx 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 40rpx;
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

.section {
  background-color: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;

    .view-all {
      font-size: 26rpx;
      color: #2196F3;
    }
  }

  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
  }
}

.contact-card {
  .contact-item {
    display: flex;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .icon {
      font-size: 36rpx;
      margin-right: 16rpx;
    }

    .label {
      font-size: 28rpx;
      color: #666;
      width: 100rpx;
    }

    .value {
      flex: 1;
      font-size: 28rpx;
      color: #333;
    }

    .arrow {
      color: #ccc;
      font-size: 28rpx;
    }
  }
}

.lesson-list {
  .lesson-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .lesson-date {
      font-size: 28rpx;
      color: #333;
    }

    .lesson-info {
      display: flex;
      align-items: center;
      gap: 16rpx;

      .lesson-time {
        font-size: 26rpx;
        color: #666;
      }

      .lesson-status {
        font-size: 24rpx;
        padding: 4rpx 12rpx;
        border-radius: 8rpx;

        &.completed {
          background-color: #E8F5E9;
          color: #4CAF50;
        }

        &.cancelled,
        &.no_show {
          background-color: #FFEBEE;
          color: #F44336;
        }
      }
    }
  }
}

.feedback-list {
  .feedback-item {
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .feedback-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12rpx;

      .feedback-date {
        font-size: 26rpx;
        color: #999;
      }

      .rating {
        .star {
          font-size: 24rpx;
          color: #ddd;

          &.active {
            color: #FFC107;
          }
        }
      }
    }

    .feedback-content {
      font-size: 28rpx;
      color: #333;
      line-height: 1.6;
    }
  }
}

.empty-state {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 28rpx;
}

.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background-color: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}
</style>
