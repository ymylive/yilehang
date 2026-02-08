<template>
  <view class="select-time-page">
    <view v-if="initialLoading" class="skeleton-group">
      <view class="skeleton-hero shimmer"></view>
      <view class="skeleton-card shimmer"></view>
    </view>

    <view v-else>
      <view class="hero-card" v-if="coach">
        <image :src="coach.avatar || '/static/default-avatar.png'" class="hero-avatar" mode="aspectFill" />
        <view class="hero-main">
          <text class="hero-name">{{ coach.name }}</text>
          <text class="hero-meta" v-if="coach.years_of_experience">{{ t.yearsLabel }} {{ coach.years_of_experience }} {{ t.yearUnit }}</text>
          <text class="hero-meta" v-else>{{ t.pickSlotPrefix }}{{ isReschedule ? t.reschedule : t.booking }}</text>
        </view>
        <view class="hero-rating" v-if="coach.avg_rating">{{ coach.avg_rating.toFixed(1) }}</view>
      </view>

      <view class="hero-card hero-empty" v-else>
        <text class="hero-name">{{ t.coachLoadFailed }}</text>
        <text class="hero-meta">{{ t.backRetry }}</text>
      </view>

      <view class="card">
        <view class="card-head">
          <text class="card-title">{{ t.selectDateTitle }}</text>
          <text class="card-sub">{{ monthLabel }}</text>
        </view>
        <scroll-view scroll-x class="date-scroll" :show-scrollbar="false">
          <view
            v-for="item in dateList"
            :key="item.date"
            :class="['date-chip', { active: selectedDate === item.date }]"
            hover-class="chip-hover"
            :hover-start-time="0"
            :hover-stay-time="60"
            @click="selectDate(item.date)"
          >
            <text class="chip-week">{{ item.weekday }}</text>
            <text class="chip-day">{{ item.day }}</text>
            <text class="chip-label">{{ item.label }}</text>
          </view>
        </scroll-view>
      </view>

      <view class="card">
        <view class="card-head">
          <text class="card-title">{{ t.slotTitle }}</text>
          <text class="card-sub" v-if="availableSlots.length">{{ t.totalPrefix }} {{ availableSlots.length }} {{ t.slotUnit }}</text>
        </view>

        <view class="slot-grid" v-if="availableSlots.length">
          <view
            v-for="slot in availableSlots"
            :key="`${slot.date}-${slot.start_time}-${slot.end_time}`"
            :class="['slot-item', { active: isSlotSelected(slot), disabled: !slot.is_available }]"
            :hover-class="slot.is_available ? 'slot-hover' : ''"
            :hover-start-time="0"
            :hover-stay-time="60"
            @click="selectSlot(slot)"
          >
            <text class="slot-time">{{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}</text>
            <text class="slot-tip" v-if="slot.is_available">
              {{ slot.remaining_slots > 0 && slot.remaining_slots < 3 ? onlyLeftText(slot.remaining_slots) : t.available }}
            </text>
            <text class="slot-tip" v-else>{{ t.full }}</text>
          </view>
        </view>

        <view class="empty" v-else-if="!loading">
          <text class="empty-title">{{ t.noSlotTitle }}</text>
          <text class="empty-sub">{{ t.noSlotSub }}</text>
        </view>

        <view class="loading" v-else>{{ t.loading }}</view>
      </view>

      <view class="bottom-bar">
        <view class="selected" v-if="selectedSlot">
          <text>{{ selectedDateLabel }}</text>
          <text>{{ formatTime(selectedSlot.start_time) }} - {{ formatTime(selectedSlot.end_time) }}</text>
        </view>
        <view class="selected muted" v-else>{{ t.selectHint }}</view>

        <button
          class="next-btn"
          :disabled="!selectedSlot"
          hover-class="btn-hover"
          :hover-stay-time="60"
          @click="goToConfirm"
        >
          {{ isReschedule ? t.nextReschedule : t.nextBooking }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { coachApi } from '@/api/index'

interface Coach {
  id: number
  name: string
  avatar: string | null
  years_of_experience?: number | null
  avg_rating?: number
}

interface TimeSlot {
  date: string
  start_time: string
  end_time: string
  is_available: boolean
  remaining_slots: number
}

interface DateItem {
  date: string
  day: number
  weekday: string
  label: string
}

const t = {
  yearsLabel: '\u6559\u9f84',
  yearUnit: '\u5e74',
  monthUnit: '\u6708',
  dayUnit: '\u65e5',
  pickSlotPrefix: '\u8bf7\u9009\u62e9\u5408\u9002\u65f6\u6bb5\u8fdb\u884c',
  booking: '\u9884\u7ea6',
  reschedule: '\u6539\u671f',
  coachLoadFailed: '\u6559\u7ec3\u4fe1\u606f\u52a0\u8f7d\u5931\u8d25',
  backRetry: '\u8bf7\u8fd4\u56de\u91cd\u8bd5',
  selectDateTitle: '\u9009\u62e9\u65e5\u671f',
  slotTitle: '\u53ef\u9009\u65f6\u6bb5',
  totalPrefix: '\u5171',
  slotUnit: '\u4e2a',
  available: '\u53ef\u9884\u7ea6',
  full: '\u5df2\u7ea6\u6ee1',
  onlyLeftPrefix: '\u4ec5\u5269',
  seatUnit: '\u5e2d',
  noSlotTitle: '\u5f53\u5929\u6682\u65e0\u53ef\u7ea6\u65f6\u6bb5',
  noSlotSub: '\u6362\u4e00\u4e2a\u65e5\u671f\u8bd5\u8bd5',
  loading: '\u52a0\u8f7d\u4e2d...',
  selectHint: '\u8bf7\u9009\u62e9\u4e00\u4e2a\u53ef\u7528\u65f6\u6bb5',
  nextReschedule: '\u4e0b\u4e00\u6b65\uff1a\u786e\u8ba4\u6539\u671f',
  nextBooking: '\u4e0b\u4e00\u6b65\uff1a\u786e\u8ba4\u9884\u7ea6',
  today: '\u4eca\u5929',
  tomorrow: '\u660e\u5929',
  coachNotFound: '\u6559\u7ec3\u4fe1\u606f\u4e0d\u5b58\u5728',
  loadCoachFail: '\u52a0\u8f7d\u6559\u7ec3\u4fe1\u606f\u5931\u8d25',
  loadSlotFail: '\u52a0\u8f7d\u65f6\u6bb5\u5931\u8d25'
} as const

const coachId = ref(0)
const rescheduleId = ref(0)
const coach = ref<Coach | null>(null)
const selectedDate = ref('')
const selectedSlot = ref<TimeSlot | null>(null)
const allSlots = ref<TimeSlot[]>([])
const loading = ref(false)
const initialLoading = ref(true)

const weekdayNames = ['\u5468\u65e5', '\u5468\u4e00', '\u5468\u4e8c', '\u5468\u4e09', '\u5468\u56db', '\u5468\u4e94', '\u5468\u516d']

const isReschedule = computed(() => rescheduleId.value > 0)

const dateList = computed<DateItem[]>(() => {
  const base = new Date()
  base.setHours(0, 0, 0, 0)

  return Array.from({ length: 14 }).map((_, index) => {
    const date = new Date(base)
    date.setDate(base.getDate() + index)
    return {
      date: formatDate(date),
      day: date.getDate(),
      weekday: index === 0 ? t.today : index === 1 ? t.tomorrow : weekdayNames[date.getDay()],
      label: `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`
    }
  })
})

const monthLabel = computed(() => {
  if (!selectedDate.value) {
    const now = new Date()
    return `${now.getFullYear()}${t.yearUnit}${now.getMonth() + 1}${t.monthUnit}`
  }
  const date = new Date(selectedDate.value)
  return `${date.getFullYear()}${t.yearUnit}${date.getMonth() + 1}${t.monthUnit}`
})

const availableSlots = computed(() => {
  return allSlots.value
    .filter((slot) => slot.date === selectedDate.value)
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
})

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  const date = new Date(selectedDate.value)
  return `${date.getMonth() + 1}${t.monthUnit}${date.getDate()}${t.dayUnit} ${weekdayNames[date.getDay()]}`
})

