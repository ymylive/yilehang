<template>
  <view class="page">
    <view class="header">
      <text class="title">精彩瞬间</text>
      <text class="desc">记录成长的每一刻</text>
    </view>

    <!-- 相册列表 -->
    <view class="album-grid">
      <view class="album-item" v-for="item in moments" :key="item.id" @click="viewMoment(item)">
        <image class="thumbnail" :src="item.thumbnail" mode="aspectFill" />
        <view class="overlay" v-if="item.type === 'video'">
          <text class="play-icon">▶</text>
        </view>
        <view class="info">
          <text class="date">{{ formatDate(item.created_at) }}</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty" v-if="!moments.length">
      <text class="icon">📸</text>
      <text class="text">暂无精彩瞬间</text>
      <text class="hint">完成训练后会自动生成精彩片段</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const moments = ref<any[]>([])

onMounted(() => {
  loadMoments()
})

function loadMoments() {
  // 模拟数据
  moments.value = [
    { id: 1, type: 'image', thumbnail: '/static/demo/moment1.jpg', created_at: '2024-02-01' },
    { id: 2, type: 'video', thumbnail: '/static/demo/moment2.jpg', created_at: '2024-01-28' },
    { id: 3, type: 'image', thumbnail: '/static/demo/moment3.jpg', created_at: '2024-01-25' }
  ]
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function viewMoment(item: any) {
  if (item.type === 'video') {
    uni.navigateTo({ url: `/pages/moments/video?id=${item.id}` })
  } else {
    uni.previewImage({
      urls: [item.thumbnail],
      current: item.thumbnail
    })
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.header {
  padding: 60rpx 30rpx 40rpx;
  background: linear-gradient(135deg, #E91E63, #F48FB1);
  color: #fff;
}

.header .title {
  font-size: 44rpx;
  font-weight: bold;
  display: block;
}

.header .desc {
  font-size: 28rpx;
  opacity: 0.9;
  margin-top: 12rpx;
}

.album-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4rpx;
  padding: 4rpx;
}

.album-item {
  position: relative;
  aspect-ratio: 1;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-icon {
  font-size: 60rpx;
  color: #fff;
}

.info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10rpx;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));
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
  font-size: 100rpx;
}

.empty .text {
  font-size: 32rpx;
  color: #333;
  margin-top: 20rpx;
}

.empty .hint {
  font-size: 26rpx;
  color: #999;
  margin-top: 10rpx;
}
</style>
