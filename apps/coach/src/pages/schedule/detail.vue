<template>
  <view class="detail-page">
    <view class="info-card">
      <view class="info-row">
        <text class="label">学员</text>
        <text class="value">{{ booking?.student_name }}</text>
      </view>
      <view class="info-row">
        <text class="label">日期</text>
        <text class="value">{{ formatDate(booking?.booking_date) }}</text>
      </view>
      <view class="info-row">
        <text class="label">时间</text>
        <text class="value">{{ formatTime(booking?.start_time) }} - {{ formatTime(booking?.end_time) }}</text>
      </view>
      <view class="info-row">
        <text class="label">类型</text>
        <text class="value">{{ booking?.course_type === 'private' ? '私教课' : '小班课' }}</text>
      </view>
      <view class="info-row">
        <text class="label">状态</text>
        <text :class="['value', 'status', booking?.status]">{{ getStatusText(booking?.status) }}</text>
      </view>
    </view>

    <view class="action-buttons" v-if="booking?.status === 'confirmed'">
      <wd-button type="primary" block @click="completeBooking">完成课程</wd-button>
      <wd-button block plain @click="goToFeedback">写学习反馈</wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

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

const bookingId = ref(0)
const booking = ref<Booking | null>(null)

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日 周${weekdays[date.getDay()]}`
}

function formatTime(timeStr: string | undefined): string {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}

function getStatusText(status: string | undefined): string {
  if (!status) return ''
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

function completeBooking() {
  uni.showModal({
    title: '确认完成',
    content: '确定要标记此课程为已完成吗？',
    success: (res) => {
      if (res.confirm && booking.value) {
        booking.value.status = 'completed'
        uni.showToast({ title: '操作成功', icon: 'success' })
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

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}
  bookingId.value = parseInt(options.id) || 0

  // 模拟数据
  booking.value = {
    id: bookingId.value,
    student_id: 1,
    student_name: '小明',
    booking_date: new Date().toISOString().split('T')[0],
    start_time: '09:00:00',
    end_time: '10:00:00',
    course_type: 'private',
    status: 'confirmed'
  }
})
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20rpx;
}

.info-card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;

  .info-row {
    display: flex;
    justify-content: space-between;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .label {
      font-size: 28rpx;
      color: #999;
    }

    .value {
      font-size: 28rpx;
      color: #333;

      &.status {
        &.pending,
        &.confirmed {
          color: #2196F3;
        }

        &.completed {
          color: #4caf50;
        }

        &.cancelled {
          color: #f44336;
        }
      }
    }
  }
}

.action-buttons {
  margin-top: 40rpx;

  :deep(.wd-button) {
    margin-bottom: 20rpx;
  }
}
</style>
