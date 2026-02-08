<template>
  <view class="page">
    <!-- 消息列表 -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-top="scrollTop"
      :scroll-into-view="scrollIntoView"
      @scrolltoupper="loadMoreMessages"
    >
      <view v-if="hasMore" class="load-more" @click="loadMoreMessages">
        <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
      </view>

      <view
        v-for="(msg, index) in messages"
        :key="msg.id"
        :id="`msg-${msg.id}`"
        class="message-item"
        :class="{ 'is-self': msg.sender_id === currentUserId }"
      >
        <!-- 时间分隔 -->
        <view v-if="shouldShowTime(msg, index)" class="time-divider">
          <text>{{ formatMessageTime(msg.created_at) }}</text>
        </view>

        <view class="message-row">
          <!-- 对方头像 -->
          <image
            v-if="msg.sender_id !== currentUserId"
            class="avatar"
            :src="msg.sender?.avatar || '/static/default-avatar.png'"
            mode="aspectFill"
          />

          <!-- 消息内容 -->
          <view class="message-content">
            <view class="bubble" :class="msg.type">
              <text v-if="msg.type === 'text'">{{ msg.content }}</text>
              <image
                v-else-if="msg.type === 'image'"
                class="msg-image"
                :src="msg.content"
                mode="widthFix"
                @click="previewImage(msg.content)"
              />
            </view>
          </view>

          <!-- 自己头像 -->
          <image
            v-if="msg.sender_id === currentUserId"
            class="avatar"
            :src="msg.sender?.avatar || '/static/default-avatar.png'"
            mode="aspectFill"
          />
        </view>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view class="input-area">
      <view class="input-row">
        <view class="more-btn" @click="showMoreOptions = !showMoreOptions">
          <text>+</text>
        </view>
        <input
          class="input"
          type="text"
          v-model="inputText"
          placeholder="输入消息..."
          confirm-type="send"
          @confirm="sendTextMessage"
        />
        <view class="send-btn" :class="{ active: inputText.trim() }" @click="sendTextMessage">
          <text>发送</text>
        </view>
      </view>

      <!-- 更多选项 -->
      <view class="more-options" v-if="showMoreOptions">
        <view class="option-item" @click="chooseImage">
          <view class="option-icon">📷</view>
          <text class="option-text">图片</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { chatApi, uploadApi } from '@/api'

interface UserBrief {
  id: number
  nickname?: string
  avatar?: string
  role: string
}

interface Message {
  id: number
  conversation_id: number
  sender_id: number
  sender?: UserBrief
  type: string
  content: string
  status: string
  is_deleted: boolean
  created_at: string
}

const userStore = useUserStore()

const conversationId = ref(0)
const conversationName = ref('')
const messages = ref<Message[]>([])
const inputText = ref('')
const showMoreOptions = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const scrollTop = ref(0)
const scrollIntoView = ref('')

const currentUserId = computed(() => userStore.user?.id || 0)

// WebSocket 连接
let ws: UniApp.SocketTask | null = null

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).options || {}

  conversationId.value = parseInt(options.id) || 0
  conversationName.value = decodeURIComponent(options.name || '聊天')

  // 设置导航栏标题
  uni.setNavigationBarTitle({ title: conversationName.value })

  if (conversationId.value) {
    await loadMessages()
    connectWebSocket()
  }
})

onUnmounted(() => {
  disconnectWebSocket()
})

