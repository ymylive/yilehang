<template>
  <view class="review-page">
    <!-- 璇剧▼淇℃伅 -->
    <view class="course-info">
      <view class="info-row">
        <text class="label">鏁欑粌</text>
        <text class="value">{{ coachName }}</text>
      </view>
      <view class="info-row">
        <text class="label">璇剧▼鏃堕棿</text>
        <text class="value">{{ courseTime }}</text>
      </view>
    </view>

    <!-- 璇勫垎 -->
    <view class="rating-section">
      <view class="section-title">璇剧▼璇勫垎</view>
      <view class="rating-stars">
        <view
          v-for="i in 5"
          :key="i"
          class="star-wrapper"
          @click="rating = i"
        >
          <text :class="['star', { active: i <= rating }]">鈽?/text>
        </view>
      </view>
      <view class="rating-text">{{ getRatingText(rating) }}</view>
    </view>

    <!-- 鏍囩閫夋嫨 -->
    <view class="tags-section">
      <view class="section-title">閫夋嫨鏍囩</view>
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

    <!-- 璇勪环鍐呭 -->
    <view class="content-section">
      <view class="section-title">璇勪环鍐呭锛堥€夊～锛?/view>
      <textarea
        v-model="content"
        placeholder="鍒嗕韩鎮ㄧ殑涓婅浣撻獙锛屽府鍔╁叾浠栧鍛樹簡瑙ｆ暀缁?.."
        class="content-input"
        :maxlength="500"
      />
      <view class="word-count">{{ content.length }}/500</view>
    </view>

    <!-- 鍖垮悕閫夐」 -->
    <view class="anonymous-section">
      <wd-checkbox v-model="isAnonymous">鍖垮悕璇勪环</wd-checkbox>
      <text class="anonymous-tip">鍖垮悕鍚庢暀缁冨皢鐪嬩笉鍒版偍鐨勫鍚?/text>
    </view>

    <!-- 鎻愪氦鎸夐挳 -->
    <view class="submit-section">
      <wd-button
        type="primary"
        block
        :disabled="rating === 0"
        :loading="submitting"
        @click="submitReview"
      >
        鎻愪氦璇勪环
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
  '涓撲笟',
  '鑰愬績',
  '鍑嗘椂',
  '鏈夎叮',
  '璁ょ湡璐熻矗',
  '璁茶В娓呮櫚',
  '鍥犳潗鏂芥暀',
  '姘涘洿濂?
]

function getRatingText(r: number): string {
  const texts = ['', '寰堝樊', '杈冨樊', '涓€鑸?, '婊℃剰', '闈炲父婊℃剰']
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
    const weekdays = ['鏃?, '涓€', '浜?, '涓?, '鍥?, '浜?, '鍏?]
    courseTime.value = `${date.getMonth() + 1}鏈?{date.getDate()}鏃?鍛?{weekdays[date.getDay()]} ${booking.start_time.substring(0, 5)}-${booking.end_time.substring(0, 5)}`
  } catch (error) {
    console.error('鍔犺浇棰勭害淇℃伅澶辫触', error)
  }
}

async function submitReview() {
  if (rating.value === 0) {
    uni.showToast({ title: '璇烽€夋嫨璇勫垎', icon: 'none' })
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

    uni.showToast({ title: '璇勪环鎴愬姛', icon: 'success' })

    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '璇勪环澶辫触', icon: 'none' })
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
      color: #FF8800;
      border-color: #FF8800;
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