function getOptions() {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1]
  return (current as any).$page?.options || {}
}

function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function toDateOnly(value?: string): string {
  if (!value) return ''
  return value.slice(0, 10)
}

function formatTime(value?: string): string {
  if (!value) return '--:--'
  if (value.includes('T')) {
    const date = new Date(value)
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  }
  return value.slice(0, 5)
}

function normalizeSlot(raw: any): TimeSlot {
  const start = String(raw.start_time || raw.start_at || '')
  const end = String(raw.end_time || raw.end_at || '')
  const date = toDateOnly(raw.date || start)

  const remaining = Number(raw.remaining_slots ?? raw.remaining ?? 0)
  const availableByStatus = raw.is_available !== false && raw.status !== 'booked' && raw.status !== 'full'

  return {
    date,
    start_time: start,
    end_time: end,
    is_available: availableByStatus && (remaining > 0 || raw.remaining_slots == null),
    remaining_slots: remaining
  }
}

function onlyLeftText(count: number) {
  return `${t.onlyLeftPrefix}${count}${t.seatUnit}`
}

async function loadCoachDetail() {
  try {
    coach.value = await coachApi.get(coachId.value)
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadCoachFail, icon: 'none' })
  }
}

async function loadAvailableSlots() {
  loading.value = true
  try {
    const startDate = dateList.value[0]?.date
    const endDate = dateList.value[dateList.value.length - 1]?.date
    const response = await coachApi.getAvailableSlots(coachId.value, startDate, endDate)

    const source = Array.isArray(response) ? response : response?.slots || response?.items || []
    allSlots.value = source.map(normalizeSlot).filter((slot) => slot.date && slot.start_time && slot.end_time)
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadSlotFail, icon: 'none' })
  } finally {
    loading.value = false
  }
}

