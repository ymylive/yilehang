<template>
  <view class="feedback-page">
    <view class="header-card">
      <view class="student-avatar">{{ displayStudentName.charAt(0) }}</view>
      <view class="header-meta">
        <text class="header-title">{{ t.feedbackTitle }}</text>
        <text class="header-sub">{{ displayStudentName }}</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">{{ t.performanceRating }}</view>
      <view class="rating-stars">
        <view
          v-for="i in 5"
          :key="i"
          class="star-wrapper"
          @click="rating = i"
        >
          <text :class="['star', { active: i <= rating }]">{{ t.star }}</text>
        </view>
      </view>
      <view class="rating-labels">
        <text v-for="(label, idx) in t.ratingLabels" :key="idx">{{ label }}</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">{{ t.studyFeedback }} <text class="required">*</text></view>
      <textarea
        v-model="content"
        :placeholder="t.feedbackPlaceholder"
        class="feedback-input"
        :maxlength="500"
      />
      <view class="word-count">{{ content.length }}/500</view>
    </view>

    <view class="section-card">
      <view class="section-title">{{ t.suggestionLabel }}</view>
      <textarea
        v-model="suggestions"
        :placeholder="t.suggestionPlaceholder"
        class="feedback-input short"
        :maxlength="300"
      />
    </view>

    <view class="submit-section">
      <wd-button
        type="primary"
        block
        :disabled="!content.trim()"
        :loading="submitting"
        @click="submitFeedback"
      >
        {{ t.submit }}
      </wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { coachFeedbackApi } from '@/api/index'

const t = {
  feedbackTitle: '\u5b66\u4e60\u53cd\u9988',
  performanceRating: '\u8868\u73b0\u8bc4\u5206',
  studyFeedback: '\u5b66\u4e60\u53cd\u9988',
  suggestionLabel: '\u6539\u8fdb\u5efa\u8bae\uff08\u9009\u586b\uff09',
  feedbackPlaceholder: '\u8bf7\u63cf\u8ff0\u672c\u6b21\u8bfe\u7a0b\u7684\u5b66\u4e60\u60c5\u51b5\u3001\u8fdb\u6b65\u8868\u73b0\u4e0e\u4e0b\u4e00\u6b65\u91cd\u70b9\u3002',
  suggestionPlaceholder: '\u53ef\u9009\uff0c\u53ef\u5199\u5bb6\u5ead\u7ec3\u4e60\u3001\u4f5c\u606f\u6216\u996e\u98df\u65b9\u9762\u5efa\u8bae\u3002',
  submit: '\u63d0\u4ea4\u53cd\u9988',
  submitSuccess: '\u63d0\u4ea4\u6210\u529f',
  submitFailed: '\u63d0\u4ea4\u5931\u8d25',
  emptyContent: '\u8bf7\u586b\u5199\u5b66\u4e60\u53cd\u9988',
  studentDefault: '\u5b66\u5458',
  star: '\u2605',
  ratingLabels: [
    '\u8f83\u5dee',
    '\u4e00\u822c',
    '\u826f\u597d',
    '\u4f18\u79c0',
    '\u51fa\u8272'
  ]
} as const

const studentId = ref(0)
const bookingId = ref(0)
const studentName = ref('')
const rating = ref(0)
const content = ref('')
const suggestions = ref('')
const submitting = ref(false)

const displayStudentName = computed(() => studentName.value || t.studentDefault)

function parseOptions() {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  return (currentPage as any).$page?.options || {}
}

async function submitFeedback() {
  const feedbackContent = content.value.trim()
  if (!feedbackContent) {
    uni.showToast({ title: t.emptyContent, icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await coachFeedbackApi.createFeedback({
      booking_id: bookingId.value || undefined,
      student_id: studentId.value,
      performance_rating: rating.value || null,
      content: feedbackContent,
      suggestions: suggestions.value.trim() || null
    })

    uni.showToast({ title: t.submitSuccess, icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 800)
  } catch (error: any) {
    uni.showToast({ title: error.message || t.submitFailed, icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const options = parseOptions()

  studentId.value = parseInt(options.studentId) || 0
  bookingId.value = parseInt(options.bookingId) || 0

  if (options.studentName) {
    try {
      studentName.value = decodeURIComponent(options.studentName)
    } catch {
      studentName.value = options.studentName
    }
  }
})
</script>

<style lang="scss" scoped>
.feedback-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding: 20rpx;
  padding-bottom: calc(150rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(150rpx + env(safe-area-inset-bottom));
}

.header-card {
  border-radius: 24rpx;
  background: linear-gradient(135deg, #ffbc47 0%, #ff8d1f 72%);
  box-shadow: 0 14rpx 28rpx rgba(255, 141, 31, 0.22);
  padding: 26rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.student-avatar {
  width: 86rpx;
  height: 86rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.22);
  border: 2rpx solid rgba(255, 255, 255, 0.36);
  color: #fff;
  font-size: 34rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-meta {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.header-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #fff;
}

.header-sub {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.section-card {
  margin-top: 16rpx;
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 24rpx;
}

.section-title {
  font-size: 28rpx;
  color: #20283a;
  font-weight: 700;
  margin-bottom: 16rpx;
}

.required {
  color: #e35746;
}

.rating-stars {
  display: flex;
  justify-content: center;
  gap: 18rpx;
}

.star-wrapper {
  padding: 8rpx;
}

.star {
  font-size: 56rpx;
  line-height: 1;
  color: #e5e8ef;
}

.star.active {
  color: #f3a21d;
}

.rating-labels {
  margin-top: 14rpx;
  display: flex;
  justify-content: space-between;
}

.rating-labels text {
  font-size: 22rpx;
  color: #8f98ad;
}

.feedback-input {
  width: 100%;
  min-height: 220rpx;
  border-radius: 16rpx;
  border: 2rpx solid #eef1f7;
  background: #f8f9fc;
  padding: 18rpx;
  box-sizing: border-box;
  font-size: 26rpx;
  color: #30384d;
}

.feedback-input.short {
  min-height: 150rpx;
}

.word-count {
  margin-top: 10rpx;
  text-align: right;
  font-size: 22rpx;
  color: #97a0b3;
}

.submit-section {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20rpx 24rpx calc(20rpx + constant(safe-area-inset-bottom));
  padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -6rpx 18rpx rgba(31, 37, 51, 0.08);
}
</style>
