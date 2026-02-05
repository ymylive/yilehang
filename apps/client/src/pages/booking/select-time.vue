<template>
  <view class="select-time-page">
    <!-- 鏁欑粌淇℃伅 -->
    <view class="coach-info-bar">
      <image
        :src="coach?.avatar || '/static/default-avatar.png'"
        class="coach-avatar"
      />
      <view class="coach-name">{{ coach?.name }}</view>
    </view>

    <!-- 鏃ユ湡閫夋嫨 -->
    <view class="date-selector">
      <view class="date-header">
        <text class="month-text">{{ currentMonth }}鏈?/text>
      </view>
      <scroll-view scroll-x class="date-scroll">
        <view
          v-for="day in dateList"
          :key="day.date"
          :class="['date-item', { active: selectedDate === day.date, disabled: day.isPast }]"
          @click="selectDate(day)"
        >
          <text class="weekday">{{ day.weekday }}</text>
          <text class="day">{{ day.day }}</text>
        </view>
      </scroll-view>
    </view>

    <!-- 鏃舵閫夋嫨 -->
    <view class="time-slots">
      <view class="slots-title">閫夋嫨鏃舵</view>
      <view class="slots-grid">
        <view
          v-for="slot in availableSlots"
          :key="`${slot.start_time}-${slot.end_time}`"
          :class="['slot-item', { active: isSlotSelected(slot), disabled: !slot.is_available }]"
          @click="selectSlot(slot)"
        >
          <text class="slot-time">{{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}</text>
          <text class="slot-status">{{ slot.is_available ? '鍙害' : '宸茬害' }}</text>
        </view>
      </view>
      <view v-if="availableSlots.length === 0" class="no-slots">
        璇ユ棩鏈熸殏鏃犲彲绾︽椂娈?      </view>
    </view>

    <!-- 搴曢儴鎿嶄綔鏍?-->
    <view class="bottom-bar">
      <view class="selected-info" v-if="selectedSlot">
        <text class="selected-date">{{ formatSelectedDate() }}</text>
        <text class="selected-time">{{ formatTime(selectedSlot.start_time) }} - {{ formatTime(selectedSlot.end_time) }}</text>
      </view>
      <button
        class="btn-next"
        :disabled="!selectedSlot"
        @click="goToConfirm"
      >
        涓嬩竴姝?      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { coachApi } from '@/api/index'

interface Coach {
  id: number
  name: string
  avatar: string | null
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
  isPast: boolean
}

const coachId = ref(0)
const coach = ref<Coach | null>(null)
const selectedDate = ref('')
const selectedSlot = ref<TimeSlot | null>(null)
const allSlots = ref<TimeSlot[]>([])
const loading = ref(false)

const weekdays = ['鏃?, '涓€', '浜?, '涓?, '鍥?, '浜?, '鍏?]

// 鐢熸垚鏈潵7澶╃殑鏃ユ湡鍒楄〃
const dateList = computed<DateItem[]>(() => {
  const list: DateItem[] = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  for (let i = 0; i < 14; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)

    list.push({
      date: formatDateStr(date),
      day: date.getDate(),
      weekday: i === 0 ? '浠婂ぉ' : i === 1 ? '鏄庡ぉ' : `鍛?{weekdays[date.getDay()]}`,
      isPast: false
    })
  }

  return list
})

const currentMonth = computed(() => {
  if (!selectedDate.value) return new Date().getMonth() + 1
  return new Date(selectedDate.value).getMonth() + 1
})

// 褰撳墠閫変腑鏃ユ湡鐨勫彲绾︽椂娈?const availableSlots = computed(() => {
  return allSlots.value.filter(slot => slot.date === selectedDate.value)
})

