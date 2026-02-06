<template>
  <view class="student-detail-page">
    <view class="header-bg"></view>

    <view class="profile-card" v-if="student">
      <view class="profile-header">
        <image :src="student.avatar || '/static/default-avatar.png'" class="avatar" mode="aspectFill" />
        <view class="profile-info">
          <view class="name-row">
            <text class="name">{{ student.name }}</text>
            <view class="gender-tag" :class="student.gender">
              <text>{{ student.gender === 'male' ? '\u2642' : '\u2640' }}</text>
            </view>
          </view>
          <view class="meta-row">
            <text class="meta-item" v-if="student.age">{{ student.age }}{{ t.ageUnit }}</text>
            <text class="divider" v-if="student.age">|</text>
            <text class="meta-item">{{ t.parentLabel }} {{ student.parent_name || t.notFilled }}</text>
          </view>
        </view>
        <view class="call-btn" @click="callPhone" v-if="student.phone">
          <text class="icon">{{ t.callIcon }}</text>
        </view>
      </view>

      <view class="stats-row">
        <view class="stat-item">
          <view class="stat-num highlight">{{ student.remaining_times }}</view>
          <view class="stat-label">{{ t.remainingLessons }}</view>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <view class="stat-num">{{ student.total_lessons }}</view>
          <view class="stat-label">{{ t.totalLessons }}</view>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <view class="stat-num">{{ student.attendance_rate }}<text class="unit">%</text></view>
          <view class="stat-label">{{ t.attendanceRate }}</view>
        </view>
      </view>
    </view>

    <view class="info-cell-group" v-if="student">
      <view class="cell-item" @click="callPhone">
        <text class="cell-label">{{ t.phoneLabel }}</text>
        <view class="cell-content">
          <text class="cell-value">{{ student.phone || t.notFilled }}</text>
          <text class="arrow" v-if="student.phone">&gt;</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="card-title-row">
        <text class="title">{{ t.recentLessons }}</text>
        <text class="more-link" @click="viewAllLessons">{{ t.more }}</text>
      </view>
      <view class="list-container">
        <view v-for="lesson in recentLessons" :key="lesson.id" class="list-item">
          <view class="item-left">
            <text class="date">{{ formatDate(lesson.booking_date) }}</text>
            <text class="time">{{ formatTime(lesson.start_time) }}-{{ formatTime(lesson.end_time) }}</text>
          </view>
          <view :class="['status-tag', lesson.status]">{{ getStatusText(lesson.status) }}</view>
        </view>
        <view v-if="!loading && recentLessons.length === 0" class="empty-box">
          <text>{{ t.noRecords }}</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="card-title-row">
        <text class="title">{{ t.recentFeedbacks }}</text>
        <text class="more-link" @click="viewAllFeedbacks">{{ t.more }}</text>
      </view>
      <view class="list-container">
        <view v-for="feedback in recentFeedbacks" :key="feedback.id" class="feedback-item">
          <view class="feedback-top">
            <view class="rating-box">
              <text v-for="i in 5" :key="i" :class="['star', { active: i <= feedback.performance_rating }]">{{ t.star }}</text>
            </view>
            <text class="date">{{ formatDate(feedback.created_at) }}</text>
          </view>
          <view class="feedback-text">{{ feedback.content }}</view>
        </view>
        <view v-if="!loading && recentFeedbacks.length === 0" class="empty-box">
          <text>{{ t.noFeedbacks }}</text>
        </view>
      </view>
    </view>

    <view class="bottom-bar" v-if="student">
      <button class="bottom-btn" @click="goToFeedback">{{ t.writeFeedback }}</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { studentsApi, scheduleApi, feedbackApi } from '@/api/index'

interface Student {
  id: number
  name: string
  avatar: string | null
  age: number | null
  gender: string
  phone: string
  parent_name: string
  remaining_times: number
  total_lessons: number
  attendance_rate: number
}