async function loadMessages(loadMore = false) {
  if (loading.value || loadingMore.value) return

  if (loadMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }

  try {
    const skip = loadMore ? messages.value.length : 0
    const res = await chatApi.getMessages(conversationId.value, { skip, limit: 50 })

    const items = res.items || []
    // 消息按时间倒序返回，需要反转
    items.reverse()

    if (loadMore) {
      messages.value = [...items, ...messages.value]
    } else {
      messages.value = items
      // 滚动到底部
      await nextTick()
      scrollToBottom()
    }

    hasMore.value = res.has_more
  } catch (error) {
    console.error('加载消息失败', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMoreMessages() {
  if (hasMore.value && !loadingMore.value) {
    loadMessages(true)
  }
}

async function sendTextMessage() {
  const text = inputText.value.trim()
  if (!text) return

  inputText.value = ''
  await sendMessage('text', text)
}

async function sendMessage(type: string, content: string) {
  try {
    const res = await chatApi.sendMessage(conversationId.value, { type, content })
    messages.value.push(res)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败', error)
    uni.showToast({ title: '发送失败', icon: 'none' })
  }
}

function chooseImage() {
  showMoreOptions.value = false
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0]
      uni.showLoading({ title: '发送中...' })
      try {
        const uploadRes = await uploadApi.image(tempFilePath) as any
        await sendMessage('image', uploadRes.url)
      } catch (error) {
        console.error('上传图片失败', error)
        uni.showToast({ title: '发送失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    }
  })
}

function previewImage(url: string) {
  uni.previewImage({
    urls: [url],
    current: url
  })
}

function scrollToBottom() {
  if (messages.value.length > 0) {
    const lastMsg = messages.value[messages.value.length - 1]
    scrollIntoView.value = `msg-${lastMsg.id}`
  }
}

function shouldShowTime(msg: Message, index: number): boolean {
  if (index === 0) return true

  const prevMsg = messages.value[index - 1]
  const prevTime = new Date(prevMsg.created_at).getTime()
  const currTime = new Date(msg.created_at).getTime()

  // 超过5分钟显示时间
  return currTime - prevTime > 5 * 60 * 1000
}

function formatMessageTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 86400000)

  const timeStr = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`

  if (date >= today) {
    return timeStr
  }
  if (date >= yesterday) {
    return `昨天 ${timeStr}`
  }

  return `${date.getMonth() + 1}/${date.getDate()} ${timeStr}`
}

function connectWebSocket() {
  const token = uni.getStorageSync('token')
  if (!token) return

  const envBase = (import.meta.env.VITE_API_BASE_URL || '').trim()
  const isMpWeixin = typeof wx !== 'undefined' && typeof (globalThis as any).__wxConfig !== 'undefined'
  const wsBase = envBase
    ? envBase.replace(/^http/, 'ws')
    : (isMpWeixin ? 'wss://yilehang.cornna.xyz/api/v1' : 'ws://localhost:8000/api/v1')

  ws = uni.connectSocket({
    url: `${wsBase}/chat/ws?token=${token}`,
    success: () => {
      console.log('WebSocket 连接成功')
    }
  })

  ws.onMessage((res) => {
    try {
      const data = JSON.parse(res.data as string)
      if (data.type === 'new_message' && data.data.conversation_id === conversationId.value) {
        messages.value.push(data.data)
        nextTick(() => scrollToBottom())
      }
    } catch (e) {
      // 忽略非 JSON 消息（如 pong）
    }
  })

  ws.onError((err) => {
    console.error('WebSocket 错误', err)
  })

  ws.onClose(() => {
    console.log('WebSocket 关闭')
  })

  // 心跳
  const heartbeat = setInterval(() => {
    if (ws) {
      ws.send({ data: 'ping' })
    }
  }, 30000)

  onUnmounted(() => {
    clearInterval(heartbeat)
  })
}

function disconnectWebSocket() {
  if (ws) {
    ws.close({})
    ws = null
  }
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.message-list {
  flex: 1;
  padding: 20rpx;
  overflow-y: auto;
}

.load-more {
  text-align: center;
  padding: 20rpx 0;
  color: #999;
  font-size: 24rpx;
}

.message-item {
  margin-bottom: 20rpx;
}

.time-divider {
  text-align: center;
  padding: 20rpx 0;
}

.time-divider text {
  font-size: 22rpx;
  color: #999;
  background: #e8e8e8;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}

.message-row {
  display: flex;
  align-items: flex-start;
}

.message-item.is-self .message-row {
  flex-direction: row-reverse;
}

.avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  margin: 0 16rpx;
}

.bubble {
  padding: 20rpx 24rpx;
  border-radius: 16rpx;
  background: #fff;
  word-break: break-all;
}

.message-item.is-self .bubble {
  background: #FF8800;
  color: #fff;
}

.bubble.image {
  padding: 8rpx;
  background: transparent;
}

.msg-image {
  max-width: 400rpx;
  border-radius: 12rpx;
}

.bubble text {
  font-size: 28rpx;
  line-height: 1.6;
}

.input-area {
  background: #fff;
  padding: 16rpx 20rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #f0f0f0;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.more-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  color: #666;
}

.input {
  flex: 1;
  height: 72rpx;
  padding: 0 24rpx;
  background: #f5f5f5;
  border-radius: 36rpx;
  font-size: 28rpx;
}

.send-btn {
  padding: 16rpx 32rpx;
  background: #e0e0e0;
  border-radius: 36rpx;
  font-size: 28rpx;
  color: #999;
}

.send-btn.active {
  background: #FF8800;
  color: #fff;
}

.more-options {
  display: flex;
  padding: 30rpx 0;
  gap: 40rpx;
}

.option-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.option-icon {
  width: 100rpx;
  height: 100rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}

.option-text {
  font-size: 24rpx;
  color: #666;
}
</style>