function formatDateStr(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatTime(timeStr: string): string {
  // 澶勭悊 "HH:MM:SS" 鏍煎紡
  return timeStr.substring(0, 5)
}

function formatSelectedDate(): string {
  if (!selectedDate.value) return ''
  const date = new Date(selectedDate.value)
  return `${date.getMonth() + 1}鏈?{date.getDate()}鏃?鍛?{weekdays[date.getDay()]}`
}

async function loadCoachInfo() {
  try {
    coach.value = await coachApi.get(coachId.value)
  } catch (error) {
    console.error('鍔犺浇鏁欑粌淇℃伅澶辫触', error)
  }
}

async function loadAvailableSlots() {
  loading.value = true
  try {
    const startDate = dateList.value[0]?.date
    const endDate = dateList.value[dateList.value.length - 1]?.date

    const data = await coachApi.getAvailableSlots(coachId.value, startDate, endDate)
    allSlots.value = data.slots || []
  } catch (error: any) {
    uni.showToast({ title: error.message || '鍔犺浇鏃舵澶辫触', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function selectDate(day: DateItem) {
  if (day.isPast) return
  selectedDate.value = day.date
  selectedSlot.value = null
}

function selectSlot(slot: TimeSlot) {
  if (!slot.is_available) return
  selectedSlot.value = slot
}

function isSlotSelected(slot: TimeSlot): boolean {
  if (!selectedSlot.value) return false
  return selectedSlot.value.start_time === slot.start_time &&
         selectedSlot.value.end_time === slot.end_time
}

function goToConfirm() {
  if (!selectedSlot.value) return

  const params = {
    coachId: coachId.value,
    coachName: coach.value?.name || '',
    date: selectedDate.value,
    startTime: selectedSlot.value.start_time,
    endTime: selectedSlot.value.end_time
  }

  uni.navigateTo({
    url: `/pages/booking/confirm?${new URLSearchParams(params as any).toString()}`
  })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}
  coachId.value = parseInt(options.coachId) || 0

  if (coachId.value) {
    // 榛樿閫変腑浠婂ぉ
    selectedDate.value = dateList.value[0]?.date || ''
    loadCoachInfo()
    loadAvailableSlots()
  }
})
</script>

<style lang="scss" scoped>
.select-time-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 160rpx;
}

.coach-info-bar {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  background-color: #fff;

  .coach-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    margin-right: 20rpx;
  }

  .coach-name {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
  }
}

.date-selector {
  background-color: #fff;
  margin-top: 20rpx;
  padding: 24rpx 0;

  .date-header {
    padding: 0 30rpx 20rpx;

    .month-text {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
    }
  }

  .date-scroll {
    white-space: nowrap;
    padding: 0 20rpx;
  }

  .date-item {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100rpx;
    height: 120rpx;
    margin: 0 10rpx;
    border-radius: 12rpx;
    background-color: #f5f5f5;

    .weekday {
      font-size: 24rpx;
      color: #999;
      margin-bottom: 8rpx;
    }

    .day {
      font-size: 36rpx;
      font-weight: 600;
      color: #333;
    }

    &.active {
      background-color: #FF8800;

      .weekday,
      .day {
        color: #fff;
      }
    }

    &.disabled {
      opacity: 0.5;
    }
  }
}

.time-slots {
  background-color: #fff;
  margin-top: 20rpx;
  padding: 30rpx;

  .slots-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 24rpx;
  }

  .slots-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20rpx;
  }

  .slot-item {
    width: calc(33.33% - 14rpx);
    padding: 24rpx 0;
    text-align: center;
    background-color: #f5f5f5;
    border-radius: 12rpx;
    border: 2rpx solid transparent;

    .slot-time {
      display: block;
      font-size: 28rpx;
      color: #333;
      margin-bottom: 8rpx;
    }

    .slot-status {
      font-size: 22rpx;
      color: #FF8800;
    }

    &.active {
      background-color: #e8f5e9;
      border-color: #FF8800;
    }

    &.disabled {
      .slot-time {
        color: #ccc;
      }

      .slot-status {
        color: #ccc;
      }
    }
  }

  .no-slots {
    text-align: center;
    padding: 60rpx 0;
    color: #999;
    font-size: 28rpx;
  }
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background-color: #fff;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);

  .selected-info {
    display: flex;
    justify-content: center;
    margin-bottom: 16rpx;

    .selected-date {
      font-size: 28rpx;
      color: #333;
      margin-right: 20rpx;
    }

    .selected-time {
      font-size: 28rpx;
      color: #FF8800;
      font-weight: 600;
    }
  }
  .btn-next {
    width: 100%;
    height: 88rpx;
    background-color: #FF8800;
    color: #fff;
    font-size: 32rpx;
    border-radius: 44rpx;
    border: none;

    &[disabled] {
      background-color: #ccc;
    }
  }
}
</style>
