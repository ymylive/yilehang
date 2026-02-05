<template>
  <view class="messages-page">
    <!-- 娑堟伅鍒楄〃 -->
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

      <!-- 绌虹姸鎬?-->
      <view v-if="messages.length === 0 && !loading" class="empty-state">
        <image src="/static/empty.png" mode="aspectFit" class="empty-image" />
        <text class="empty-text">鏆傛棤娑堟伅</text>
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

// 妯℃嫙娑堟伅鏁版嵁
const mockMessages: Message[] = [
  {
    id: 1,
    type: 'booking',
    title: '棰勭害鎴愬姛',
    content: '鎮ㄥ凡鎴愬姛棰勭害鏄庡ぉ10:00-11:00鐨勭鏁欒锛屾暀缁冿細寮犳暀缁?,
    is_read: false,
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    type: 'reminder',
    title: '涓婅鎻愰啋',
    content: '鎮ㄩ绾︾殑璇剧▼灏嗗湪1灏忔椂鍚庡紑濮嬶紝璇峰噯鏃跺埌杈?,
    is_read: true,
    created_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 3,
    type: 'feedback',
    title: '鏁欑粌鍙嶉',
    content: '寮犳暀缁冨鎮ㄧ殑璇剧▼杩涜浜嗗弽棣堬紝鐐瑰嚮鏌ョ湅璇︽儏',
    is_read: true,
    created_at: new Date(Date.now() - 86400000).toISOString()
  }
]

function getTypeIcon(type: string): string {
  const map: Record<string, string> = {
    booking: '馃搮',
    reminder: '鈴?,
    feedback: '馃摑',
    system: '馃摙'
  }
  return map[type] || '馃搶'
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '鍒氬垰'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}鍒嗛挓鍓峘
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}灏忔椂鍓峘
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}澶╁墠`

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
  // 鍔犺浇娑堟伅鍒楄〃
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

  .message-content {
    flex: 1;
    overflow: hidden;

    .message-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12rpx;

      .message-title {
        font-size: 30rpx;
        font-weight: 600;
        color: #333;
      }

      .message-time {
        font-size: 24rpx;
        color: #999;
      }
    }

    .message-body {
      font-size: 26rpx;
      color: #666;
      line-height: 1.5;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
  }

  .unread-dot {
    position: absolute;
    top: 24rpx;
    right: 24rpx;
    width: 16rpx;
    height: 16rpx;
    background-color: #f44336;
    border-radius: 50%;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;

  .empty-image {
    width: 160rpx;
    height: 160rpx;
    margin-bottom: 16rpx;
  }

  .empty-text {
    font-size: 28rpx;
    color: #999;
  }
}
</style>
