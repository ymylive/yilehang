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

    <!-- 交易列表 -->
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
        <image src="/static/empty.png" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无记录</text>
      </view>

      <!-- 加载更多 -->
      <view v-if="loading" class="loading-more">
        <wd-loading />
        <text>加载中...</text>
      </view>

      <!-- 加载完成 -->
      <view v-if="!loading && filteredTransactions.length > 0 && !hasMore" class="load-end">
        没有更多了
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { membershipApi } from '@/api'

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
    gift: '🎁',
    manual: '✎'
  }
  return map[type] || '•'
}

function getTypeText(type: string): string {
  const map: Record<string, string> = {
    purchase: '购买课时',
    consume: '预约扣费',
    refund: '取消退还',
    gift: '赠送课时',
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

// 监听tab切换时重新加载
watch(currentTab, () => {
  // 由于是前端筛选，不需要重新请求
})

onMounted(() => {
  loadTransactions()
})

// 触底加载更多
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
      color: #4caf50;
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
  background-color: #fff;
  padding: 24rpx;
  border-radius: 12rpx;
  margin-bottom: 16rpx;

  .item-icon {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32rpx;
    font-weight: 600;
    margin-right: 20rpx;

    &.purchase {
      background-color: #e8f5e9;
      color: #4caf50;
    }

    &.consume {
      background-color: #ffebee;
      color: #f44336;
    }

    &.refund {
      background-color: #e3f2fd;
      color: #2196f3;
    }

    &.gift {
      background-color: #fff3e0;
      color: #ff9800;
    }

    &.manual {
      background-color: #f3e5f5;
      color: #9c27b0;
    }

    &.default {
      background-color: #f5f5f5;
      color: #999;
    }
  }

  .item-info {
    flex: 1;

    .item-title {
      font-size: 30rpx;
      color: #333;
      margin-bottom: 8rpx;
    }

    .item-time {
      font-size: 24rpx;
      color: #999;
    }
  }

  .item-change {
    font-size: 36rpx;
    font-weight: 600;
    color: #f44336;

    &.positive {
      color: #4caf50;
    }
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

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;

  text {
    margin-left: 10rpx;
  }
}

.load-end {
  text-align: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
