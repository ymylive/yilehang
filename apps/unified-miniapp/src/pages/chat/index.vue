<template>
  <PageErrorBoundary page="chat.index" @retry="retryLoad">
  <view class="page">
    <!-- 会话列表 -->
    <view class="conversation-list">
      <view
        v-for="conv in conversations"
        :key="conv.id"
        class="conversation-item"
        @click="openConversation(conv)"
      >
        <image
          class="avatar"
          :src="conv.other_user?.avatar || '/static/default-avatar.png'"
          mode="aspectFill"
        />
        <view class="content">
          <view class="header">
            <text class="name">{{ conv.other_user?.nickname || '用户' }}</text>
            <text class="time">{{ formatTime(conv.last_message_at) }}</text>
          </view>
          <view class="message">
            <text class="preview">{{ getMessagePreview(conv.last_message) }}</text>
            <view class="badge" v-if="conv.unread_count > 0">
              {{ conv.unread_count > 99 ? '99+' : conv.unread_count }}
            </view>
          </view>
        </view>
      </view>

      <view v-if="conversations.length === 0 && !loading" class="empty-state">
        <image src="/static/empty.svg" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无消息</text>
        <text class="empty-hint">与教练或家长开始聊天吧</text>
      </view>

      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>
    </view>
  <DynamicTabBar />
</view>
  </PageErrorBoundary>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import PageErrorBoundary from '@/components/PageErrorBoundary.vue'
import { ref } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'
import { chatApi } from '@/api'
import { safeNavigate } from '@/utils/safe-nav'

interface UserBrief {
  id: number
  nickname?: string
  avatar?: string
  role: string
}

interface Message {
  id: number
  type: string
  content: string
  created_at: string
}

interface Conversation {
  id: number
  type: string
  other_user?: UserBrief
  last_message?: Message
  last_message_at?: string
  unread_count: number
}

const conversations = ref<Conversation[]>([])
const loading = ref(false)

async function loadConversations() {
  loading.value = true
  try {
    const res: any = await chatApi.getConversations()
    conversations.value = Array.isArray(res?.items) ? res.items : (Array.isArray(res) ? res : [])
  } catch (error) {
    console.error('加载会话列表失败', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function formatTime(dateStr?: string): string {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`

  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 86400000)

  if (date >= today) {
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  if (date >= yesterday) {
    return '昨天'
  }

  return `${date.getMonth() + 1}/${date.getDate()}`
}

function getMessagePreview(message?: Message): string {
  if (!message) return '暂无消息'

  switch (message.type) {
    case 'image':
      return '[图片]'
    case 'voice':
      return '[语音]'
    case 'file':
      return '[文件]'
    default:
      return message.content.length > 30
        ? message.content.substring(0, 30) + '...'
        : message.content
  }
}

function openConversation(conv: Conversation) {
  safeNavigate(`/pages/chat/conversation?id=${conv.id}&name=${encodeURIComponent(conv.other_user?.nickname || '聊天')}`)
}

function retryLoad() {
  loadConversations()
}

// 下拉刷新
onPullDownRefresh(async () => {
  await loadConversations()
  uni.stopPullDownRefresh()
})

// 页面显示时刷新
onShow(() => {
  if (!loading.value) {
    loadConversations()
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
}

.conversation-list {
  background: #fff;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.conversation-item:active {
  background: #f5f5f5;
}

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.content {
  flex: 1;
  margin-left: 24rpx;
  overflow: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.name {
  font-size: 30rpx;
  color: #333;
  font-weight: 500;
}

.time {
  font-size: 24rpx;
  color: #999;
}

.message {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview {
  flex: 1;
  font-size: 26rpx;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge {
  min-width: 36rpx;
  height: 36rpx;
  line-height: 36rpx;
  padding: 0 10rpx;
  background: #FF3B30;
  color: #fff;
  font-size: 22rpx;
  border-radius: 18rpx;
  text-align: center;
  margin-left: 16rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.empty-image {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 30rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: #999;
}

.loading-state {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
}
</style>