function selectDate(date: string) {
  selectedDate.value = date
  selectedSlot.value = null
}

function selectSlot(slot: TimeSlot) {
  if (!slot.is_available) return
  selectedSlot.value = slot
}

function isSlotSelected(slot: TimeSlot) {
  if (!selectedSlot.value) return false
  return selectedSlot.value.start_time === slot.start_time && selectedSlot.value.end_time === slot.end_time
}

function goToConfirm() {
  if (!selectedSlot.value) return

  const query = [
    `coachId=${coachId.value}`,
    `coachName=${encodeURIComponent(coach.value?.name || '')}`,
    `date=${selectedDate.value}`,
    `startTime=${encodeURIComponent(selectedSlot.value.start_time)}`,
    `endTime=${encodeURIComponent(selectedSlot.value.end_time)}`
  ]

  if (rescheduleId.value) {
    query.push(`rescheduleId=${rescheduleId.value}`)
  }

  uni.navigateTo({
    url: `/pages/booking/confirm?${query.join('&')}`
  })
}

onMounted(async () => {
  const options = getOptions()
  coachId.value = Number(options.coachId || options.id || 0)
  rescheduleId.value = Number(options.rescheduleId || 0)
  selectedDate.value = dateList.value[0]?.date || ''

  if (!coachId.value) {
    uni.showToast({ title: t.coachNotFound, icon: 'none' })
    initialLoading.value = false
    return
  }

  try {
    await Promise.all([loadCoachDetail(), loadAvailableSlots()])
  } finally {
    initialLoading.value = false
  }
})
</script>

<style lang="scss" scoped>
:root {
  --c-primary-start: #ffc04d;
  --c-primary-end: #ff9024;
  --c-primary-bg-light: #fff8ed;
  --c-text-main: #1d2129;
  --c-text-sub: #86909c;
  --c-bg-page: #f7f8fa;
}

.select-time-page {
  min-height: 100vh;
  background: var(--c-bg-page);
  padding: 24rpx;
  padding-bottom: 220rpx;
}

.hero-card,
.card {
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.04);
}

.hero-card {
  display: flex;
  align-items: center;
  padding: 20rpx;
  margin-bottom: 14rpx;
  animation: fadeInUp 0.35s ease-out;
}

.hero-empty {
  flex-direction: column;
  align-items: flex-start;
}

.hero-avatar {
  width: 98rpx;
  height: 98rpx;
  border-radius: 24rpx;
  background: #f3f5fb;
  flex-shrink: 0;
  margin-right: 14rpx;
}

