<template>
  <view class="schedule-page">
    <!-- 日期选择器 -->
    <view class="date-picker">
      <view class="arrow" @click="prevWeek">&lt;</view>
      <view class="dates">
        <view
          v-for="date in weekDates"
          :key="date.dateStr"
          :class="['date-item', { active: selectedDate === date.dateStr, today: date.isToday }]"
          @click="selectDate(date.dateStr)"
        >
          <text class="weekday">{{ date.weekday }}</text>
          <text class="day">{{ date.day }}</text>
          <view class="dot" v-if="hasLesson(date.dateStr)"></view>
        </view>
      </view>
      <view class="arrow" @click="nextWeek">&gt;</view>
    </view>

    <!-- 课程列表 -->
    <view class="lesson-list" v-if="dayLessons.length">
      <view
        v-for="lesson in dayLessons"
        :key="lesson.id"
        class="lesson-card"
        @click="goToDetail(lesson.id)"
      >
        <view class="time-line">
          <view class="time">{{ formatTime(lesson.start_time) }}</view>
          <view class="line"></view>
          <view class="time">{{ formatTime(lesson.end_time) }}</view>
        </view>
        <view class="lesson-info">
          <view class="lesson-header">
            <text class="student-name">{{ lesson.student_name }}</text>
            <view :class="['status', lesson.status]">
              {{ getStatusText(lesson.status) }}
            </view>
          </view>
          <view class="lesson-meta">
            <text>{{ lesson.course_type === 'private' ? '私教课' : '小班课' }}</text>
          </view>
          <view class="lesson-actions" v-if="lesson.status === 'confirmed'">
            <wd-button size="small" @click.stop="completelesson(lesson)">完成课程</wd-button>
            <wd-button size="small" plain @click.stop="goToFeedback(lesson)">写反馈</wd-button>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty" v-else>
      <text class="icon">📅</text>
      <text class="text">当日暂无课程安排</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Lesson {
  id: number
  student_id: number
  student_name: string
  booking_date: string
  start_time: string
  end_time: string
  course_type: string
  status: string
}

const weekStart = ref(getWeekStart(new Date()))
const selectedDate = ref(formatDateStr(new Date()))
const lessons = ref<Lesson[]>([])

const weekDates = computed(() => {
  const dates = []
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  const today = formatDateStr(new Date())

  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart.value)
    date.setDate(date.getDate() + i)
    dates.push({
      dateStr: formatDateStr(date),
      day: date.getDate(),
      weekday: weekdays[date.getDay()],
      isToday: formatDateStr(date) === today
    })
  }
  return dates
})

const dayLessons = computed(() => {
  return lessons.value.filter(l => l.booking_date === selectedDate.value)
})

function getWeekStart(date: Date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  d.setHours(0, 0, 0, 0)
  return d
}

function formatDateStr(date: Date) {
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

function formatTime(timeStr: string) {
  return timeStr.substring(0, 5)
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
    no_show: '未到'
  }
  return map[status] || status
}

function selectDate(dateStr: string) {
  selectedDate.value = dateStr
}

function prevWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() - 7)
  weekStart.value = newStart
}

function nextWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() + 7)
  weekStart.value = newStart
}

function hasLesson(dateStr: string) {
  return lessons.value.some(l => l.booking_date === dateStr)
}

function goToDetail(id: number) {
  uni.navigateTo({ url: `/pages/schedule/detail?id=${id}` })
}

function completelesson(lesson: Lesson) {
  uni.showModal({
    title: '确认完成',
    content: '确定要标记此课程为已完成吗？',
    success: (res) => {
      if (res.confirm) {
        lesson.status = 'completed'
        uni.showToast({ title: '操作成功', icon: 'success' })
      }
    }
  })
}

function goToFeedback(lesson: Lesson) {
  uni.navigateTo({
    url: `/pages/students/feedback?studentId=${lesson.student_id}&bookingId=${lesson.id}&studentName=${encodeURIComponent(lesson.student_name)}`
  })
}

onMounted(() => {
  const today = formatDateStr(new Date())
  lessons.value = [
    { id: 1, student_id: 1, student_name: '小明', booking_date: today, start_time: '09:00:00', end_time: '10:00:00', course_type: 'private', status: 'completed' },
    { id: 2, student_id: 2, student_name: '小红', booking_date: today, start_time: '10:30:00', end_time: '11:30:00', course_type: 'private', status: 'confirmed' },
    { id: 3, student_id: 3, student_name: '小刚', booking_date: today, start_time: '14:00:00', end_time: '15:00:00', course_type: 'private', status: 'pending' }
  ]
})
</script>

<style scoped>
.schedule-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.date-picker {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 20rpx;
}

.arrow {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  color: #999;
}

.dates {
  flex: 1;
  display: flex;
  justify-content: space-around;
}

.date-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 20rpx;
  border-radius: 16rpx;
  position: relative;
}

.date-item.active {
  background: #2196F3;
}

.date-item.active .weekday,
.date-item.active .day {
  color: #fff;
}

.date-item.today .day {
  color: #2196F3;
  font-weight: bold;
}

.date-item.active.today .day {
  color: #fff;
}

.weekday {
  font-size: 24rpx;
  color: #999;
}

.day {
  font-size: 32rpx;
  color: #333;
  margin-top: 8rpx;
}

.dot {
  width: 10rpx;
  height: 10rpx;
  background: #2196F3;
  border-radius: 50%;
  position: absolute;
  bottom: 8rpx;
}

.date-item.active .dot {
  background: #fff;
}

.lesson-list {
  padding: 20rpx;
}

.lesson-card {
  display: flex;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.time-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100rpx;
}

.time-line .time {
  font-size: 26rpx;
  color: #333;
  font-weight: bold;
}

.time-line .line {
  flex: 1;
  width: 4rpx;
  background: #e0e0e0;
  margin: 10rpx 0;
}

.lesson-info {
  flex: 1;
  margin-left: 24rpx;
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.student-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.status {
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
}

.status.pending,
.status.confirmed {
  background: #E3F2FD;
  color: #2196F3;
}

.status.completed {
  background: #E8F5E9;
  color: #4CAF50;
}

.status.cancelled,
.status.no_show {
  background: #FFEBEE;
  color: #F44336;
}

.lesson-meta {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #999;
}

.lesson-actions {
  margin-top: 20rpx;
  display: flex;
  gap: 16rpx;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty .icon {
  font-size: 100rpx;
}

.empty .text {
  font-size: 28rpx;
  color: #999;
  margin-top: 20rpx;
}
</style>
