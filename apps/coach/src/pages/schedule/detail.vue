<template>
  <view class="detail-page">
    <view class="nav-bg"></view>

    <view class="content-wrapper">
      <view class="info-card">
        <view class="card-header">
          <text class="title">{{ t.detailTitle }}</text>
          <view :class="['status-badge', booking?.status]">
            {{ getStatusText(booking?.status) }}
          </view>
        </view>

        <view class="info-list">
          <view class="info-item">
            <text class="label">{{ t.studentName }}</text>
            <view class="value-box">
              <text class="value highlight">{{ booking?.student_name || '--' }}</text>
            </view>
          </view>

          <view class="info-item">
            <text class="label">{{ t.lessonDate }}</text>
            <text class="value">{{ formatDate(booking?.booking_date) }}</text>
          </view>

          <view class="info-item">
            <text class="label">{{ t.lessonTime }}</text>
            <text class="value time-value">{{ formatTime(booking?.start_time) }} - {{ formatTime(booking?.end_time) }}</text>
          </view>

          <view class="info-item">
            <text class="label">{{ t.courseType }}</text>
            <text class="value">{{ booking?.course_type === 'private' ? t.privateCourse : t.groupCourse }}</text>
          </view>
        </view>
      </view>

      <view class="action-section" v-if="booking?.status === 'confirmed'">
        <button class="action-btn primary" @click="completeBooking">{{ t.completeLesson }}</button>
        <button class="action-btn secondary" @click="goToFeedback">{{ t.writeFeedback }}</button>
      </view>

      <view class="state-wrap" v-if="loading">
        <text class="state-text">{{ t.loading }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { scheduleApi } from '@/api/index'

interface Booking {
  id: number
  student_id: number
  student_name: string
  booking_date: string
  start_time: string
  end_time: string
  course_type: string
  status: string
}

const t = {
  detailTitle: '\u8bfe\u7a0b\u8be6\u60c5',
  studentName: '\u5b66\u5458\u59d3\u540d',
  lessonDate: '\u4e0a\u8bfe\u65e5\u671f',
  lessonTime: '\u4e0a\u8bfe\u65f6\u95f4',
  courseType: '\u8bfe\u7a0b\u7c7b\u578b',
  privateCourse: '\u79c1\u6559\u8bfe',
  groupCourse: '\u5c0f\u73ed\u8bfe',
  completeLesson: '\u5b8c\u6210\u8bfe\u7a0b',
  writeFeedback: '\u5199\u5b66\u4e60\u53cd\u9988',
  loading: '\u52a0\u8f7d\u4e2d...',
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
  completeConfirmTitle: '\u786e\u8ba4\u5b8c\u6210',
  completeConfirmText: '\u786e\u5b9a\u8981\u6807\u8bb0\u6b64\u8bfe\u7a0b\u4e3a\u5df2\u5b8c\u6210\u5417\uff1f',
  completeSuccess: '\u64cd\u4f5c\u6210\u529f',
  completeFailed: '\u64cd\u4f5c\u5931\u8d25',
  loadFailed: '\u52a0\u8f7d\u8be6\u60c5\u5931\u8d25',
  studentDefault: '\u5b66\u5458'
} as const

const bookingId = ref(0)
const booking = ref<Booking | null>(null)
const loading = ref(false)

const weekdays = [t.weekdaySun, t.weekdayMon, t.weekdayTue, t.weekdayWed, t.weekdayThu, t.weekdayFri, t.weekdaySat]

function parseOptions() {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  return (currentPage as any).$page?.options || {}
}

function normalizeTime(value?: string) {
  if (!value) return ''
  if (value.includes('T')) {
    const d = new Date(value)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:00`
  }
  return value
}

function normalizeBooking(raw: any): Booking {
  return {
    id: Number(raw?.id || bookingId.value),
    student_id: Number(raw?.student_id || 0),
    student_name: String(raw?.student_name || raw?.student?.name || t.studentDefault),
    booking_date: String(raw?.booking_date || raw?.date || '').slice(0, 10),
    start_time: normalizeTime(raw?.start_time || raw?.start_at),
    end_time: normalizeTime(raw?.end_time || raw?.end_at),
    course_type: String(raw?.course_type || 'private'),
    status: String(raw?.status || 'pending')
  }
}

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}${t.monthUnit}${date.getDate()}${t.dayUnit} ${weekdays[date.getDay()]}`
}

function formatTime(timeStr: string | undefined): string {
  if (!timeStr) return '--:--'
  return timeStr.substring(0, 5)
}

function getStatusText(status: string | undefined): string {
  if (!status) return ''
  const map: Record<string, string> = {
    pending: t.pending,
    confirmed: t.confirmed,
    completed: t.completed,
    cancelled: t.cancelled,
    no_show: t.noShow
  }
  return map[status] || status
}

async function loadBookingDetail() {
  if (!bookingId.value) return
  loading.value = true
  try {
    const data = await scheduleApi.getBookingDetail(bookingId.value)
    booking.value = normalizeBooking(data)
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadFailed, icon: 'none' })
  } finally {
    loading.value = false
  }
}

