<template>
  <view class="page-guard">
    <slot v-if="!hasError"></slot>

    <view v-else class="fallback-card">
      <view class="icon-wrap">
        <wd-icon name="warning" size="44rpx" color="#f97316" />
      </view>
      <text class="title">{{ titleText }}</text>
      <text class="desc">{{ descText }}</text>
      <button class="retry-btn" @click="retry">{{ retryText }}</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onErrorCaptured, ref } from 'vue'
import { trackError, trackEvent } from '@/utils/telemetry'

const props = withDefaults(
  defineProps<{
    page: string
    title?: string
    desc?: string
    retryLabel?: string
  }>(),
  {
    title: '页面加载异常',
    desc: '已触发保护机制，请重试',
    retryLabel: '重新加载'
  }
)

const emit = defineEmits<{ (e: 'retry'): void }>()
const hasError = ref(false)

const titleText = computed(() => props.title)
const descText = computed(() => props.desc)
const retryText = computed(() => props.retryLabel)

onErrorCaptured((error, _instance, info) => {
  hasError.value = true
  trackError('page.boundary.error', error, { page: props.page, info })
  return false
})

function retry() {
  hasError.value = false
  trackEvent('page.boundary.retry', { page: props.page })
  emit('retry')
}
</script>

<style scoped>
.page-guard {
  min-height: 100vh;
}

.fallback-card {
  margin: 36rpx 24rpx 0;
  border-radius: 24rpx;
  padding: 34rpx 26rpx;
  background: linear-gradient(180deg, #ffffff, #fffaf4);
  border: 1rpx solid rgba(253, 186, 116, 0.48);
  box-shadow: 0 16rpx 30rpx rgba(148, 76, 13, 0.12);
  text-align: center;
}

.icon-wrap {
  width: 86rpx;
  height: 86rpx;
  border-radius: 24rpx;
  margin: 0 auto 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff3e4;
}

.title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #1f2937;
}

.desc {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #64748b;
}

.retry-btn {
  margin-top: 20rpx;
  height: 76rpx;
  border: none;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #ffb347, #ff8a1f);
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 700;
}

.retry-btn::after {
  border: none;
}
</style>

