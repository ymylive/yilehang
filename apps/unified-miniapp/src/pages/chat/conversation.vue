<template>
  <view class="page">
    <!-- 娑堟伅鍒楄〃 -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-top="scrollTop"
      :scroll-into-view="scrollIntoView"
      @scrolltoupper="loadMoreMessages"
    >
      <view v-if="hasMore" class="load-more" @click="loadMoreMessages">
        <text>{{ loadingMore ? '鍔犺浇涓?..' : '鍔犺浇鏇村' }}</text>
      </view>

      <view
        v-for="(msg, index) in messages"
        :key="msg.id"
        :id="`msg-${msg.id}`"
        class="message-item"
        :class="{ 'is-self': msg.sender_id === currentUserId }"
      >
        <!-- 鏃堕棿鍒嗛殧 -->
        <view v-if="shouldShowTime(msg, index)" class="time-divider">
          <text>{{ formatMessageTime(msg.created_at) }}</text>
        </view>

        <view class="message-row">
          <!-- 瀵规柟澶村儚 -->
          <image
            v-if="msg.sender_id !== currentUserId"
            class="avatar"
            :src="msg.sender?.avatar || '/static/default-avatar.png'"
            mode="aspectFill"
          />

          <!-- 娑堟伅鍐呭 -->
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

          <!-- 鑷繁澶村儚 -->
          <image
            v-if="msg.sender_id === currentUserId"
            class="avatar"
            :src="msg.sender?.avatar || '/static/default-avatar.png'"
            mode="aspectFill"
          />
        </view>
      </view>
    </scroll-view>

    <!-- 杈撳叆鍖哄煙 -->
    <view class="input-area">
      <view class="input-row">
        <view class="more-btn" @click="showMoreOptions = !showMoreOptions">
          <text>+</text>
        </view>
        <input
          class="input"
          type="text"
          v-model="inputText"
          placeholder="杈撳叆娑堟伅..."
          confirm-type="send"
          @confirm="sendTextMessage"
        />
        <view class="send-btn" :class="{ active: inputText.trim() }" @click="sendTextMessage">
          <text>发送</text>
        </view>
      </view>

      <!-- 鏇村閫夐」 -->
      <view class="more-options" v-if="showMoreOptions">
        <view class="option-item" @click="chooseImage">
          <view class="option-icon">
            <wd-icon name="camera" size="44rpx" color="#2563eb" />
          </view>
          <text class="option-text">鍥剧墖</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { CHAT_WS_URL, chatApi, uploadApi } from '@/api'

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

// WebSocket 杩炴帴
let ws: UniApp.SocketTask | null = null
let heartbeatTimer: ReturnType<typeof setInterval> | null = null
let manualSocketClose = false
let hasRetriedWithTicket = false

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).options || {}

  conversationId.value = parseInt(options.id) || 0
  conversationName.value = decodeURIComponent(options.name || '鑱婂ぉ')

  // Set page title for current conversation.
  uni.setNavigationBarTitle({ title: conversationName.value })

  if (conversationId.value) {
    await loadMessages()
    connectWebSocket()
  }
})

onUnmounted(() => {
  disconnectWebSocket()
})

function clearHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

function startHeartbeat(socketTask: UniApp.SocketTask) {
  clearHeartbeat()
  heartbeatTimer = setInterval(() => {
    try {
      socketTask.send({ data: 'ping' })
    } catch (_) {
      // ignore heartbeat errors from closed sockets
    }
  }, 30000)
}

async function loadMessages(loadMore = false) {
  if (loading.value || loadingMore.value) return

  if (loadMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }

  try {
    const skip = loadMore ? messages.value.length : 0
    const res: any = await chatApi.getMessages(conversationId.value, { skip, limit: 50 })

    const items = Array.isArray(res?.items) ? res.items : (Array.isArray(res) ? res : [])
    // Backend may return newest-first; normalize to oldest-first for rendering.
    items.reverse()

    if (loadMore) {
      messages.value = [...items, ...messages.value]
    } else {
      messages.value = items
      // Wait for DOM update before moving scroll anchor.
      await nextTick()
      scrollToBottom()
    }

    hasMore.value = Boolean(res?.has_more)
  } catch (error) {
    console.error('鍔犺浇娑堟伅澶辫触', error)
    uni.showToast({ title: '鍔犺浇澶辫触', icon: 'none' })
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
      uni.showLoading({ title: '鍙戦€佷腑...' })
      try {
        const uploadRes = await uploadApi.image(tempFilePath) as any
        await sendMessage('image', uploadRes.url)
      } catch (error) {
        console.error('涓婁紶鍥剧墖澶辫触', error)
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

  // 瓒呰繃5鍒嗛挓鏄剧ず鏃堕棿
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
    return `鏄ㄥぉ ${timeStr}`
  }

  return `${date.getMonth() + 1}/${date.getDate()} ${timeStr}`
}

async function buildTicketWsUrl(): Promise<string | null> {
  try {
    const res: any = await chatApi.getWsTicket()
    const ticket = res?.ticket
    if (!ticket) return null
    return `${CHAT_WS_URL}?ticket=${encodeURIComponent(ticket)}`
  } catch (error) {
    console.error('Get websocket ticket failed', error)
    return null
  }
}

function connectWebSocket() {
  const token = uni.getStorageSync('token')
  if (!token) return

  disconnectWebSocket()
  manualSocketClose = false
  hasRetriedWithTicket = false

  const createSocket = (url: string, header?: Record<string, string>, allowTicketFallback = false) => {
    const socketTask = uni.connectSocket({
      url,
      ...(header ? { header } : {}),
      success: () => {
        console.log('WebSocket connection created')
      }
    })
    ws = socketTask

    const tryTicketFallback = async () => {
      if (!manualSocketClose && allowTicketFallback && !hasRetriedWithTicket) {
        hasRetriedWithTicket = true
        const ticketUrl = await buildTicketWsUrl()
        if (ticketUrl) {
          createSocket(ticketUrl)
        }
      }
    }

    socketTask.onOpen(() => {
      startHeartbeat(socketTask)
    })

    socketTask.onMessage((res) => {
      try {
        const data = JSON.parse(res.data as string)
        if (data.type === 'new_message' && data.data.conversation_id === conversationId.value) {
          messages.value.push(data.data)
          nextTick(() => scrollToBottom())
        }
      } catch (_) {
        // ignore non-JSON ws payloads (e.g. pong)
      }
    })

    socketTask.onError((err) => {
      console.error('WebSocket error', err)
      void tryTicketFallback()
    })

    socketTask.onClose(() => {
      if (ws === socketTask) {
        ws = null
        clearHeartbeat()
      }
      console.log('WebSocket closed')
      void tryTicketFallback()
    })
  }

  // #ifdef H5
  void (async () => {
    const ticketUrl = await buildTicketWsUrl()
    if (!ticketUrl) return
    createSocket(ticketUrl)
  })()
  // #endif

  // #ifndef H5
  createSocket(CHAT_WS_URL, { Authorization: `Bearer ${token}` }, true)
  // #endif
}

function disconnectWebSocket() {
  manualSocketClose = true
  clearHeartbeat()
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
  animation: fadeInUp 220ms ease-out;
}

.option-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  min-width: 120rpx;
  cursor: pointer;
  transition: transform 200ms ease;
}

.option-item:active {
  transform: translateY(2rpx);
}

.option-icon {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #eef4ff, #f5f8ff);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1rpx rgba(189, 208, 244, 0.65);
}

.option-text {
  font-size: 24rpx;
  color: #475569;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(8rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

