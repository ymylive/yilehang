<template>
  <view class="select-time-page">
    <!-- 教练信息 -->
    <view class="coach-info-bar">
      <image
        :src="coach?.avatar || '/static/default-avatar.png'"
        class="coach-avatar"
      />
      <view class="coach-name">{{ coach?.name }}</view>
    </view>

    <!-- 日期选择 -->
    <view class="date-selector">
      <view class="date-header">
        <text class="month-text">{{ currentMonth }}月</text>
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

    <!-- 时段选择 -->
    <view class="time-slots">
      <view class="slots-title">选择时段</view>
      <view class="slots-grid">
        <view
          v-for="slot in availableSlots"
          :key="`${slot.start_time}-${slot.end_time}`"
          :class="['slot-item', { active: isSlotSelected(slot), disabled: !slot.is_available }]"
          @click="selectSlot(slot)"
        >
          <text class="slot-time">{{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}</text>
          <text class="slot-status">{{ slot.is_available ? '可约' : '已约' }}</text>
        </view>
      </view>
      <view v-if="availableSlots.length === 0" class="no-slots">
        该日期暂无可约时段
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="selected-info" v-if="selectedSlot">
        <text class="selected-date">{{ formatSelectedDate() }}</text>
        <text class="selected-time">{{ formatTime(selectedSlot.start_time) }} - {{ formatTime(selectedSlot.end_time) }}</text>
      </view>
      <wd-button
        type="primary"
        block
        :disabled="!selectedSlot"
        @click="goToConfirm"
      >
        下一步
      </wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { coachApi } from '@/api'

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

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 生成未来7天的日期列表
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
      weekday: i === 0 ? '今天' : i === 1 ? '明天' : `周${weekdays[date.getDay()]}`,
      isPast: false
    })
  }

  return list
})

const currentMonth = computed(() => {
  if (!selectedDate.value) return new Date().getMonth() + 1
  return new Date(selectedDate.value).getMonth() + 1
})

// 当前选中日期的可约时段
const availableSlots = computed(() => {
  return allSlots.value.filter(slot => slot.date === selectedDate.value)
})

function formatDateStr(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatTime(timeStr: string): string {
  // 处理 "HH:MM:SS" 格式
  return timeStr.substring(0, 5)
}

function formatSelectedDate(): string {
  if (!selectedDate.value) return ''
  const date = new Date(selectedDate.value)
  return `${date.getMonth() + 1}月${date.getDate()}日 周${weekdays[date.getDay()]}`
}

async function loadCoachInfo() {
  try {
    coach.value = await coachApi.get(coachId.value)
  } catch (error) {
    console.error('加载教练信息失败', error)
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
    uni.showToast({ title: error.message || '加载时段失败', icon: 'none' })
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
    // 默认选中今天
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
      background-color: #4caf50;

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
      color: #4caf50;
    }

    &.active {
      background-color: #e8f5e9;
      border-color: #4caf50;
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
      color: #4caf50;
      font-weight: 600;
    }
  }
}
</style>
