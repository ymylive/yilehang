<template>
  <view class="detail-page">
    <view class="booking-card" v-if="booking">
      <view class="booking-head">
        <text class="course-name">{{ booking.course_name || '课程详情' }}</text>
        <text :class="['status-tag', booking.status]">{{ getStatusText(booking.status) }}</text>
      </view>

      <view class="info-list">
        <view class="info-item">
          <text class="label">教练</text>
          <text class="value">{{ booking.coach_name || '待定' }}</text>
        </view>
        <view class="info-item">
          <text class="label">日期</text>
          <text class="value">{{ formatDate(booking.booking_date) }}</text>
        </view>
        <view class="info-item">
          <text class="label">时间</text>
          <text class="value">{{ formatClock(booking.start_time) }} - {{ formatClock(booking.end_time) }}</text>
        </view>
        <view class="info-item">
          <text class="label">课程类型</text>
          <text class="value">{{ booking.course_type === 'private' ? '私教课' : '小班课' }}</text>
        </view>
        <view class="info-item" v-if="booking.remark">
          <text class="label">备注</text>
          <text class="value">{{ booking.remark }}</text>
        </view>
      </view>
    </view>

    <view class="feedback-card" v-if="feedback">
      <view class="card-title">教练反馈</view>
      <view class="feedback-content">
        <view class="rating-row" v-if="feedback.performance_rating">
          <text class="rating-label">表现评分</text>
          <view class="rating-stars">
            <image
              v-for="(icon, index) in getRatingStarIcons(feedback.performance_rating)"
              :key="index"
              :src="icon"
              class="rating-star-icon"
              mode="aspectFit"
            />
          </view>
        </view>
        <text class="content">{{ feedback.content }}</text>
        <view class="suggestions" v-if="feedback.suggestions">
          <text class="suggestions-label">改进建议</text>
          <text class="suggestions-text">{{ feedback.suggestions }}</text>
        </view>
      </view>
    </view>

    <view class="action-card" v-if="booking">
      <template v-if="booking.status === 'confirmed' || booking.status === 'pending'">
        <button class="action-btn ghost" v-if="canReschedule" @click="handleReschedule">改期</button>
        <button class="action-btn danger" v-if="canCancel" @click="openCancelPanel">取消预约</button>
      </template>

      <template v-if="booking.status === 'completed'">
        <button class="action-btn primary" v-if="!hasReviewed" @click="goToReview">评价课程</button>
        <view v-else class="reviewed-tip">已评价</view>
      </template>
    </view>

    <view class="cancel-mask" v-if="showCancelPanel" @click="closeCancelPanel">
      <view class="cancel-panel" @click.stop>
        <text class="panel-title">取消预约</text>
        <text class="panel-tip">可填写取消原因（选填）</text>
        <textarea v-model="cancelReason" class="cancel-input" maxlength="200" placeholder="请输入取消原因" />
        <view class="panel-actions">
          <button class="panel-btn ghost" @click="closeCancelPanel">再想想</button>
          <button class="panel-btn danger" :disabled="cancelling" @click="confirmCancel">{{ cancelling ? '处理中...' : '确认取消' }}</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { bookingApi, reviewApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

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
const ratingStarActiveIcon = getSemanticIcon('icon-star-filled')
const ratingStarInactiveIcon = getSemanticIcon('icon-star-outline')

const showCancelPanel = ref(false)
const cancelReason = ref('')
const cancelling = ref(false)

const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const canCancel = computed(() => {
  if (!booking.value) return false
  const dateTime = new Date(`${booking.value.booking_date}T${booking.value.start_time}`)
  const now = new Date()
  const diff = dateTime.getTime() - now.getTime()
  return diff > 2 * 60 * 60 * 1000
})

const canReschedule = computed(() => canCancel.value)

function getStatusText(status?: string) {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    cancelled: '已取消',
    completed: '已完成',
    no_show: '未到课'
  }
  return map[status || ''] || status || ''
}

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日 ${weekdays[date.getDay()]}`
}

function formatClock(timeStr?: string) {
  if (!timeStr) return '--:--'
  return timeStr.slice(0, 5)
}

function getRatingStarIcons(score: number | null) {
  if (!score) {
    return Array.from({ length: 5 }, () => ratingStarInactiveIcon)
  }
  const num = Math.max(0, Math.min(5, Math.round(score)))
  return Array.from({ length: 5 }, (_, index) => (index < num ? ratingStarActiveIcon : ratingStarInactiveIcon))
}

async function loadBookingDetail() {
  try {
    booking.value = await bookingApi.get(bookingId.value)

    if (booking.value?.status === 'completed') {
      const list = await reviewApi.getMyFeedbacks(1, 50)
      const matched = (list || []).find((item: any) => item.booking_id === bookingId.value)
      feedback.value = matched || null
      hasReviewed.value = !!matched
    } else {
      feedback.value = null
      hasReviewed.value = false
    }
  } catch (error: any) {
    uni.showToast({ title: error.message || '加载预约失败', icon: 'none' })
  }
}

function openCancelPanel() {
  showCancelPanel.value = true
}

function closeCancelPanel() {
  showCancelPanel.value = false
  cancelReason.value = ''
}

async function confirmCancel() {
  if (cancelling.value) return
  cancelling.value = true

  try {
    await bookingApi.cancel(bookingId.value, cancelReason.value || undefined)
    uni.showToast({ title: '取消成功', icon: 'success' })
    closeCancelPanel()
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
  uni.navigateTo({ url: `/pages/review/create?bookingId=${bookingId.value}` })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}
  bookingId.value = parseInt(options.id) || 0
  if (bookingId.value) loadBookingDetail()
})
</script>

<style lang="scss" scoped>
.detail-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.booking-card,
.feedback-card,
.action-card {
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 20rpx;
  margin-bottom: 14rpx;
}

.booking-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.course-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #1f2533;
}

.status-tag {
  border-radius: 999rpx;
  padding: 6rpx 14rpx;
  font-size: 21rpx;
}

.status-tag.pending,
.status-tag.confirmed {
  background: #fff1df;
  color: #df7f17;
}

.status-tag.completed {
  background: #e6f5eb;
  color: #239458;
}

.status-tag.cancelled,
.status-tag.no_show {
  background: #ffebe8;
  color: #cc5c4e;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 14rpx;
  background: #f9fbff;
  padding: 14rpx;
}

.label {
  font-size: 24rpx;
  color: #8992a6;
}

.value {
  font-size: 25rpx;
  color: #2b3448;
  font-weight: 600;
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2533;
  margin-bottom: 14rpx;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 10rpx;
}

.rating-label {
  font-size: 24rpx;
  color: #8992a6;
}

.rating-stars {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.rating-star-icon {
  width: 24rpx;
  height: 24rpx;
}

.content {
  font-size: 25rpx;
  line-height: 1.6;
  color: #4f5870;
}

.suggestions {
  margin-top: 10rpx;
  border-radius: 14rpx;
  background: #fff8ee;
  padding: 12rpx;
}

.suggestions-label {
  display: block;
  font-size: 22rpx;
  color: #de7f16;
}

.suggestions-text {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #4f5870;
}

.action-btn {
  width: 100%;
  border: none;
  border-radius: 16rpx;
  height: 84rpx;
  line-height: 84rpx;
  font-size: 30rpx;
  font-weight: 700;
  margin-bottom: 10rpx;
}

.action-btn::after {
  border: none;
}

.action-btn.primary {
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  color: #fff;
}

.action-btn.ghost {
  background: #fff8ee;
  color: #d97810;
}

.action-btn.danger {
  background: #fff1ef;
  color: #d95b4a;
}

.reviewed-tip {
  text-align: center;
  font-size: 26rpx;
  color: #9099ab;
  padding: 8rpx 0;
}

.cancel-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: flex-end;
  z-index: 30;
}

.cancel-panel {
  width: 100%;
  border-radius: 24rpx 24rpx 0 0;
  background: #fff;
  padding: 24rpx;
}

.panel-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2533;
}

.panel-tip {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #9099ab;
}

.cancel-input {
  width: 100%;
  min-height: 140rpx;
  border-radius: 14rpx;
  background: #f7f8fb;
  padding: 14rpx;
  margin-top: 12rpx;
  box-sizing: border-box;
  font-size: 24rpx;
}

.panel-actions {
  margin-top: 12rpx;
  display: flex;
  justify-content: flex-end;
  gap: 10rpx;
}

.panel-btn {
  border: none;
  border-radius: 999rpx;
  padding: 12rpx 24rpx;
  font-size: 22rpx;
}

.panel-btn::after {
  border: none;
}

.panel-btn.ghost {
  background: #eff2f7;
  color: #6d768c;
}

.panel-btn.danger {
  background: #ffeceb;
  color: #d95b4a;
}
</style>
