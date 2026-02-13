<template>
  <view class="transactions-page">
    <!-- 筛选标签 -->
    <view class="filter-tabs">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        :class="['tab-item', { active: currentTab === tab.value }]"
        @click="currentTab = tab.value"
      >
        {{ tab.label }}
      </view>
    </view>

    <!-- 记录列表 -->
    <view class="transaction-list">
      <view
        v-for="item in filteredTransactions"
        :key="item.id"
        class="transaction-item"
      >
        <view class="item-icon" :class="getTypeClass(item.type)">
          <text>{{ getTypeIcon(item.type) }}</text>
        </view>
        <view class="item-info">
          <view class="item-title">{{ item.description || getTypeText(item.type) }}</view>
          <view class="item-time">{{ formatDateTime(item.created_at) }}</view>
        </view>
        <view class="item-change" :class="{ positive: item.times_change > 0 }">
          {{ item.times_change > 0 ? '+' : '' }}{{ item.times_change }}次
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="filteredTransactions.length === 0 && !loading" class="empty-state">
        <image :src="emptyIcon" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无记录</text>
      </view>

      <!-- 加载中 -->
      <view v-if="loading" class="loading-more">
        <wd-loading />
        <text>加载中...</text>
      </view>

      <!-- 无更多 -->
      <view v-if="!loading && filteredTransactions.length > 0 && !hasMore" class="load-end">
        没有更多记录了
      </view>
    </view>
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { onReachBottom } from '@dcloudio/uni-app'
import { membershipApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

interface Transaction {
  id: number
  student_id: number
  type: string
  amount: number | null
  times_change: number
  membership_id: number | null
  booking_id: number | null
  description: string | null
  created_at: string
}

const tabs = [
  { label: '全部', value: '' },
  { label: '消费', value: 'consume' },
  { label: '充值', value: 'purchase' },
  { label: '退款', value: 'refund' }
]

const currentTab = ref('')
const transactions = ref<Transaction[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const hasMore = ref(true)
const emptyIcon = getSemanticIcon('membership-transactions-empty')

const filteredTransactions = computed(() => {
  if (!currentTab.value) return transactions.value
  return transactions.value.filter(t => t.type === currentTab.value)
})

function getTypeClass(type: string): string {
  const map: Record<string, string> = {
    purchase: 'purchase',
    consume: 'consume',
    refund: 'refund',
    gift: 'gift',
    manual: 'manual'
  }
  return map[type] || 'default'
}

function getTypeIcon(type: string): string {
  const map: Record<string, string> = {
    purchase: '+',
    consume: '-',
    refund: '↩',
    gift: '赠',
    manual: '调'
  }
  return map[type] || '•'
}

function getTypeText(type: string): string {
  const map: Record<string, string> = {
    purchase: '充值',
    consume: '扣课',
    refund: '退款',
    gift: '赠送',
    manual: '手动调整'
  }
  return map[type] || '其他'
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

async function loadTransactions(refresh = false) {
  if (loading.value) return
  if (refresh) {
    page.value = 1
    hasMore.value = true
  }

  loading.value = true
  try {
    const data = await membershipApi.getTransactions(page.value, pageSize)

    if (refresh) {
      transactions.value = data
    } else {
      transactions.value = [...transactions.value, ...data]
    }

    hasMore.value = data.length === pageSize
    page.value++
  } catch (error: any) {
    uni.showToast({ title: error.message || '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

watch(currentTab, () => {
  loadTransactions(true)
})

onMounted(() => {
  loadTransactions()
})

onReachBottom(() => {
  if (hasMore.value && !loading.value) {
    loadTransactions()
  }
})
</script>

<style lang="scss" scoped>
.transactions-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
}

.filter-tabs {
  display: flex;
  background-color: #fff;
  padding: 20rpx;
  position: sticky;
  top: 0;
  z-index: 10;

  .tab-item {
    flex: 1;
    text-align: center;
    padding: 16rpx 0;
    font-size: 28rpx;
    color: #666;
    border-radius: 8rpx;

    &.active {
      background-color: #e8f5e9;
      color: #FF8800;
      font-weight: 600;
    }
  }
}

.transaction-list {
  padding: 20rpx;
}

.transaction-item {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}

.item-icon {
  width: 60rpx;
  height: 60rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  margin-right: 16rpx;
}

.item-info {
  flex: 1;
}

.item-title {
  font-size: 28rpx;
  color: #333;
}

.item-time {
  font-size: 22rpx;
  color: #999;
  margin-top: 6rpx;
}

.item-change {
  font-size: 28rpx;
  color: #666;
}

.item-change.positive {
  color: #FF8800;
}

.empty-state {
  text-align: center;
  padding: 80rpx 0;

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

.loading-more,
.load-end {
  text-align: center;
  color: #999;
  padding: 20rpx 0;
}
</style>
