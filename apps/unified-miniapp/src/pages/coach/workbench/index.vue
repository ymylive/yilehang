<template>
  <PageErrorBoundary page="coach.workbench" @retry="retryLoad">
  <view class="workbench-page page-enter">
    <view class="hero anim-fade-up">
      <view class="hero-glow" aria-hidden="true"></view>

      <view class="hero-content">
        <view class="profile">
          <image :src="coachInfo?.avatar || '/static/default-avatar.png'" class="avatar" mode="aspectFill" />
          <view class="profile-text">
            <text class="greeting">{{ getGreeting() }}{{ t.comma }}{{ coachInfo?.name || t.coachDefault }}</text>
            <text class="date">{{ formatDate(new Date()) }}</text>
          </view>
        </view>

        <view class="stats-card">
          <view class="stat-item">
            <text class="stat-value">{{ todayStats.totalLessons }}</text>
            <text class="stat-label">{{ t.todayLessons }}</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ todayStats.completedLessons }}</text>
            <text class="stat-label">{{ t.completedLessons }}</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ todayStats.totalStudents }}</text>
            <text class="stat-label">{{ t.myStudents }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="quick-card anim-fade-up anim-delay-1">
      <view class="quick-item tap-active" @click="goToSlots">
        <view class="quick-icon">{{ t.slotIcon }}</view>
        <text class="quick-label">{{ t.slotManagement }}</text>
      </view>
      <view class="quick-item tap-active" @click="goToStudents">
        <view class="quick-icon">{{ t.studentIcon }}</view>
        <text class="quick-label">{{ t.studentManagement }}</text>
      </view>
      <view class="quick-item tap-active" @click="goToIncome">
        <view class="quick-icon">{{ t.incomeIcon }}</view>
        <text class="quick-label">{{ t.incomeStats }}</text>
      </view>
      <view class="quick-item tap-active" @click="goToReviews">
        <view class="quick-icon">{{ t.reviewIcon }}</view>
        <text class="quick-label">{{ t.reviewCenter }}</text>
      </view>
    </view>

    <view class="section anim-fade-up anim-delay-2">
      <view class="section-head">
        <text class="section-title">{{ t.todaySchedule }}</text>
        <view class="section-link tap-active" @click="goToSchedule">
          <text>{{ t.viewAll }}</text>
          <text class="arrow">&gt;</text>
        </view>
      </view>

      <view v-if="loading" class="skeleton-wrap">
        <view class="skeleton-row"></view>
        <view class="skeleton-row short"></view>
      </view>

      <view v-else-if="todayLessons.length > 0" class="lesson-list">
        <view
          v-for="lesson in todayLessons"
          :key="lesson.id"
          class="lesson-item tap-active"
          @click="goToLessonDetail(lesson.id)"
        >
          <view class="lesson-time">
            <text class="start">{{ formatClock(lesson.start_time) }}</text>
            <text class="end">{{ formatClock(lesson.end_time) }}</text>
          </view>
          <view class="lesson-info">
            <view class="lesson-top">
              <text class="student-name">{{ lesson.student_name }}</text>
              <view :class="['status-chip', lesson.status]">
                <text class="status-dot"></text>
                <text>{{ getStatusText(lesson.status) }}</text>
              </view>
            </view>
            <text class="lesson-meta">{{ getCourseTypeText(lesson.course_type) }}</text>
          </view>
        </view>
      </view>

      <view v-else class="empty-state">
        <text class="empty-title">{{ t.noScheduleTitle }}</text>
        <text class="empty-sub">{{ t.noScheduleSub }}</text>
      </view>
    </view>
  <DynamicTabBar />
</view>
  </PageErrorBoundary>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import PageErrorBoundary from '@/components/PageErrorBoundary.vue'
import { ref, onMounted } from 'vue'
import { coachProfileApi, coachScheduleApi } from '@/api/index'
import { safeNavigate } from '@/utils/safe-nav'

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
  course_type: string
}

