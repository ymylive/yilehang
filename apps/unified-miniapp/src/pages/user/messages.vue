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
          <wd-icon :name="getTypeIcon(msg.type)" size="34rpx" :color="getTypeIconColor(msg.type)" />
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
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { notificationApi } from '@/api'
import { safeNavigate } from '@/utils/safe-nav'

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
    booking: 'calendar',
    reminder: 'notification',
    feedback: 'note',
    system: 'setting',
    chat: 'chat'
  }
  return map[type] || 'tips'
}

function getTypeIconColor(type: string): string {
  const map: Record<string, string> = {
    booking: '#2e7d32',
    reminder: '#ff8f00',
    feedback: '#1d4ed8',
    system: '#7e57c2',
    chat: '#0d9488'
  }
  return map[type] || '#64748b'
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
    const res: any = await notificationApi.list()
    messages.value = Array.isArray(res?.items) ? res.items : (Array.isArray(res) ? res : [])
    total.value = Number(res?.total || messages.value.length || 0)
    unreadCount.value = Number(res?.unread_count || 0)
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
    booking: `/pages/schedule/detail?id=${msg.related_id || msg.id}`,
    reminder: `/pages/schedule/detail?id=${msg.related_id || msg.id}`,
    feedback: `/pages/review/create?bookingId=${msg.related_id || msg.id}`,
    chat: `/pages/chat/conversation?id=${msg.related_id || msg.id}`,
    system: ''
  }
  const url = routes[msg.type]
  if (url) {
    safeNavigate(url)
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
  background: #f7f9fc;
  padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
}

.message-list {
  padding: 20rpx;
}

.message-item {
  display: flex;
  align-items: flex-start;
  background: #fff;
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  position: relative;
  box-shadow: 0 8rpx 18rpx rgba(30, 41, 59, 0.06);
  border: 1rpx solid rgba(226, 232, 240, 0.9);
  transition: transform 200ms ease, box-shadow 200ms ease;
  cursor: pointer;

  &:active {
    transform: translateY(2rpx);
    box-shadow: 0 6rpx 16rpx rgba(37, 99, 235, 0.16);
  }

  .message-icon {
    width: 72rpx;
    height: 72rpx;
    border-radius: 20rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    flex-shrink: 0;
    border: 1rpx solid rgba(204, 215, 231, 0.8);

    &.booking {
      background: linear-gradient(135deg, #e8f5e9, #f3fbf4);
    }

    &.reminder {
      background: linear-gradient(135deg, #fff3e0, #fff8ed);
    }

    &.feedback {
      background: linear-gradient(135deg, #e3f2fd, #eff7ff);
    }

    &.system {
      background: linear-gradient(135deg, #f3e5f5, #f8eef9);
    }

    &.chat {
      background: linear-gradient(135deg, #e0f7fa, #ebfbfc);
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
