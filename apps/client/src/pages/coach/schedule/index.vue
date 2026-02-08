<template>
  <view class="schedule-page">
    <view class="calendar-card">
      <view class="calendar-head">
        <text class="month">{{ currentMonth }}</text>
        <view class="week-switch">
          <view class="switch-btn" hover-class="switch-btn-active" @click="prevWeek">&lt;</view>
          <view class="switch-btn" hover-class="switch-btn-active" @click="nextWeek">&gt;</view>
        </view>
      </view>

      <view class="week-row">
        <view
          v-for="date in weekDates"
          :key="date.dateStr"
          :class="['day-item', { active: selectedDate === date.dateStr, today: date.isToday }]"
          @click="selectDate(date.dateStr)"
        >
          <text class="weekday">{{ date.weekday }}</text>
          <text class="day">{{ date.day }}</text>
          <view v-if="hasLesson(date.dateStr)" class="dot"></view>
        </view>
      </view>
    </view>

    <view v-if="loading" class="state-wrap loading-wrap">
      <text class="state-text">{{ t.loading }}</text>
    </view>

    <view class="list-wrap" v-else-if="dayLessons.length">
      <view class="date-tip">
        <text>{{ selectedDateLabel }}</text>
        <text class="count">{{ dayLessons.length }} {{ t.lessonUnit }}</text>
      </view>

      <view
        v-for="lesson in dayLessons"
        :key="lesson.id"
        class="lesson-card"
        @click="goToDetail(lesson)"
      >
        <view class="lesson-main">
          <view class="time-col">
            <text class="time-main">{{ formatTime(lesson.start_time) }}</text>
            <text class="time-sub">{{ formatTime(lesson.end_time) }}</text>
          </view>

          <view class="lesson-info">
            <view class="info-top">
              <text class="student">{{ lesson.student_name }}</text>
              <text class="course-tag">{{ lesson.course_type === 'private' ? t.privateCourse : t.groupCourse }}</text>
            </view>
            <view class="info-bottom">
              <text :class="['status-pill', lesson.status]">{{ getStatusText(lesson.status) }}</text>
            </view>
            <view class="actions" v-if="lesson.status === 'confirmed'">
              <button class="action-btn ghost" @click.stop="completeLesson(lesson)">{{ t.completeLesson }}</button>
              <button class="action-btn outline" @click.stop="goToFeedback(lesson)">{{ t.writeFeedback }}</button>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view v-else class="empty">
      <view class="empty-icon">{{ t.scheduleIcon }}</view>
      <text class="empty-title">{{ t.emptyTitle }}</text>
      <text class="empty-sub">{{ t.emptySub }}</text>
      <button class="action-btn ghost" @click="goToSlots">{{ t.goSchedule }}</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { coachScheduleApi } from '@/api/index'

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

const t = {
  loading: '\u52a0\u8f7d\u4e2d...',
  lessonUnit: '\u8282\u8bfe',
  privateCourse: '\u79c1\u6559\u8bfe',
  groupCourse: '\u56e2\u8bfe',
  completeLesson: '\u5b8c\u6210\u8bfe\u7a0b',
  writeFeedback: '\u5199\u53cd\u9988',
  scheduleIcon: '\u6392',
  emptyTitle: '\u5f53\u5929\u6682\u65e0\u8bfe\u7a0b\u5b89\u6392',
  emptySub: '\u53ef\u53bb\u8bbe\u7f6e\u65b0\u7684\u53ef\u7ea6\u65f6\u6bb5',
  goSchedule: '\u53bb\u6392\u8bfe',
  weekdayMon: '\u4e00',
  weekdayTue: '\u4e8c',
  weekdayWed: '\u4e09',
  weekdayThu: '\u56db',
  weekdayFri: '\u4e94',
  weekdaySat: '\u516d',
  weekdaySun: '\u65e5',
  weekdaySunFull: '\u5468\u65e5',
  weekdayMonFull: '\u5468\u4e00',
  weekdayTueFull: '\u5468\u4e8c',
  weekdayWedFull: '\u5468\u4e09',
  weekdayThuFull: '\u5468\u56db',
  weekdayFriFull: '\u5468\u4e94',
  weekdaySatFull: '\u5468\u516d',
  pending: '\u5f85\u786e\u8ba4',
  confirmed: '\u5df2\u786e\u8ba4',
  completed: '\u5df2\u5b8c\u6210',
  cancelled: '\u5df2\u53d6\u6d88',
  noShow: '\u672a\u5230\u573a',
  monthUnit: '\u6708',
  yearUnit: '\u5e74',
  dayUnit: '\u65e5',
  completeConfirmTitle: '\u786e\u8ba4\u5b8c\u8bfe',
  completeConfirmText: '\u786e\u5b9a\u5c06\u8fd9\u8282\u8bfe\u7a0b\u6807\u8bb0\u4e3a\u5df2\u5b8c\u6210\u5417\uff1f',
  completeSuccess: '\u64cd\u4f5c\u6210\u529f',
  completeFailed: '\u64cd\u4f5c\u5931\u8d25',
  loadFailed: '\u52a0\u8f7d\u8bfe\u8868\u5931\u8d25'
} as const