const t = {
  comma: '\uff0c',
  coachDefault: '\u6559\u7ec3',
  studentDefault: '\u5b66\u5458',
  todayLessons: '\u4eca\u65e5\u8bfe\u7a0b',
  completedLessons: '\u5df2\u5b8c\u6210',
  myStudents: '\u6211\u7684\u5b66\u5458',
  slotIcon: '\u6392',
  slotManagement: '\u6392\u8bfe\u7ba1\u7406',
  studentIcon: '\u5458',
  studentManagement: '\u5b66\u5458\u7ba1\u7406',
  incomeIcon: '\u6536',
  incomeStats: '\u6536\u5165\u7edf\u8ba1',
  reviewIcon: '\u8bc4',
  reviewCenter: '\u8bc4\u4ef7\u4e2d\u5fc3',
  todaySchedule: '\u4eca\u65e5\u65e5\u7a0b',
  viewAll: '\u67e5\u770b\u5168\u90e8',
  privateCourse: '1\u5bf91\u79c1\u6559\u8bfe',
  groupCourse: '\u56e2\u8bfe',
  noScheduleTitle: '\u4eca\u5929\u6682\u65e0\u8bfe\u7a0b\u5b89\u6392',
  noScheduleSub: '\u53ef\u4ee5\u53bb\u8bbe\u7f6e\u53ef\u9884\u7ea6\u65f6\u6bb5',
  greetingNight: '\u591c\u6df1\u4e86',
  greetingMorning: '\u65e9\u4e0a\u597d',
  greetingNoon: '\u4e2d\u5348\u597d',
  greetingAfternoon: '\u4e0b\u5348\u597d',
  greetingEvening: '\u665a\u4e0a\u597d',
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
  loadScheduleFailed: '\u52a0\u8f7d\u4eca\u65e5\u8bfe\u8868\u5931\u8d25'
} as const

const weekdays = [t.weekdaySun, t.weekdayMon, t.weekdayTue, t.weekdayWed, t.weekdayThu, t.weekdayFri, t.weekdaySat]

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
  if (hour < 6) return t.greetingNight
  if (hour < 12) return t.greetingMorning
  if (hour < 14) return t.greetingNoon
  if (hour < 18) return t.greetingAfternoon
  return t.greetingEvening
}

function formatDate(date: Date): string {
  return `${date.getMonth() + 1}${t.monthUnit}${date.getDate()}${t.dayUnit} ${weekdays[date.getDay()]}`
}