.hero-main {
  flex: 1;
  min-width: 0;
}

.hero-name {
  display: block;
  font-size: 31rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.hero-meta {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: var(--c-text-sub);
}

.hero-rating {
  min-width: 72rpx;
  height: 48rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #ffe7c2, #ffd08a);
  color: #d2780f;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  padding: 20rpx;
  margin-bottom: 14rpx;
  animation: fadeInUp 0.4s ease-out;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.card-sub {
  font-size: 22rpx;
  color: #9aa2b5;
}

.date-scroll {
  white-space: nowrap;
}

.date-chip {
  width: 116rpx;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 18rpx;
  background: #fff;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.02);
  border: 2rpx solid transparent;
  padding: 12rpx 0;
  margin-right: 10rpx;
  transition: all 0.2s ease;
}

.date-chip.active {
  background: linear-gradient(135deg, var(--c-primary-start), var(--c-primary-end));
  box-shadow: 0 8rpx 20rpx rgba(255, 144, 36, 0.25);
  transform: translateY(-2rpx);
}

.chip-hover {
  transform: scale(0.96);
  opacity: 0.92;
}

.chip-week {
  font-size: 21rpx;
  color: #8f98ac;
}

.chip-day {
  margin-top: 6rpx;
  font-size: 33rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.chip-label {
  margin-top: 4rpx;
  font-size: 20rpx;
  color: #a1a9bb;
}

.date-chip.active .chip-week,
.date-chip.active .chip-day,
.date-chip.active .chip-label {
  color: #fff;
}

.slot-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10rpx;
}

.slot-item {
  border-radius: 16rpx;
  background: #fff;
  border: 1rpx solid #f2f4f7;
  padding: 16rpx 12rpx;
  text-align: center;
  transition: all 0.2s ease;
}

.slot-item.active {
  background: var(--c-primary-bg-light);
  border-color: var(--c-primary-end);
}

.slot-item.disabled {
  background: #fafafa;
  border-color: transparent;
  opacity: 0.6;
}

.slot-hover {
  background: #fffbf5;
  border-color: #ffe0b2;
}

.slot-time {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: #2b3448;
}

.slot-item.disabled .slot-time {
  color: #c9cdd4;
}

.slot-tip {
  display: block;
  margin-top: 8rpx;
  font-size: 21rpx;
  color: #9aa2b5;
}

.slot-item.active .slot-tip {
  color: #dc7d15;
}

.empty,
.loading {
  border-radius: 18rpx;
  background: #f8f9fd;
  text-align: center;
  padding: 40rpx 20rpx;
}

.empty-title {
  display: block;
  font-size: 26rpx;
  color: #4e5870;
}

.empty-sub {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #a0a8ba;
}

.loading {
  font-size: 24rpx;
  color: #9aa2b5;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 18rpx 20rpx calc(18rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(18rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 -8rpx 24rpx rgba(30, 36, 50, 0.08);
}

.selected {
  font-size: 23rpx;
  color: #4f5870;
  display: flex;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.selected.muted {
  color: #9ba3b6;
}

.next-btn {
  width: 100%;
  height: 84rpx;
  border: none;
  border-radius: 20rpx;
  background: linear-gradient(135deg, var(--c-primary-start), var(--c-primary-end));
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 12rpx 32rpx rgba(255, 144, 36, 0.16);
}

.next-btn::after {
  border: none;
}

.next-btn[disabled] {
  background: #d6dbe6;
  box-shadow: none;
  color: #fff;
}

.btn-hover {
  transform: scale(0.98);
  opacity: 0.95;
}

.skeleton-group {
  animation: fadeInUp 0.2s ease-out;
}

.skeleton-hero,
.skeleton-card {
  border-radius: 24rpx;
  margin-bottom: 14rpx;
}

.skeleton-hero {
  height: 140rpx;
}

.skeleton-card {
  height: 380rpx;
}

.shimmer {
  background: linear-gradient(90deg, #f0f2f5 25%, #e6e8eb 37%, #f0f2f5 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}

@keyframes shimmer {
  0% {
    background-position: -100% 0;
  }
  100% {
    background-position: 100% 0;
  }
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
