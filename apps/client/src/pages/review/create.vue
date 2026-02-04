<template>
  <view class="review-page">
    <!-- 课程信息 -->
    <view class="course-info">
      <view class="info-row">
        <text class="label">教练</text>
        <text class="value">{{ coachName }}</text>
      </view>
      <view class="info-row">
        <text class="label">课程时间</text>
        <text class="value">{{ courseTime }}</text>
      </view>
    </view>

    <!-- 评分 -->
    <view class="rating-section">
      <view class="section-title">课程评分</view>
      <view class="rating-stars">
        <view
          v-for="i in 5"
          :key="i"
          class="star-wrapper"
          @click="rating = i"
        >
          <text :class="['star', { active: i <= rating }]">★</text>
        </view>
      </view>
      <view class="rating-text">{{ getRatingText(rating) }}</view>
    </view>

    <!-- 标签选择 -->
    <view class="tags-section">
      <view class="section-title">选择标签</view>
      <view class="tags-list">
        <view
          v-for="tag in availableTags"
          :key="tag"
          :class="['tag-item', { active: selectedTags.includes(tag) }]"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </view>
      </view>
    </view>

    <!-- 评价内容 -->
    <view class="content-section">
      <view class="section-title">评价内容（选填）</view>
      <textarea
        v-model="content"
        placeholder="分享您的上课体验，帮助其他学员了解教练..."
        class="content-input"
        :maxlength="500"
      />
      <view class="word-count">{{ content.length }}/500</view>
    </view>

    <!-- 匿名选项 -->
    <view class="anonymous-section">
      <wd-checkbox v-model="isAnonymous">匿名评价</wd-checkbox>
      <text class="anonymous-tip">匿名后教练将看不到您的姓名</text>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <wd-button
        type="primary"
        block
        :disabled="rating === 0"
        :loading="submitting"
        @click="submitReview"
      >
        提交评价
      </wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { reviewApi, bookingApi } from '@/api'

const bookingId = ref(0)
const coachName = ref('')
const courseTime = ref('')

const rating = ref(0)
const selectedTags = ref<string[]>([])
const content = ref('')
const isAnonymous = ref(false)
const submitting = ref(false)

const availableTags = [
  '专业',
  '耐心',
  '准时',
  '有趣',
  '认真负责',
  '讲解清晰',
  '因材施教',
  '氛围好'
]

function getRatingText(r: number): string {
  const texts = ['', '很差', '较差', '一般', '满意', '非常满意']
  return texts[r] || ''
}

function toggleTag(tag: string) {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    if (selectedTags.value.length < 5) {
      selectedTags.value.push(tag)
    }
  }
}

async function loadBookingInfo() {
  try {
    const booking = await bookingApi.get(bookingId.value)
    coachName.value = booking.coach_name || ''
    const date = new Date(booking.booking_date)
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    courseTime.value = `${date.getMonth() + 1}月${date.getDate()}日 周${weekdays[date.getDay()]} ${booking.start_time.substring(0, 5)}-${booking.end_time.substring(0, 5)}`
  } catch (error) {
    console.error('加载预约信息失败', error)
  }
}

async function submitReview() {
  if (rating.value === 0) {
    uni.showToast({ title: '请选择评分', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await reviewApi.create({
      booking_id: bookingId.value,
      rating: rating.value,
      content: content.value || undefined,
      tags: selectedTags.value.length > 0 ? selectedTags.value : undefined,
      is_anonymous: isAnonymous.value
    })

    uni.showToast({ title: '评价成功', icon: 'success' })

    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '评价失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}
  bookingId.value = parseInt(options.bookingId) || 0

  if (bookingId.value) {
    loadBookingInfo()
  }
})
</script>

<style lang="scss" scoped>
.review-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 140rpx;
}

.course-info {
  background-color: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;

  .info-row {
    display: flex;
    justify-content: space-between;
    padding: 12rpx 0;

    .label {
      font-size: 28rpx;
      color: #999;
    }

    .value {
      font-size: 28rpx;
      color: #333;
    }
  }
}

.rating-section,
.tags-section,
.content-section {
  background-color: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
}

.rating-stars {
  display: flex;
  justify-content: center;
  gap: 20rpx;

  .star-wrapper {
    padding: 10rpx;
  }

  .star {
    font-size: 60rpx;
    color: #ddd;
    transition: all 0.2s;

    &.active {
      color: #ffb800;
      transform: scale(1.1);
    }
  }
}

.rating-text {
  text-align: center;
  font-size: 28rpx;
  color: #ff9800;
  margin-top: 16rpx;
  height: 40rpx;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;

  .tag-item {
    padding: 16rpx 28rpx;
    background-color: #f5f5f5;
    border-radius: 30rpx;
    font-size: 26rpx;
    color: #666;
    border: 2rpx solid transparent;

    &.active {
      background-color: #e8f5e9;
      color: #4caf50;
      border-color: #4caf50;
    }
  }
}

.content-input {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.word-count {
  text-align: right;
  font-size: 24rpx;
  color: #999;
  margin-top: 12rpx;
}

.anonymous-section {
  display: flex;
  align-items: center;
  background-color: #fff;
  padding: 30rpx;

  .anonymous-tip {
    font-size: 24rpx;
    color: #999;
    margin-left: 16rpx;
  }
}

.submit-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background-color: #fff;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
}
</style>
