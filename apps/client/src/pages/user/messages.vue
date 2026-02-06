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
        <image src="/static/empty.png" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无消息</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Message {
  id: number
  type: string
  title: string
  content: string
  is_read: boolean
  created_at: string
}

const messages = ref<Message[]>([])
const loading = ref(false)

const mockMessages: Message[] = [
  {
    id: 1,
    type: 'booking',
    title: '预约成功',
    content: '您已成功预约明天10:00-11:00的私教课，教练：张教练。',
    is_read: false,
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    type: 'reminder',
    title: '课程提醒',
    content: '请准时参加今日16:00的课程，记得携带运动装备。',
    is_read: true,
    created_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 3,
    type: 'feedback',
    title: '教练反馈',
    content: '今天动作完成度很高，建议加强核心力量训练。',
    is_read: true,
    created_at: new Date(Date.now() - 86400000).toISOString()
  }
]

function getTypeIcon(type: string): string {
  const map: Record<string, string> = {
    booking: '📅',
    reminder: '⏰',
    feedback: '📝',
    system: '⚙'
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

function viewMessage(msg: Message) {
  msg.is_read = true
  const routes: Record<string, string> = {
    booking: `/pages/booking/detail?id=${msg.id}`,
    reminder: `/pages/booking/detail?id=${msg.id}`,
    feedback: `/pages/user/feedback-detail?id=${msg.id}`,
    system: `/pages/user/system-message?id=${msg.id}`
  }
  const url = routes[msg.type] || '/pages/user/messages'
  uni.navigateTo({ url })
}

onMounted(() => {
  messages.value = mockMessages
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
</style>
