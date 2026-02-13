<template>
  <view class="page">
    <view class="header">
      <text class="title">精彩瞬间</text>
      <text class="desc">记录每一次成长高光时刻</text>
    </view>

    <view class="album-grid" v-if="moments.length">
      <view class="album-item" v-for="item in moments" :key="item.id" @click="viewMoment(item)">
        <image class="thumbnail" :src="item.thumbnail" mode="aspectFill" />
        <view class="overlay" v-if="item.type === 'video'">
          <image :src="playIcon" class="play-icon" mode="aspectFit" />
        </view>
        <view class="info">
          <text class="date">{{ formatDate(item.created_at) }}</text>
        </view>
      </view>
    </view>

    <view class="empty" v-else>
      <view class="icon">
        <image :src="momentsEmptyIcon" class="empty-icon-image" mode="aspectFit" />
      </view>
      <text class="text">暂无精彩瞬间</text>
      <text class="hint">完成训练后会自动生成内容</text>
    </view>

    <DynamicTabBar />
  </view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, onMounted } from 'vue'
import { safeNavigate } from '@/utils/safe-nav'
import { getSemanticIcon } from '@/constants/semantic-icons'

interface MomentItem {
  id: number
  type: 'image' | 'video'
  thumbnail: string
  created_at: string
}

const moments = ref<MomentItem[]>([])
const playIcon = getSemanticIcon('icon-play-filled')
const momentsEmptyIcon = getSemanticIcon('moments-empty')

onMounted(() => {
  loadMoments()
})

function loadMoments() {
  moments.value = [
    { id: 1, type: 'image', thumbnail: '/static/demo/moment1.jpg', created_at: '2024-02-01' },
    { id: 2, type: 'video', thumbnail: '/static/demo/moment2.jpg', created_at: '2024-01-28' },
    { id: 3, type: 'image', thumbnail: '/static/demo/moment3.jpg', created_at: '2024-01-25' }
  ]
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}-${date.getDate()}`
}

function viewMoment(item: MomentItem) {
  if (item.type === 'video') {
    const opened = safeNavigate(`/pages/moments/video?id=${item.id}`, 'navigateTo', '视频页暂未开放')
    if (!opened) {
      uni.previewImage({
        urls: [item.thumbnail],
        current: item.thumbnail
      })
    }
    return
  }

  uni.previewImage({
    urls: [item.thumbnail],
    current: item.thumbnail
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fbff 0%, #f3f7ff 35%, #eef4ff 100%);
  padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
}

.header {
  padding: 60rpx 30rpx 36rpx;
  background: linear-gradient(135deg, #ffb347, #ff8800);
  color: #fff;
  border-radius: 0 0 34rpx 34rpx;
}

.header .title {
  font-size: 44rpx;
  font-weight: 700;
  display: block;
}

.header .desc {
  font-size: 26rpx;
  opacity: 0.9;
  margin-top: 10rpx;
}

.album-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10rpx;
  padding: 20rpx;
}

.album-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 14rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 18rpx rgba(25, 52, 92, 0.12);
  transition: transform 180ms ease;
}

.album-item:active {
  transform: scale(0.98);
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-icon {
  width: 54rpx;
  height: 54rpx;
}

.info {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 10rpx;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.48));
}

.date {
  font-size: 22rpx;
  color: #fff;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty .icon {
  width: 118rpx;
  height: 118rpx;
  border-radius: 28rpx;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon-image {
  width: 66rpx;
  height: 66rpx;
}

.empty .text {
  font-size: 32rpx;
  color: #1e293b;
  margin-top: 20rpx;
}

.empty .hint {
  font-size: 26rpx;
  color: #64748b;
  margin-top: 10rpx;
}
</style>
