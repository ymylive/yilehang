<template>
  <view class="admin-notices">
    <view class="composer card">
      <view class="row">
        <text class="label">类型</text>
        <picker mode="selector" :range="kindLabels" :value="kindIndex" @change="onKindChange">
          <view class="picker-value">{{ kindLabels[kindIndex] }}</view>
        </picker>
      </view>
      <view class="row block">
        <text class="label">标题</text>
        <input class="input" v-model="title" maxlength="100" placeholder="输入公告或活动标题" />
      </view>
      <view class="row block">
        <text class="label">内容</text>
        <textarea class="textarea" v-model="content" maxlength="2000" placeholder="输入详细内容" />
      </view>
      <button class="btn primary" :loading="publishing" @click="publish">立即发布</button>
    </view>

    <view class="history card">
      <view class="title">最近发布</view>
      <view v-if="items.length" class="list">
        <view class="item" v-for="item in items" :key="item.publish_id">
          <view class="head">
            <text class="kind" :class="item.kind">{{ item.kind === 'activity' ? '活动' : '公告' }}</text>
            <text class="time">{{ item.created_at?.slice(0, 16).replace('T', ' ') }}</text>
          </view>
          <text class="item-title">{{ item.title }}</text>
          <text class="item-content">{{ item.content }}</text>
          <text class="item-meta">触达用户 {{ item.recipient_count || 0 }} 人</text>
        </view>
      </view>
      <view v-else class="empty">
        <image :src="emptyIcon" class="empty-icon" mode="aspectFit" />
        <text>暂无发布记录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { adminPanelApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

type NoticeKind = 'announcement' | 'activity'

interface NoticeItem {
  publish_id: number
  kind: NoticeKind
  title: string
  content: string
  recipient_count: number
  created_at: string
}

const kinds: NoticeKind[] = ['announcement', 'activity']
const kindLabels = ['公告', '活动']
const kindIndex = ref(0)
const title = ref('')
const content = ref('')
const publishing = ref(false)
const items = ref<NoticeItem[]>([])
const emptyIcon = getSemanticIcon('admin-notices-empty')

function onKindChange(e: any) {
  kindIndex.value = Number(e?.detail?.value || 0)
}

async function loadList() {
  try {
    const data: any = await adminPanelApi.listNotices(30)
    items.value = (data?.items || []) as NoticeItem[]
  } catch (error: any) {
    uni.showToast({ title: error?.message || '加载失败', icon: 'none' })
  }
}

async function publish() {
  if (!title.value.trim() || !content.value.trim()) {
    uni.showToast({ title: '请填写标题和内容', icon: 'none' })
    return
  }

  publishing.value = true
  try {
    await adminPanelApi.publishNotice({
      kind: kinds[kindIndex.value] || 'announcement',
      title: title.value.trim(),
      content: content.value.trim()
    })
    uni.showToast({ title: '发布成功', icon: 'success' })
    title.value = ''
    content.value = ''
    await loadList()
  } catch (error: any) {
    uni.showToast({ title: error?.message || '发布失败', icon: 'none' })
  } finally {
    publishing.value = false
  }
}

onShow(() => {
  loadList()
})
</script>

<style scoped>
.admin-notices {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 20rpx;
}

.card {
  border-radius: 18rpx;
  background: #fff;
  padding: 18rpx;
  box-shadow: 0 8rpx 18rpx rgba(31, 37, 51, 0.06);
  margin-bottom: 14rpx;
}

.row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 10rpx;
}

.row.block {
  display: block;
}

.label {
  width: 76rpx;
  font-size: 23rpx;
  color: #667189;
}

.picker-value,
.input,
.textarea {
  border-radius: 12rpx;
  background: #f6f8fc;
  font-size: 24rpx;
}

.picker-value,
.input {
  height: 68rpx;
  line-height: 68rpx;
  padding: 0 14rpx;
}

.textarea {
  width: 100%;
  min-height: 160rpx;
  padding: 12rpx 14rpx;
  box-sizing: border-box;
}

.btn {
  height: 68rpx;
  line-height: 68rpx;
  border-radius: 999rpx;
  border: none;
  font-size: 24rpx;
}

.btn::after {
  border: none;
}

.btn.primary {
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  color: #fff;
}

.title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1f2533;
}

.list {
  margin-top: 10rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.item {
  border-radius: 12rpx;
  background: #f8f9fc;
  padding: 12rpx;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kind {
  border-radius: 999rpx;
  padding: 4rpx 10rpx;
  font-size: 20rpx;
  color: #fff;
}

.kind.announcement {
  background: #3b82f6;
}

.kind.activity {
  background: #ff9120;
}

.time {
  font-size: 20rpx;
  color: #8c97ae;
}

.item-title {
  display: block;
  margin-top: 8rpx;
  font-size: 25rpx;
  font-weight: 700;
  color: #273149;
}

.item-content {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #6d7891;
  line-height: 1.6;
}

.item-meta {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: #8f99ae;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: #90a0ba;
  padding: 24rpx 0;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 8rpx;
}
</style>