const weekStart = ref(getWeekStart(new Date()))
const selectedDate = ref(formatDateStr(new Date()))
const lessons = ref<Lesson[]>([])
const loading = ref(false)

const currentMonth = computed(() => {
  const d = new Date(weekStart.value)
  return `${d.getFullYear()}${t.yearUnit}${d.getMonth() + 1}${t.monthUnit}`
})

const selectedDateLabel = computed(() => {
  const d = new Date(selectedDate.value)
  const weekdays = [t.weekdaySunFull, t.weekdayMonFull, t.weekdayTueFull, t.weekdayWedFull, t.weekdayThuFull, t.weekdayFriFull, t.weekdaySatFull]
  return `${d.getMonth() + 1}${t.monthUnit}${d.getDate()}${t.dayUnit} ${weekdays[d.getDay()]}`
})

const weekDates = computed(() => {
  const dates = []
  const weekdays = [t.weekdayMon, t.weekdayTue, t.weekdayWed, t.weekdayThu, t.weekdayFri, t.weekdaySat, t.weekdaySun]
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

const dayLessons = computed(() => {
  return lessons.value.filter(lesson => lesson.booking_date === selectedDate.value)
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
  return `${date.getFullYear()}-${(date.getMonth() + 1)
    .toString()
    .padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

function getDatePart(value: string) {
  if (!value) return ''
  return value.includes('T') ? value.slice(0, 10) : value.slice(0, 10)
}

function normalizeTime(value: any) {
  if (!value) return ''
  const text = String(value)
  if (text.includes('T')) {
    const d = new Date(text)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:00`
  }
  return text
}

function normalizeLesson(raw: any): Lesson {
  const start = normalizeTime(raw?.start_time || raw?.start_at)
  const end = normalizeTime(raw?.end_time || raw?.end_at)
  const date = getDatePart(raw?.booking_date || raw?.date || raw?.start_time || '')

  return {
    id: Number(raw?.id || 0),
    student_id: Number(raw?.student_id || 0),
    student_name: String(raw?.student_name || raw?.student?.name || '\u5b66\u5458'),
    booking_date: date,
    start_time: start,
    end_time: end,
    course_type: String(raw?.course_type || 'private'),
    status: String(raw?.status || 'pending')
  }
}

function normalizeList(data: any): Lesson[] {
  const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
  return list.map(normalizeLesson).filter(item => item.id > 0 && item.booking_date)
}

function formatTime(timeStr: string) {
  if (!timeStr) return '--:--'
  return timeStr.substring(0, 5)
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending: t.pending,
    confirmed: t.confirmed,
    completed: t.completed,
    cancelled: t.cancelled,
    no_show: t.noShow
  }
  return map[status] || status
}

async function loadWeekLessons() {
  loading.value = true
  try {
    const start = new Date(weekStart.value)
    const end = new Date(weekStart.value)
    end.setDate(end.getDate() + 6)

    const data = await coachScheduleApi.getSchedule({
      start_date: formatDateStr(start),
      end_date: formatDateStr(end)
    })

    lessons.value = normalizeList(data)
  } catch (error: any) {
    lessons.value = []
    uni.showToast({ title: error.message || t.loadFailed, icon: 'none' })
  } finally {
    loading.value = false
  }
}

function selectDate(dateStr: string) {
  selectedDate.value = dateStr
}

async function prevWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() - 7)
  weekStart.value = newStart
  selectedDate.value = formatDateStr(newStart)
  await loadWeekLessons()
}

async function nextWeek() {
  const newStart = new Date(weekStart.value)
  newStart.setDate(newStart.getDate() + 7)
  weekStart.value = newStart
  selectedDate.value = formatDateStr(newStart)
  await loadWeekLessons()
}

function hasLesson(dateStr: string) {
  return lessons.value.some(lesson => lesson.booking_date === dateStr)
}

function goToDetail(lesson: Lesson) {
  const query = [
    `id=${lesson.id}`,
    `studentId=${lesson.student_id}`,
    `studentName=${encodeURIComponent(lesson.student_name)}`,
    `bookingDate=${lesson.booking_date}`,
    `startTime=${encodeURIComponent(lesson.start_time)}`,
    `endTime=${encodeURIComponent(lesson.end_time)}`,
    `courseType=${lesson.course_type}`,
    `status=${lesson.status}`
  ]
  uni.navigateTo({ url: `/pages/coach/schedule/detail?${query.join('&')}` })
}

function goToSlots() {
  uni.navigateTo({ url: '/pages/coach/slots/manage' })
}

function completeLesson(lesson: Lesson) {
  uni.showModal({
    title: t.completeConfirmTitle,
    content: t.completeConfirmText,
    success: async (res) => {
      if (!res.confirm) return
      try {
        await coachScheduleApi.completeBooking(lesson.id)
        lesson.status = 'completed'
        uni.showToast({ title: t.completeSuccess, icon: 'success' })
      } catch (error: any) {
        uni.showToast({ title: error.message || t.completeFailed, icon: 'none' })
      }
    }
  })
}

