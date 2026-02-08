<template>
  <view class="schedule-page">
    <view class="calendar-card">
      <view class="calendar-head">
        <view class="switch-btn" @click="prevWeek">&lt;</view>
        <view class="month-title">{{ currentMonthLabel }}</view>
        <view class="switch-btn" @click="nextWeek">&gt;</view>
      </view>

      <view class="week-row">
        <view
          class="day-item"
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
    </view>

    <view class="schedule-list" v-if="daySchedules.length">
      <view class="schedule-card" v-for="schedule in daySchedules" :key="schedule.id">
        <view class="time-line">
          <text class="time-main">{{ formatTime(schedule.start_time) }}</text>
          <view class="time-divider"></view>
          <text class="time-sub">{{ formatTime(schedule.end_time) }}</text>
        </view>

        <view class="course-info">
          <view class="course-head">
            <text class="course-name">{{ schedule.course?.name || schedule.course_name || '课程' }}</text>
            <view class="status" :class="schedule.status">{{ getStatusText(schedule.status) }}</view>
          </view>

          <view class="course-meta">
            <text>教练：{{ schedule.coach_name || '待定' }}</text>
            <text>场馆：{{ schedule.venue_name || '待定' }}</text>
            <text>人数：{{ schedule.enrolled_count || 0 }}/{{ schedule.capacity || '-' }}</text>
          </view>

          <view class="course-actions">
            <button
              class="action-btn primary"
              v-if="schedule.status === 'scheduled' && !isEnrolled(schedule)"
              @click="enrollSchedule(schedule)"
            >报名</button>

            <button
              class="action-btn success"
              v-if="isEnrolled(schedule) && canCheckin(schedule)"
              @click="checkinSchedule(schedule)"
            >签到</button>

            <text class="enrolled-text" v-if="isEnrolled(schedule)">已报名</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <view class="empty-icon">课</view>
      <text class="empty-title">当天暂无课程安排</text>
      <text class="empty-sub">去预约一节新课程吧</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { scheduleApi } from '@/api'

const userStore = useUserStore()

const weekStart = ref(getWeekStart(new Date()))
const selectedDate = ref(formatDateStr(new Date()))
const schedules = ref<any[]>([])
const enrolledIds = ref<number[]>([])

const weekDates = computed(() => {
  const dates = []
  const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const today = formatDateStr(new Date())

  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart.value)
    date.setDate(date.getDate() + i)
    const dateStr = formatDateStr(date)
    dates.push({
      dateStr,
      day: date.getDate(),
      weekday: weekdays[(date.getDay() + 6) % 7],
      isToday: dateStr === today
    })
  }
  return dates
})

const currentMonthLabel = computed(() => {
  const date = new Date(selectedDate.value)
  return `${date.getMonth() + 1}月课程表`
})

const daySchedules = computed(() => {
  return schedules.value.filter(schedule => getScheduleDate(schedule) === selectedDate.value)
})

onMounted(async () => {
  await loadSchedules()
})

function getWeekStart(date: Date) {
  const d = new Date(date)
  const day = d.getDay() || 7
  d.setDate(d.getDate() - day + 1)
  d.setHours(0, 0, 0, 0)
  return d
}

function formatDateStr(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function getScheduleDate(schedule: any): string {
  if (schedule?.booking_date) return schedule.booking_date.slice(0, 10)
  if (schedule?.date) return schedule.date.slice(0, 10)
  if (typeof schedule?.start_time === 'string' && schedule.start_time.includes('T')) {
    return schedule.start_time.slice(0, 10)
  }
  return ''
}

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

function selectDate(dateStr: string) {
  selectedDate.value = dateStr
}

function prevWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() - 7)
  weekStart.value = newStart
  loadSchedules()
}

function nextWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() + 7)
  weekStart.value = newStart
  loadSchedules()
}

function hasSchedule(dateStr: string) {
  return schedules.value.some(schedule => getScheduleDate(schedule) === dateStr)
}

