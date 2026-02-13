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
          <image
            :src="i <= rating ? ratingStarActiveIcon : ratingStarInactiveIcon"
            :class="['star', { active: i <= rating }]"
            mode="aspectFit"
          />
        </view>
      </view>
      <view class="rating-text">{{ getRatingText(rating) }}</view>
    </view>

    <!-- 标签选择 -->
    <view class="tags-section">
      <view class="section-title">标签选择</view>
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
      <view class="section-title">评价内容</view>
      <textarea
        v-model="content"
        placeholder="说说孩子的表现、教练的指导或课程体验..."
        class="content-input"
        :maxlength="500"
      />
      <view class="word-count">{{ content.length }}/500</view>
    </view>

    <!-- 匿名评价 -->
    <view class="anonymous-section">
      <wd-checkbox v-model="isAnonymous">匿名评价</wd-checkbox>
      <text class="anonymous-tip">匿名后仅展示评价内容，不显示姓名</text>
    </view>

    <!-- 提交 -->
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
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, onMounted } from 'vue'
import { reviewApi, bookingApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

const bookingId = ref(0)
const coachName = ref('')
const courseTime = ref('')

const rating = ref(0)
const ratingStarActiveIcon = getSemanticIcon('icon-star-filled')
const ratingStarInactiveIcon = getSemanticIcon('icon-star-outline')
const selectedTags = ref<string[]>([])
const content = ref('')
const isAnonymous = ref(false)
const submitting = ref(false)

const availableTags = [
  '讲解清晰',
  '耐心细致',
  '专业度高',
  '氛围好',
  '动作纠正到位',
  '互动有趣',
  '孩子喜欢'
]

function getRatingText(r: number): string {
  const texts = ['', '非常不满意', '不满意', '一般', '满意', '非常满意']
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
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    courseTime.value = `${date.getMonth() + 1}月${date.getDate()}日 ${weekdays[date.getDay()]} ${booking.start_time.substring(0, 5)}-${booking.end_time.substring(0, 5)}`
  } catch (error) {
    console.error('加载课程信息失败', error)
  }
}

async function submitReview() {
  if (rating.value === 0) {
    uni.showToast({ title: '请先打分', icon: 'none' })
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
  padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
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
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.rating-stars {
  display: flex;
  gap: 10rpx;
}

.star {
  width: 48rpx;
  height: 48rpx;

  &.active {
    transform: scale(1.02);
  }
}

.rating-text {
  font-size: 26rpx;
  color: #999;
  margin-top: 12rpx;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag-item {
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
  background: #f5f5f5;
  font-size: 24rpx;
  color: #666;

  &.active {
    background: #FF8800;
    color: #fff;
  }
}

.content-input {
  width: 100%;
  height: 200rpx;
  border: 1rpx solid #eee;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 26rpx;
  color: #333;
  box-sizing: border-box;
}

.word-count {
  text-align: right;
  color: #999;
  font-size: 22rpx;
  margin-top: 8rpx;
}

.anonymous-section {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 30rpx;
  background: #fff;
  margin-bottom: 20rpx;
  font-size: 24rpx;
  color: #666;
}

.submit-section {
  padding: 0 30rpx;
}
</style>
