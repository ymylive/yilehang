<template>
  <view class="detail-page">
    <!-- 课程信息卡片 -->
    <view class="course-card">
      <view class="course-header">
        <view class="course-name">{{ booking?.course_name || '私教课' }}</view>
        <view :class="['course-status', booking?.status]">
          {{ getStatusText(booking?.status) }}
        </view>
      </view>

      <view class="info-list">
        <view class="info-item">
          <text class="info-label">教练</text>
          <text class="info-value">{{ booking?.coach_name }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">日期</text>
          <text class="info-value">{{ formatDate(booking?.booking_date) }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">时间</text>
          <text class="info-value">{{ formatTime(booking?.start_time) }} - {{ formatTime(booking?.end_time) }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">类型</text>
          <text class="info-value">{{ booking?.course_type === 'private' ? '私教课' : '小班课' }}</text>
        </view>
        <view class="info-item" v-if="booking?.remark">
          <text class="info-label">备注</text>
          <text class="info-value">{{ booking.remark }}</text>
        </view>
      </view>
    </view>

    <!-- 教练反馈 -->
    <view class="feedback-card" v-if="feedback">
      <view class="card-title">教练反馈</view>
      <view class="feedback-content">
        <view class="rating-row" v-if="feedback.performance_rating">
          <text class="rating-label">表现评分</text>
          <view class="rating-stars">
            <text v-for="i in 5" :key="i" :class="['star', { active: i <= feedback.performance_rating }]">★</text>
          </view>
        </view>
        <view class="feedback-text">{{ feedback.content }}</view>
        <view class="suggestions" v-if="feedback.suggestions">
          <text class="suggestions-label">改进建议：</text>
          <text class="suggestions-text">{{ feedback.suggestions }}</text>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <!-- 待上课状态 -->
      <template v-if="booking?.status === 'confirmed' || booking?.status === 'pending'">
        <wd-button type="warning" block @click="handleReschedule" v-if="canReschedule">
          改期
        </wd-button>
        <wd-button type="error" block plain @click="handleCancel" v-if="canCancel">
          取消预约
        </wd-button>
      </template>

      <!-- 已完成状态 -->
      <template v-if="booking?.status === 'completed'">
        <wd-button type="primary" block @click="goToReview" v-if="!hasReviewed">
          评价课程
        </wd-button>
        <view v-else class="reviewed-tip">您已评价此课程</view>
      </template>
    </view>

    <!-- 取消确认弹窗 -->
    <wd-popup v-model="showCancelPopup" position="bottom" round>
      <view class="cancel-popup">
        <view class="popup-title">取消预约</view>
        <view class="popup-tip">取消后课时将自动退还</view>
        <textarea
          v-model="cancelReason"
          placeholder="请输入取消原因（选填）"
          class="cancel-input"
        />
        <view class="popup-buttons">
          <wd-button plain @click="showCancelPopup = false">再想想</wd-button>
          <wd-button type="error" @click="confirmCancel" :loading="cancelling">确认取消</wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { bookingApi, reviewApi } from '@/api'

interface Booking {
  id: number
  student_id: number
  coach_id: number
  schedule_id: number | null
  booking_date: string
  start_time: string
  end_time: string
  course_type: string
  status: string
  cancel_reason: string | null
  cancelled_at: string | null
  remark: string | null
  created_at: string
  student_name: string | null
  coach_name: string | null
  course_name: string | null
}

interface Feedback {
  id: number
  booking_id: number
  performance_rating: number | null
  content: string
  suggestions: string | null
}

const bookingId = ref(0)
const booking = ref<Booking | null>(null)
const feedback = ref<Feedback | null>(null)
const hasReviewed = ref(false)
const loading = ref(false)

const showCancelPopup = ref(false)
const cancelReason = ref('')
const cancelling = ref(false)

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 是否可以取消（开课前2小时）
const canCancel = computed(() => {
  if (!booking.value) return false
  const bookingDateTime = new Date(`${booking.value.booking_date}T${booking.value.start_time}`)
  const now = new Date()
  const diff = bookingDateTime.getTime() - now.getTime()
  return diff > 2 * 60 * 60 * 1000
})

// 是否可以改期
const canReschedule = computed(() => {
  return canCancel.value
})

function getStatusText(status: string | undefined): string {
  if (!status) return ''
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    cancelled: '已取消',
    completed: '已完成',
    no_show: '未到'
  }
  return map[status] || status
}

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日 周${weekdays[date.getDay()]}`
}

function formatTime(timeStr: string | undefined): string {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}

async function loadBookingDetail() {
  loading.value = true
  try {
    booking.value = await bookingApi.get(bookingId.value)
  } catch (error: any) {
    uni.showToast({ title: error.message || '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  showCancelPopup.value = true
}

async function confirmCancel() {
  if (cancelling.value) return
  cancelling.value = true

  try {
    await bookingApi.cancel(bookingId.value, cancelReason.value || undefined)
    uni.showToast({ title: '取消成功', icon: 'success' })
    showCancelPopup.value = false

    // 刷新数据
    await loadBookingDetail()
  } catch (error: any) {
    uni.showToast({ title: error.message || '取消失败', icon: 'none' })
  } finally {
    cancelling.value = false
  }
}

function handleReschedule() {
  if (!booking.value) return
  uni.navigateTo({
    url: `/pages/booking/select-time?coachId=${booking.value.coach_id}&rescheduleId=${bookingId.value}`
  })
}

function goToReview() {
  uni.navigateTo({
    url: `/pages/review/create?bookingId=${bookingId.value}`
  })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}
  bookingId.value = parseInt(options.id) || 0

  if (bookingId.value) {
    loadBookingDetail()
  }
})
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20rpx;
  padding-bottom: 40rpx;
}

.course-card,
.feedback-card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  padding-bottom: 24rpx;
  border-bottom: 1rpx solid #f0f0f0;

  .course-name {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
  }

  .course-status {
    padding: 8rpx 20rpx;
    border-radius: 20rpx;
    font-size: 24rpx;

    &.pending,
    &.confirmed {
      background-color: #e8f5e9;
      color: #4caf50;
    }

    &.completed {
      background-color: #e3f2fd;
      color: #2196f3;
    }

    &.cancelled {
      background-color: #ffebee;
      color: #f44336;
    }

    &.no_show {
      background-color: #fff3e0;
      color: #ff9800;
    }
  }
}

.info-list {
  .info-item {
    display: flex;
    justify-content: space-between;
    padding: 16rpx 0;

    .info-label {
      font-size: 28rpx;
      color: #999;
    }

    .info-value {
      font-size: 28rpx;
      color: #333;
    }
  }
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
}

.feedback-content {
  .rating-row {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;

    .rating-label {
      font-size: 28rpx;
      color: #666;
      margin-right: 16rpx;
    }

    .rating-stars {
      .star {
        font-size: 32rpx;
        color: #ddd;

        &.active {
          color: #ffb800;
        }
      }
    }
  }

  .feedback-text {
    font-size: 28rpx;
    color: #333;
    line-height: 1.6;
    margin-bottom: 16rpx;
  }

  .suggestions {
    padding: 16rpx;
    background-color: #f5f5f5;
    border-radius: 8rpx;

    .suggestions-label {
      font-size: 26rpx;
      color: #666;
    }

    .suggestions-text {
      font-size: 26rpx;
      color: #333;
    }
  }
}

.action-buttons {
  margin-top: 40rpx;

  :deep(.wd-button) {
    margin-bottom: 20rpx;
  }

  .reviewed-tip {
    text-align: center;
    font-size: 28rpx;
    color: #999;
    padding: 20rpx;
  }
}

.cancel-popup {
  padding: 40rpx;

  .popup-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
    text-align: center;
    margin-bottom: 16rpx;
  }

  .popup-tip {
    font-size: 26rpx;
    color: #999;
    text-align: center;
    margin-bottom: 30rpx;
  }

  .cancel-input {
    width: 100%;
    height: 160rpx;
    padding: 20rpx;
    background-color: #f5f5f5;
    border-radius: 12rpx;
    font-size: 28rpx;
    box-sizing: border-box;
    margin-bottom: 30rpx;
  }

  .popup-buttons {
    display: flex;
    gap: 20rpx;

    :deep(.wd-button) {
      flex: 1;
    }
  }
}
</style>
