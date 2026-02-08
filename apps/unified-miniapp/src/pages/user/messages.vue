<template>
  <view class="messages-page">
    <view class="message-list">
      <view
        v-for="msg in messages"
        :key="msg.id"
        class="message-item"
        @click="viewMessage(msg)"
      >
        <view :class="['message-icon', msg.type]">
          <text>{{ getTypeIcon(msg.type) }}</text>
        </view>
        <view class="message-content">
          <view class="message-header">
            <text class="message-title">{{ msg.title }}</text>
            <text class="message-time">{{ formatTime(msg.created_at) }}</text>
          </view>
          <view class="message-body">{{ msg.content }}</view>
        </view>
        <view class="unread-dot" v-if="!msg.is_read"></view>
      </view>

      <view v-if="messages.length === 0 && !loading" class="empty-state">
        <image src="/static/empty.svg" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无消息</text>
      </view>

      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { notificationApi } from '@/api'

interface Message {
  id: number
  type: string
  title: string
  content: string
  is_read: boolean
  created_at: string
  related_id?: number
  related_type?: string
}

const messages = ref<Message[]>([])
const loading = ref(false)
const total = ref(0)
const unreadCount = ref(0)

function getTypeIcon(type: string): string {
  const map: Record<string, string> = {
    booking: '📅',
    reminder: '⏰',
    feedback: '📝',
    system: '⚙',
    chat: '💬'
  }
  return map[type] || '•'
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

  return `${date.getMonth() + 1}-${date.getDate()}`
}

async function loadMessages() {
  loading.value = true
  try {
    const res = await notificationApi.list()
    messages.value = res.items || []
    total.value = res.total || 0
    unreadCount.value = res.unread_count || 0
  } catch (error) {
    console.error('加载消息失败', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function viewMessage(msg: Message) {
  // 标记已读
  if (!msg.is_read) {
    try {
      await notificationApi.markRead(msg.id)
      msg.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      console.error('标记已读失败', error)
    }
  }

  // 根据类型跳转
  const routes: Record<string, string> = {
    booking: `/pages/booking/detail?id=${msg.related_id || msg.id}`,
    reminder: `/pages/schedule/detail?id=${msg.related_id || msg.id}`,
    feedback: `/pages/review/detail?id=${msg.related_id || msg.id}`,
    chat: `/pages/chat/conversation?id=${msg.related_id || msg.id}`,
    system: ''
  }
  const url = routes[msg.type]
  if (url) {
    uni.navigateTo({ url })
  }
}

onMounted(() => {
  loadMessages()
})

// 下拉刷新
onPullDownRefresh(async () => {
  await loadMessages()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
.messages-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.message-list {
  padding: 20rpx;
}

.message-item {
  display: flex;
  align-items: flex-start;
  background-color: #fff;
  padding: 24rpx;
  border-radius: 12rpx;
  margin-bottom: 16rpx;
  position: relative;

  .message-icon {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32rpx;
    margin-right: 20rpx;
    flex-shrink: 0;

    &.booking {
      background-color: #e8f5e9;
    }

    &.reminder {
      background-color: #fff3e0;
    }

    &.feedback {
      background-color: #e3f2fd;
    }

    &.system {
      background-color: #f3e5f5;
    }

    &.chat {
      background-color: #e0f7fa;
    }
  }
}

.message-content {
  flex: 1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8rpx;
}

.message-title {
  font-size: 28rpx;
  color: #333;
  font-weight: 600;
}

.message-time {
  font-size: 22rpx;
  color: #999;
}

.message-body {
  font-size: 24rpx;
  color: #666;
  line-height: 1.6;
}

.unread-dot {
  width: 12rpx;
  height: 12rpx;
  background-color: #FF3B30;
  border-radius: 50%;
  position: absolute;
  top: 16rpx;
  right: 16rpx;
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;

  .empty-image {
    width: 200rpx;
    height: 200rpx;
    margin-bottom: 20rpx;
  }

  .empty-text {
    color: #999;
    font-size: 26rpx;
  }
}

.loading-state {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
}
</style>