function formatDateKey(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function formatClock(time: string): string {
  if (!time) return '--:--'
  return time.slice(0, 5)
}

function normalizeTime(value: any): string {
  if (!value) return ''
  const text = String(value)
  if (text.includes('T')) {
    const d = new Date(text)
    if (Number.isNaN(d.getTime())) return text
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:00`
  }
  return text
}

function normalizeLesson(raw: any): Lesson {
  return {
    id: Number(raw?.id || 0),
    student_name: String(raw?.student_name || raw?.student?.name || t.studentDefault),
    start_time: normalizeTime(raw?.start_time || raw?.start_at),
    end_time: normalizeTime(raw?.end_time || raw?.end_at),
    status: String(raw?.status || 'pending'),
    booking_date: String(raw?.booking_date || raw?.date || '').slice(0, 10),
    course_type: String(raw?.course_type || 'private')
  }
}

function normalizeLessons(data: any): Lesson[] {
  const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
  return list.map(normalizeLesson).filter(item => item.id > 0)
}

function getCourseTypeText(courseType: string): string {
  if (courseType === 'group') {
    return t.groupCourse
  }
  return t.privateCourse
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

async function loadCoachInfo() {
  try {
    const data: any = await coachProfileApi.getProfile()
    coachInfo.value = {
      id: Number(data?.id || 0),
      name: String(data?.name || t.coachDefault),
      avatar: data?.avatar || null,
      total_students: Number(data?.total_students || 0),
      total_lessons: Number(data?.total_lessons || 0),
      avg_rating: Number(data?.avg_rating || 0)
    }
    todayStats.value.totalStudents = coachInfo.value.total_students
  } catch (error) {
    console.error('load coach profile failed:', error)
  }
}

async function loadTodaySchedule() {
  loading.value = true
  try {
    const today = formatDateKey(new Date())
    const data = await coachScheduleApi.getSchedule({
      start_date: today,
      end_date: today,
      page: 1,
      page_size: 200
    })

    const list = normalizeLessons(data)
    list.sort((a, b) => a.start_time.localeCompare(b.start_time))

    todayLessons.value = list
    todayStats.value.totalLessons = list.length
    todayStats.value.completedLessons = list.filter(item => item.status === 'completed').length
  } catch (error) {
    console.error('load schedule failed:', error)
    todayLessons.value = []
    todayStats.value.totalLessons = 0
    todayStats.value.completedLessons = 0
    uni.showToast({ title: t.loadScheduleFailed, icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goToSchedule() {
  safeNavigate('/pages/coach/schedule/index', 'reLaunch')
}

function goToLessonDetail(id: number) {
  safeNavigate(`/pages/coach/schedule/detail?id=${id}`)
}

function goToSlots() {
  safeNavigate('/pages/coach/slots/manage')
}

function goToStudents() {
  safeNavigate('/pages/coach/students/index')
}

function goToIncome() {
  safeNavigate('/pages/coach/income/index')
}

function goToReviews() {
  safeNavigate('/pages/coach/reviews/index')
}

async function retryLoad() {
  await Promise.all([loadCoachInfo(), loadTodaySchedule()])
}

onMounted(async () => {
  await Promise.all([loadCoachInfo(), loadTodaySchedule()])
})
</script>

<style lang="scss" scoped>
.workbench-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding-bottom: calc(120rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #ffbc47 0%, #ff8d1f 72%);
  border-radius: 0 0 44rpx 44rpx;
  padding: 38rpx 30rpx 110rpx;
}

.hero-glow {
  position: absolute;
  top: -160rpx;
  right: -120rpx;
  width: 420rpx;
  height: 420rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 244, 214, 0.88) 0%, rgba(255, 187, 80, 0.35) 48%, rgba(255, 146, 23, 0.02) 78%);
  animation: pulse 5s ease-in-out infinite;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.profile {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.4);
  background: #fff;
}

.profile-text {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.greeting {
  font-size: 35rpx;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 4rpx 14rpx rgba(0, 0, 0, 0.15);
}

.date {
  display: inline-flex;
  width: fit-content;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.94);
  font-size: 22rpx;
}

.stats-card {
  margin-top: 26rpx;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 24rpx;
  box-shadow: 0 16rpx 28rpx rgba(120, 72, 0, 0.16);
  display: flex;
  align-items: center;
  padding: 22rpx 0;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 42rpx;
  line-height: 1.1;
  font-weight: 800;
  color: #1f2533;
}

.stat-label {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #8790a4;
}

.stat-divider {
  width: 2rpx;
  height: 44rpx;
  background: #edf0f4;
}

.quick-card {
  margin: -40rpx 24rpx 24rpx;
  padding: 18rpx 12rpx;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 12rpx 26rpx rgba(31, 37, 51, 0.07);
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8rpx;
  position: relative;
  z-index: 3;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  padding: 14rpx 6rpx;
  border-radius: 18rpx;
  transition: all 0.25s ease;
}

.quick-item:active {
  background: #fff5e8;
  transform: scale(0.98);
}

.quick-icon {
  width: 74rpx;
  height: 74rpx;
  border-radius: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
  color: #ff8f1f;
  background: linear-gradient(145deg, #fff7e8, #ffe7cb);
  border: 1rpx solid rgba(255, 163, 62, 0.18);
  box-shadow: 0 8rpx 16rpx rgba(255, 143, 31, 0.12);
}

.quick-label {
  font-size: 24rpx;
  color: #44506a;
}

.section {
  margin: 0 24rpx;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 12rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 26rpx;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1f2533;
}

.section-link {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 24rpx;
  color: #8b93a7;
}

.arrow {
  font-size: 22rpx;
}

.skeleton-wrap {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.skeleton-row {
  height: 104rpx;
  border-radius: 18rpx;
  background: linear-gradient(90deg, #f4f6f9, #eef1f5, #f4f6f9);
  animation: shimmer 1.6s linear infinite;
}

.skeleton-row.short {
  width: 72%;
}

.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.lesson-item {
  display: flex;
  gap: 16rpx;
  border-radius: 20rpx;
  background: #fff9f0;
  border: 1rpx solid #ffe5c2;
  padding: 18rpx;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.lesson-item:active {
  transform: translateY(2rpx);
}

.lesson-time {
  min-width: 102rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  justify-content: center;
}

.start {
  font-size: 30rpx;
  font-weight: 700;
  color: #2a3245;
}

.end {
  font-size: 22rpx;
  color: #9aa2b5;
}

.lesson-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8rpx;
}

.lesson-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10rpx;
}

.student-name {
  font-size: 29rpx;
  color: #1f2533;
  font-weight: 600;
}

.lesson-meta {
  font-size: 22rpx;
  color: #7f8798;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  font-size: 21rpx;
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  font-weight: 600;
}

.status-dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background: currentColor;
}

.status-chip.pending {
  background: #fff1dc;
  color: #e68a00;
}

.status-chip.confirmed {
  background: #ffe8c6;
  color: #d77200;
}

.status-chip.completed {
  background: #e9f7ef;
  color: #1d9b55;
}

.status-chip.cancelled,
.status-chip.no_show {
  background: #ffebe9;
  color: #d95142;
}

.empty-state {
  text-align: center;
  padding: 52rpx 0 36rpx;
}

.empty-title {
  display: block;
  font-size: 28rpx;
  color: #5a6478;
}

.empty-sub {
  display: block;
  margin-top: 10rpx;
  font-size: 23rpx;
  color: #99a1b2;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.88;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

@keyframes shimmer {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 240rpx 0;
  }
}
</style>