function goToFeedback(lesson: Lesson) {
  uni.navigateTo({
    url: `/pages/coach/students/feedback?studentId=${lesson.student_id}&bookingId=${lesson.id}&studentName=${encodeURIComponent(lesson.student_name)}`
  })
}

onMounted(async () => {
  await loadWeekLessons()
})
</script>

<style scoped>
.schedule-page {
  min-height: 100vh;
  background: #FFFBF5;
  padding: 22rpx;
  padding-bottom: calc(120rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.calendar-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 22rpx 18rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  animation: fadeUp 0.3s ease-out;
}

.calendar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rpx 8rpx 18rpx;
}

.month {
  font-size: 32rpx;
  font-weight: 700;
  color: #1f2533;
}

.week-switch {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.switch-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #717b90;
  font-size: 28rpx;
  background: transparent;
  transition: all 0.25s ease;
}

.switch-btn-active {
  background: #f2f4f9;
  transform: scale(0.96);
}

.week-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8rpx;
}

.day-item {
  border-radius: 16rpx;
  padding: 12rpx 6rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.day-item.active {
  background: linear-gradient(135deg, #ffbe4d 0%, #ff9422 100%);
  box-shadow: 0 8rpx 16rpx rgba(255, 148, 34, 0.28);
}

.weekday {
  font-size: 21rpx;
  color: #95a0b7;
}

.day {
  margin-top: 6rpx;
  font-size: 30rpx;
  color: #273148;
  font-weight: 700;
}

.day-item.today .day {
  color: #ff8d1f;
}

.day-item.active .weekday,
.day-item.active .day {
  color: #ffffff;
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
  background: #ffffff;
}

.list-wrap {
  margin-top: 20rpx;
}

.date-tip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
  padding: 0 6rpx;
  font-size: 24rpx;
  color: #7c859b;
}

.count {
  color: #9ea7ba;
}

.lesson-card {
  margin-bottom: 14rpx;
  border-radius: 24rpx;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid #eef1f6;
  transition: all 0.25s ease;
  animation: slideInRight 0.3s ease-out;
  animation-fill-mode: both;
}

.lesson-card:nth-child(1) { animation-delay: 0.05s; }
.lesson-card:nth-child(2) { animation-delay: 0.1s; }
.lesson-card:nth-child(3) { animation-delay: 0.15s; }
.lesson-card:nth-child(4) { animation-delay: 0.2s; }

.lesson-card:active {
  transform: scale(0.99);
}

.lesson-main {
  flex: 1;
  padding: 18rpx;
  display: flex;
  gap: 14rpx;
}

.time-col {
  min-width: 96rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6rpx;
  background: #FFF7ED;
  border-radius: 14rpx;
  padding: 10rpx 6rpx;
}

.time-main {
  font-size: 29rpx;
  font-weight: 700;
  color: #1f2533;
}

.time-sub {
  font-size: 22rpx;
  color: #9099ab;
}

.lesson-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10rpx;
}

.info-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10rpx;
}

.student {
  font-size: 29rpx;
  color: #1f2533;
  font-weight: 700;
}

.course-tag {
  font-size: 20rpx;
  color: #f08923;
  border-radius: 999rpx;
  padding: 4rpx 12rpx;
  background: #fff1df;
}

.info-bottom {
  display: flex;
  align-items: center;
}

.status-pill {
  font-size: 22rpx;
  border-radius: 999rpx;
  padding: 5rpx 14rpx;
}

.status-pill.pending {
  color: #e08b13;
  background: rgba(255, 244, 227, 0.82);
}

.status-pill.confirmed {
  color: #d87100;
  background: rgba(255, 232, 203, 0.85);
}

.status-pill.completed {
  color: #218f55;
  background: rgba(230, 245, 235, 0.9);
}

.status-pill.cancelled,
.status-pill.no_show {
  color: #c75447;
  background: rgba(255, 235, 232, 0.9);
}

.actions {
  display: flex;
  gap: 12rpx;
  margin-top: 4rpx;
}

.action-btn {
  border: none;
  border-radius: 999rpx;
  padding: 10rpx 20rpx;
  line-height: 1;
  font-size: 22rpx;
  transition: all 0.2s ease;
}

.action-btn::after {
  border: none;
}

.action-btn.ghost {
  background: #fff2e0;
  color: #d7740b;
}

.action-btn.outline {
  background: #fff;
  color: #d7740b;
  border: 2rpx solid #ffd4a6;
}

.action-btn:active {
  transform: scale(0.96);
}

.empty {
  margin-top: 26rpx;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 52rpx 28rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.empty-icon {
  width: 90rpx;
  height: 90rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #fff3df, #ffe1bc);
  color: #ff8d1f;
  font-size: 34rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-title {
  font-size: 28rpx;
  color: #4f5870;
}

.empty-sub {
  font-size: 23rpx;
  color: #929ab0;
}

.state-wrap {
  margin-top: 20rpx;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 46rpx 20rpx;
  text-align: center;
}

.state-text {
  font-size: 24rpx;
  color: #8d96ab;
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