interface Lesson {
  id: number
  student_id: number
  student_name: string
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

const t = {
  ageUnit: '\u5c81',
  parentLabel: '\u5bb6\u957f\uff1a',
  notFilled: '\u672a\u586b\u5199',
  callIcon: '\u62e8',
  remainingLessons: '\u5269\u4f59\u8bfe\u65f6',
  totalLessons: '\u7d2f\u8ba1\u4e0a\u8bfe',
  attendanceRate: '\u51fa\u52e4\u7387',
  phoneLabel: '\u8054\u7cfb\u7535\u8bdd',
  recentLessons: '\u6700\u8fd1\u8bfe\u7a0b',
  recentFeedbacks: '\u6700\u8fd1\u53cd\u9988',
  more: '\u5168\u90e8 >',
  noRecords: '\u6682\u65e0\u8bb0\u5f55',
  noFeedbacks: '\u6682\u65e0\u53cd\u9988',
  writeFeedback: '\u5199\u5b66\u4e60\u53cd\u9988',
  star: '\u2605',
  weekdaySun: '\u5468\u65e5',
  weekdayMon: '\u5468\u4e00',
  weekdayTue: '\u5468\u4e8c',
  weekdayWed: '\u5468\u4e09',
  weekdayThu: '\u5468\u56db',
  weekdayFri: '\u5468\u4e94',
  weekdaySat: '\u5468\u516d',
  monthUnit: '\u6708',
  dayUnit: '\u65e5',
  pending: '\u5f85\u786e\u8ba4',
  confirmed: '\u5df2\u786e\u8ba4',
  completed: '\u5df2\u5b8c\u6210',
  cancelled: '\u5df2\u53d6\u6d88',
  noShow: '\u672a\u5230\u573a',
  loadingFailed: '\u52a0\u8f7d\u5931\u8d25',
  functionPending: '\u529f\u80fd\u5f00\u53d1\u4e2d',
  studentDefault: '\u5b66\u5458'
} as const

const studentId = ref(0)
const student = ref<Student | null>(null)
const recentLessons = ref<Lesson[]>([])
const recentFeedbacks = ref<Feedback[]>([])
const loading = ref(false)

const weekdays = [t.weekdaySun, t.weekdayMon, t.weekdayTue, t.weekdayWed, t.weekdayThu, t.weekdayFri, t.weekdaySat]

function parseOptions() {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  return (currentPage as any).$page?.options || {}
}

function calcAge(birthDate?: string) {
  if (!birthDate) return null
  const birth = new Date(birthDate)
  if (Number.isNaN(birth.getTime())) return null
  const now = new Date()
  let age = now.getFullYear() - birth.getFullYear()
  const monthDiff = now.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birth.getDate())) {
    age -= 1
  }
  return age > 0 ? age : null
}

function normalizeStudent(raw: any): Student {
  return {
    id: Number(raw?.id || studentId.value),
    name: String(raw?.name || t.studentDefault),
    avatar: raw?.avatar || null,
    age: Number(raw?.age || 0) || calcAge(raw?.birth_date),
    gender: String(raw?.gender || 'male'),
    phone: String(raw?.phone || ''),
    parent_name: String(raw?.parent_name || raw?.guardian_name || ''),
    remaining_times: Number(raw?.remaining_times ?? raw?.remaining_lessons ?? 0),
    total_lessons: Number(raw?.total_lessons ?? raw?.completed_lessons ?? 0),
    attendance_rate: Number(raw?.attendance_rate ?? 0)
  }
}