function formatTime(timeStr: string) {
  if (!timeStr) return '--:--'
  if (timeStr.includes('T')) {
    const date = new Date(timeStr)
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  }
  return timeStr.slice(0, 5)
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    scheduled: '待上课',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

function isEnrolled(schedule: any) {
  return enrolledIds.value.includes(schedule.id)
}

function canCheckin(schedule: any) {
  if (!schedule?.start_time) return false
  const start = schedule.start_time.includes('T')
    ? new Date(schedule.start_time)
    : new Date(`${selectedDate.value}T${schedule.start_time}`)
  const now = new Date()
  const diff = start.getTime() - now.getTime()
  return diff <= 30 * 60 * 1000 && diff >= -60 * 60 * 1000
}

async function enrollSchedule(schedule: any) {
  if (!userStore.currentStudent) {
    uni.showToast({ title: '请先登录或选择学员', icon: 'none' })
    return
  }

  try {
    await scheduleApi.enroll(schedule.id, userStore.currentStudent.id)
    enrolledIds.value.push(schedule.id)
    schedule.enrolled_count = (schedule.enrolled_count || 0) + 1
    uni.showToast({ title: '报名成功', icon: 'success' })
  } catch (error: any) {
    uni.showToast({ title: error.message || '报名失败', icon: 'none' })
  }
}

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
.schedule-page {
  min-height: 100vh;
  background: #FFFBF5;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.calendar-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 18rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  animation: fadeUp 0.3s ease-out;
}

.calendar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14rpx;
}

.switch-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 16rpx;
  background: #f4f6fb;
  color: #738099;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.month-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2533;
}

.week-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8rpx;
}

.day-item {
  border-radius: 16rpx;
  padding: 10rpx 6rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.day-item.active {
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  box-shadow: 0 8rpx 16rpx rgba(255, 145, 32, 0.28);
}

.weekday {
  font-size: 20rpx;
  color: #97a2b6;
}

.day {
  margin-top: 6rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #26314a;
}

.day-item.today .day {
  color: #ff8d1f;
}

.day-item.active .weekday,
.day-item.active .day {
  color: #fff;
}

.dot {
  position: absolute;
  bottom: 8rpx;
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: #ff8d1f;
}

.day-item.active .dot {
  background: #fff;
}

.schedule-list {
  margin-top: 14rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.schedule-card {
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  padding: 18rpx;
  display: flex;
  gap: 14rpx;
  animation: slideInRight 0.3s ease-out;
  animation-fill-mode: both;
  transition: all 0.2s ease;
}

.schedule-card:nth-child(1) { animation-delay: 0.05s; }
.schedule-card:nth-child(2) { animation-delay: 0.1s; }
.schedule-card:nth-child(3) { animation-delay: 0.15s; }
.schedule-card:nth-child(4) { animation-delay: 0.2s; }

.schedule-card:active {
  transform: scale(0.99);
}

.time-line {
  width: 96rpx;
  border-radius: 14rpx;
  background: #FFF7ED;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  padding: 10rpx 6rpx;
}

.time-main {
  font-size: 28rpx;
  font-weight: 700;
  color: #1f2533;
}

.time-divider {
  width: 2rpx;
  height: 20rpx;
  background: #e8dfd0;
}

.time-sub {
  font-size: 22rpx;
  color: #9099ab;
}

.course-info {
  flex: 1;
}

.course-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10rpx;
}

.course-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1f2533;
}

.status {
  font-size: 21rpx;
  border-radius: 999rpx;
  padding: 6rpx 14rpx;
}

.status.scheduled {
  color: #df7f17;
  background: #fff1df;
}

.status.ongoing {
  color: #278ad6;
  background: #e8f4ff;
}

.status.completed {
  color: #239458;
  background: #e6f5eb;
}

.status.cancelled {
  color: #cc5c4e;
  background: #ffebe8;
}

.course-meta {
  margin-top: 10rpx;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  font-size: 22rpx;
  color: #8c95aa;
}

.course-actions {
  margin-top: 12rpx;
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.action-btn {
  border: none;
  border-radius: 999rpx;
  padding: 10rpx 22rpx;
  line-height: 1;
  font-size: 22rpx;
  color: #fff;
}

.action-btn::after {
  border: none;
}

.action-btn.primary {
  background: linear-gradient(135deg, #ffbe4d, #ff9422);
}

.action-btn.success {
  background: linear-gradient(135deg, #30b06b, #219357);
}

.enrolled-text {
  font-size: 22rpx;
  color: #8e97aa;
}

.empty-state {
  margin-top: 14rpx;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  padding: 56rpx 24rpx;
  text-align: center;
  animation: fadeUp 0.3s ease-out 0.1s both;
}

.empty-icon {
  width: 88rpx;
  height: 88rpx;
  margin: 0 auto;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #fff1dd, #ffdcb9);
  color: #ff8d1f;
  font-size: 36rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-title {
  display: block;
  margin-top: 16rpx;
  font-size: 28rpx;
  color: #4f5870;
}

.empty-sub {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #99a1b2;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(20rpx); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