function completeBooking() {
  if (!booking.value) return

  uni.showModal({
    title: t.completeConfirmTitle,
    content: t.completeConfirmText,
    success: async (res) => {
      if (!res.confirm || !booking.value) return
      try {
        await scheduleApi.completeBooking(booking.value.id)
        booking.value.status = 'completed'
        uni.showToast({ title: t.completeSuccess, icon: 'success' })
      } catch (error: any) {
        uni.showToast({ title: error.message || t.completeFailed, icon: 'none' })
      }
    }
  })
}

function goToFeedback() {
  if (!booking.value) return
  uni.navigateTo({
    url: `/pages/students/feedback?studentId=${booking.value.student_id}&bookingId=${booking.value.id}&studentName=${encodeURIComponent(booking.value.student_name)}`
  })
}

onMounted(async () => {
  const options = parseOptions()
  bookingId.value = parseInt(options.id) || 0

  if (!bookingId.value) {
    return
  }

  const hasInline = options.studentName || options.bookingDate
  if (hasInline) {
    booking.value = normalizeBooking({
      id: bookingId.value,
      student_id: Number(options.studentId || 0),
      student_name: decodeURIComponent(options.studentName || ''),
      booking_date: options.bookingDate,
      start_time: decodeURIComponent(options.startTime || ''),
      end_time: decodeURIComponent(options.endTime || ''),
      course_type: options.courseType,
      status: options.status
    })
  }

  await loadBookingDetail()
})
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  position: relative;

  .nav-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 300rpx;
    background: linear-gradient(135deg, #ffc000 0%, #ff9500 100%);
    border-bottom-left-radius: 40rpx;
    border-bottom-right-radius: 40rpx;
    z-index: 0;
  }
}

.content-wrapper {
  position: relative;
  z-index: 1;
  padding: 40rpx 30rpx;
}

.info-card {
  background-color: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(255, 149, 0, 0.1);
  margin-top: 20rpx;
  animation: fadeInUp 0.6s ease-out;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40rpx;
    padding-bottom: 20rpx;
    border-bottom: 2rpx dashed #eee;

    .title {
      font-size: 34rpx;
      font-weight: 600;
      color: #333;
    }
  }

  .status-badge {
    padding: 6rpx 20rpx;
    border-radius: 30rpx;
    font-size: 24rpx;
    font-weight: 500;

    &.pending,
    &.confirmed {
      background-color: rgba(255, 149, 0, 0.1);
      color: #ff9500;
    }

    &.completed {
      background-color: rgba(76, 175, 80, 0.1);
      color: #4caf50;
    }

    &.cancelled,
    &.no_show {
      background-color: rgba(244, 67, 54, 0.1);
      color: #f44336;
    }
  }

  .info-list {
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 32rpx;

      &:last-child {
        margin-bottom: 0;
      }

      .label {
        font-size: 28rpx;
        color: #909399;
      }

      .value {
        font-size: 30rpx;
        color: #333;
        font-weight: 500;

        &.highlight {
          font-size: 32rpx;
          color: #333;
          font-weight: 600;
        }

        &.time-value {
          font-family: 'DIN Alternate', sans-serif;
          font-size: 32rpx;
          color: #ff9500;
        }
      }
    }
  }
}

.action-section {
  margin-top: 60rpx;
  padding: 0 10rpx;
}

.action-btn {
  width: 100%;
  border: none;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 88rpx;
  height: 88rpx;
  margin-bottom: 24rpx;
}

.action-btn::after {
  border: none;
}

.action-btn.primary {
  color: #fff;
  background: linear-gradient(135deg, #ffbc47, #ff8d1f);
  box-shadow: 0 6rpx 16rpx rgba(255, 149, 0, 0.25);
}

.action-btn.secondary {
  color: #606266;
  background: #fff;
  border: 2rpx solid #e4e7ed;
}

.state-wrap {
  margin-top: 20rpx;
  text-align: center;
}

.state-text {
  font-size: 24rpx;
  color: #909399;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