function normalizeTime(value?: string) {
  if (!value) return ''
  if (value.includes('T')) {
    const d = new Date(value)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:00`
  }
  return value
}

function normalizeLesson(raw: any): Lesson {
  return {
    id: Number(raw?.id || 0),
    student_id: Number(raw?.student_id || 0),
    student_name: String(raw?.student_name || raw?.student?.name || t.studentDefault),
    booking_date: String(raw?.booking_date || raw?.date || '').slice(0, 10),
    start_time: normalizeTime(raw?.start_time || raw?.start_at),
    end_time: normalizeTime(raw?.end_time || raw?.end_at),
    status: String(raw?.status || 'pending')
  }
}

function normalizeFeedback(raw: any): Feedback {
  return {
    id: Number(raw?.id || 0),
    created_at: String(raw?.created_at || ''),
    performance_rating: Number(raw?.performance_rating || 0),
    content: String(raw?.content || '')
  }
}

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}${t.monthUnit}${date.getDate()}${t.dayUnit}`
}

function formatTime(timeStr: string | undefined): string {
  if (!timeStr) return '--:--'
  return timeStr.substring(0, 5)
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: t.pending,
    confirmed: t.confirmed,
    completed: t.completed,
    cancelled: t.cancelled,
    no_show: t.noShow
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
  uni.showToast({ title: t.functionPending, icon: 'none' })
}

function viewAllFeedbacks() {
  uni.showToast({ title: t.functionPending, icon: 'none' })
}

function goToFeedback() {
  if (!student.value) return
  uni.navigateTo({
    url: `/pages/students/feedback?studentId=${student.value.id}&studentName=${encodeURIComponent(student.value.name)}`
  })
}

function formatDateKey(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

async function loadStudent() {
  const data = await studentsApi.getStudent(studentId.value)
  student.value = normalizeStudent(data)
}

async function loadRecentLessons() {
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - 90)

  const data: any = await scheduleApi.getSchedule({
    start_date: formatDateKey(start),
    end_date: formatDateKey(end)
  })

  const list = (Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : [])
    .map(normalizeLesson)
    .filter(item => item.id > 0)

  recentLessons.value = list
    .filter(item => item.student_id === studentId.value || item.student_name === (student.value?.name || ''))
    .sort((a, b) => `${b.booking_date} ${b.start_time}`.localeCompare(`${a.booking_date} ${a.start_time}`))
    .slice(0, 3)
}

async function loadRecentFeedbacks() {
  const data: any = await feedbackApi.getFeedbacks({
    page: 1,
    page_size: 20,
    student_id: studentId.value
  })

  const list = (Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : [])
    .map(normalizeFeedback)
    .filter(item => item.id > 0)

  recentFeedbacks.value = list
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
    .slice(0, 3)
}

onMounted(async () => {
  const options = parseOptions()
  studentId.value = parseInt(options.id) || parseInt(options.studentId) || 0

  if (!studentId.value) return

  loading.value = true
  try {
    await loadStudent()
    await Promise.all([loadRecentLessons(), loadRecentFeedbacks()])
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadingFailed, icon: 'none' })
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
.student-detail-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 160rpx;
  position: relative;
}

.header-bg {
  height: 320rpx;
  background: linear-gradient(135deg, #ffc000 0%, #ff9500 100%);
  border-bottom-left-radius: 40rpx;
  border-bottom-right-radius: 40rpx;
}

.profile-card {
  margin: -200rpx 30rpx 24rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx 30rpx;
  box-shadow: 0 8rpx 24rpx rgba(255, 149, 0, 0.1);
  position: relative;
  z-index: 1;

  .profile-header {
    display: flex;
    align-items: center;
    margin-bottom: 40rpx;

    .avatar {
      width: 120rpx;
      height: 120rpx;
      border-radius: 60rpx;
      border: 4rpx solid #fff;
      box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
      margin-right: 24rpx;
    }

    .profile-info {
      flex: 1;

      .name-row {
        display: flex;
        align-items: center;
        margin-bottom: 8rpx;

        .name {
          font-size: 36rpx;
          font-weight: 600;
          color: #333;
          margin-right: 12rpx;
        }

        .gender-tag {
          font-size: 20rpx;
          padding: 2rpx 10rpx;
          border-radius: 20rpx;

          &.male {
            background-color: #e3f2fd;
            color: #2196f3;
          }

          &.female {
            background-color: #fce4ec;
            color: #e91e63;
          }
        }
      }

      .meta-row {
        font-size: 26rpx;
        color: #909399;

        .divider {
          margin: 0 10rpx;
          color: #eee;
        }
      }
    }

    .call-btn {
      width: 80rpx;
      height: 80rpx;
      border-radius: 40rpx;
      background-color: #fff8e1;
      display: flex;
      align-items: center;
      justify-content: center;

      .icon {
        font-size: 36rpx;
      }
    }
  }

  .stats-row {
    display: flex;
    justify-content: space-around;
    align-items: center;

    .stat-item {
      text-align: center;

      .stat-num {
        font-size: 36rpx;
        font-weight: 600;
        color: #333;
        margin-bottom: 4rpx;

        &.highlight {
          color: #ff9500;
          font-size: 40rpx;
        }

        .unit {
          font-size: 24rpx;
          font-weight: normal;
          color: #909399;
          margin-left: 2rpx;
        }
      }

      .stat-label {
        font-size: 24rpx;
        color: #909399;
      }
    }

    .stat-divider {
      width: 2rpx;
      height: 30rpx;
      background-color: #eee;
    }
  }
}

.info-cell-group {
  margin: 0 30rpx 24rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 0 30rpx;

  .cell-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx 0;

    .cell-label {
      font-size: 28rpx;
      color: #333;
    }

    .cell-content {
      display: flex;
      align-items: center;

      .cell-value {
        font-size: 28rpx;
        color: #606266;
      }

      .arrow {
        margin-left: 10rpx;
        color: #c0c4cc;
        font-size: 26rpx;
      }
    }
  }
}

.section-card {
  margin: 0 30rpx 24rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;

  .card-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;

    .title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
      padding-left: 16rpx;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 6rpx;
        height: 24rpx;
        background-color: #ff9500;
        border-radius: 4rpx;
      }
    }

    .more-link {
      font-size: 24rpx;
      color: #909399;
    }
  }

  .list-container {
    .list-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20rpx 0;
      border-bottom: 1rpx solid #f5f7fa;

      &:last-child {
        border-bottom: none;
      }

      .item-left {
        display: flex;
        flex-direction: column;

        .date {
          font-size: 28rpx;
          color: #333;
          margin-bottom: 4rpx;
        }

        .time {
          font-size: 24rpx;
          color: #909399;
        }
      }

      .status-tag {
        font-size: 24rpx;
        padding: 4rpx 16rpx;
        border-radius: 8rpx;

        &.completed {
          background-color: rgba(76, 175, 80, 0.1);
          color: #4caf50;
        }

        &.pending,
        &.confirmed {
          background-color: rgba(255, 149, 0, 0.1);
          color: #ff9500;
        }

        &.cancelled,
        &.no_show {
          background-color: rgba(244, 67, 54, 0.1);
          color: #f44336;
        }
      }
    }

    .feedback-item {
      padding: 24rpx 0;
      border-bottom: 1rpx solid #f5f7fa;

      &:last-child {
        border-bottom: none;
        padding-bottom: 0;
      }

      .feedback-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12rpx;

        .rating-box {
          .star {
            color: #e4e7ed;
            font-size: 24rpx;
            margin-right: 4rpx;

            &.active {
              color: #ffc107;
            }
          }
        }

        .date {
          font-size: 24rpx;
          color: #c0c4cc;
        }
      }

      .feedback-text {
        font-size: 28rpx;
        color: #606266;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        overflow: hidden;
      }
    }
  }

  .empty-box {
    padding: 30rpx 0;
    text-align: center;
    color: #909399;
    font-size: 26rpx;
  }
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.bottom-btn {
  width: 100%;
  border: none;
  border-radius: 44rpx;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #ffbc47, #ff8d1f);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  box-shadow: 0 6rpx 16rpx rgba(255, 149, 0, 0.25);
}

.bottom-btn::after {
  border: none;
}
</style>
