<template>
  <view class="page">
    <!-- 日期选择器 -->
    <view class="date-picker">
      <view class="arrow" @click="prevWeek">&lt;</view>
      <view class="dates">
        <view
          class="date-item"
          v-for="date in weekDates"
          :key="date.dateStr"
          :class="{ active: selectedDate === date.dateStr, today: date.isToday }"
          @click="selectDate(date.dateStr)"
        >
          <text class="weekday">{{ date.weekday }}</text>
          <text class="day">{{ date.day }}</text>
          <view class="dot" v-if="hasSchedule(date.dateStr)"></view>
        </view>
      </view>
      <view class="arrow" @click="nextWeek">&gt;</view>
    </view>

    <!-- 课程列表 -->
    <view class="schedule-list" v-if="daySchedules.length">
      <view class="schedule-card" v-for="schedule in daySchedules" :key="schedule.id">
        <view class="time-line">
          <view class="time">{{ formatTime(schedule.start_time) }}</view>
          <view class="line"></view>
          <view class="time">{{ formatTime(schedule.end_time) }}</view>
        </view>
        <view class="course-info">
          <view class="course-header">
            <text class="course-name">{{ schedule.course?.name || '课程' }}</text>
            <view class="status" :class="schedule.status">
              {{ getStatusText(schedule.status) }}
            </view>
          </view>
          <view class="course-details">
            <text class="detail">教练: {{ schedule.coach_name || '待定' }}</text>
            <text class="detail">场地: {{ schedule.venue_name || '待定' }}</text>
            <text class="detail">人数: {{ schedule.enrolled_count }}/{{ schedule.capacity }}</text>
          </view>
          <view class="course-actions">
            <button
              class="btn-enroll"
              v-if="schedule.status === 'scheduled' && !isEnrolled(schedule)"
              @click="enrollSchedule(schedule)"
            >
              报名
            </button>
            <button
              class="btn-checkin"
              v-if="isEnrolled(schedule) && canCheckin(schedule)"
              @click="checkinSchedule(schedule)"
            >
              签到
            </button>
            <text class="enrolled-text" v-if="isEnrolled(schedule)">已报名</text>
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
import { useUserStore } from '@/stores/user'
import { scheduleApi } from '@/api'

const userStore = useUserStore()

// 当前周的起始日期
const weekStart = ref(getWeekStart(new Date()))
const selectedDate = ref(formatDateStr(new Date()))
const schedules = ref<any[]>([])
const enrolledIds = ref<number[]>([])

// 计算当前周的日期
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

// 当天的课程
const daySchedules = computed(() => {
  return schedules.value.filter(s => {
    const scheduleDate = formatDateStr(new Date(s.start_time))
    return scheduleDate === selectedDate.value
  })
})

onMounted(async () => {
  await loadSchedules()
})

// 获取周一日期
function getWeekStart(date: Date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  d.setHours(0, 0, 0, 0)
  return d
}

// 格式化日期字符串
function formatDateStr(date: Date) {
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

// 加载课程
async function loadSchedules() {
  try {
    const startDate = new Date(weekStart.value)
    const endDate = new Date(weekStart.value)
    endDate.setDate(endDate.getDate() + 7)

    const res = await scheduleApi.list({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    })
    schedules.value = res || []
  } catch (error) {
    console.error('加载课程失败', error)
  }
}

// 选择日期
function selectDate(dateStr: string) {
  selectedDate.value = dateStr
}

// 上一周
function prevWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() - 7)
  weekStart.value = newStart
  loadSchedules()
}

// 下一周
function nextWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() + 7)
  weekStart.value = newStart
  loadSchedules()
}

// 是否有课程
function hasSchedule(dateStr: string) {
  return schedules.value.some(s => {
    const scheduleDate = formatDateStr(new Date(s.start_time))
    return scheduleDate === dateStr
  })
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

// 是否已报名
function isEnrolled(schedule: any) {
  return enrolledIds.value.includes(schedule.id)
}

// 是否可签到
function canCheckin(schedule: any) {
  const now = new Date()
  const start = new Date(schedule.start_time)
  const diff = start.getTime() - now.getTime()
  // 开课前30分钟可签到
  return diff <= 30 * 60 * 1000 && diff >= -60 * 60 * 1000
}

// 报名
async function enrollSchedule(schedule: any) {
  if (!userStore.currentStudent) {
    uni.showToast({ title: '请先绑定学员', icon: 'none' })
    return
  }

  try {
    await scheduleApi.enroll(schedule.id, userStore.currentStudent.id)
    enrolledIds.value.push(schedule.id)
    schedule.enrolled_count++
    uni.showToast({ title: '报名成功', icon: 'success' })
  } catch (error: any) {
    uni.showToast({ title: error.message || '报名失败', icon: 'none' })
  }
}

// 签到
async function checkinSchedule(schedule: any) {
  if (!userStore.currentStudent) return

  try {
    await scheduleApi.checkin(schedule.id, userStore.currentStudent.id)
    uni.showToast({ title: '签到成功', icon: 'success' })
  } catch (error: any) {
    uni.showToast({ title: error.message || '签到失败', icon: 'none' })
  }
}
</script>

<style scoped>
.page {
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
  background: #4CAF50;
}

.date-item.active .weekday,
.date-item.active .day {
  color: #fff;
}

.date-item.today .day {
  color: #4CAF50;
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
  background: #4CAF50;
  border-radius: 50%;
  position: absolute;
  bottom: 8rpx;
}

.date-item.active .dot {
  background: #fff;
}

.schedule-list {
  padding: 20rpx;
}

.schedule-card {
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

.course-info {
  flex: 1;
  margin-left: 24rpx;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.status {
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
}

.status.scheduled {
  background: #E8F5E9;
  color: #4CAF50;
}

.status.ongoing {
  background: #FFF3E0;
  color: #FF9800;
}

.status.completed {
  background: #E3F2FD;
  color: #2196F3;
}

.status.cancelled {
  background: #FFEBEE;
  color: #F44336;
}

.course-details {
  margin-top: 16rpx;
}

.detail {
  font-size: 24rpx;
  color: #999;
  margin-right: 20rpx;
}

.course-actions {
  margin-top: 20rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.btn-enroll,
.btn-checkin {
  padding: 12rpx 40rpx;
  border-radius: 30rpx;
  font-size: 26rpx;
  border: none;
}

.btn-enroll {
  background: #4CAF50;
  color: #fff;
}

.btn-checkin {
  background: #FF9800;
  color: #fff;
}

.enrolled-text {
  font-size: 26rpx;
  color: #4CAF50;
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
