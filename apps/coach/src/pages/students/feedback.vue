<template>
  <view class="feedback-page">
    <!-- 学员信息 -->
    <view class="student-info">
      <view class="student-avatar">{{ studentName.charAt(0) }}</view>
      <view class="student-name">{{ studentName }}</view>
    </view>

    <!-- 表现评分 -->
    <view class="section">
      <view class="section-title">表现评分</view>
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
      <view class="rating-labels">
        <text>较差</text>
        <text>一般</text>
        <text>良好</text>
        <text>优秀</text>
        <text>出色</text>
      </view>
    </view>

    <!-- 学习反馈 -->
    <view class="section">
      <view class="section-title">学习反馈 <text class="required">*</text></view>
      <textarea
        v-model="content"
        placeholder="请描述学员本次课程的学习情况、进步表现等..."
        class="feedback-input"
        :maxlength="500"
      />
      <view class="word-count">{{ content.length }}/500</view>
    </view>

    <!-- 改进建议 -->
    <view class="section">
      <view class="section-title">改进建议（选填）</view>
      <textarea
        v-model="suggestions"
        placeholder="请给出针对性的改进建议..."
        class="feedback-input short"
        :maxlength="300"
      />
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <wd-button
        type="primary"
        block
        :disabled="!content"
        :loading="submitting"
        @click="submitFeedback"
      >
        提交反馈
      </wd-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const studentId = ref(0)
const bookingId = ref(0)
const studentName = ref('')
const rating = ref(0)
const content = ref('')
const suggestions = ref('')
const submitting = ref(false)

async function submitFeedback() {
  if (!content.value) {
    uni.showToast({ title: '请填写学习反馈', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    // TODO: 调用API提交反馈
    await new Promise(resolve => setTimeout(resolve, 1000))

    uni.showToast({ title: '提交成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '提交失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}

  studentId.value = parseInt(options.studentId) || 0
  bookingId.value = parseInt(options.bookingId) || 0
  studentName.value = decodeURIComponent(options.studentName || '学员')
})
</script>

<style lang="scss" scoped>
.feedback-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 140rpx;
}

.student-info {
  display: flex;
  align-items: center;
  padding: 30rpx;
  background-color: #fff;

  .student-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36rpx;
    font-weight: 600;
  }

  .student-name {
    margin-left: 20rpx;
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
  }
}

.section {
  background-color: #fff;
  margin-top: 20rpx;
  padding: 30rpx;

  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 24rpx;

    .required {
      color: #f44336;
    }
  }
}

.rating-stars {
  display: flex;
  justify-content: center;
  gap: 30rpx;

  .star-wrapper {
    padding: 10rpx;
  }

  .star {
    font-size: 56rpx;
    color: #ddd;
    transition: all 0.2s;

    &.active {
      color: #ffb800;
    }
  }
}

.rating-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
  padding: 0 20rpx;

  text {
    font-size: 22rpx;
    color: #999;
  }
}

.feedback-input {
  width: 100%;
  height: 240rpx;
  padding: 20rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;

  &.short {
    height: 160rpx;
  }
}

.word-count {
  text-align: right;
  font-size: 24rpx;
  color: #999;
  margin-top: 12rpx;
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
