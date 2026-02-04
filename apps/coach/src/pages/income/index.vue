<template>
  <view class="income-page">
    <!-- 收入概览 -->
    <view class="overview-card">
      <view class="overview-header">
        <text class="overview-title">本月收入</text>
        <text class="overview-month">{{ currentMonth }}月</text>
      </view>
      <view class="overview-amount">
        <text class="currency">¥</text>
        <text class="amount">{{ summary.this_month?.income?.toFixed(2) || '0.00' }}</text>
      </view>
      <view class="overview-stats">
        <view class="stat-item">
          <text class="stat-value">{{ summary.this_month?.lessons || 0 }}</text>
          <text class="stat-label">课时数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">¥{{ summary.hourly_rate || 0 }}</text>
          <text class="stat-label">课时费</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ ((summary.commission_rate || 0) * 100).toFixed(0) }}%</text>
          <text class="stat-label">提成比例</text>
        </view>
      </view>
    </view>

    <!-- 月份对比 -->
    <view class="compare-card">
      <view class="compare-item">
        <view class="compare-label">上月收入</view>
        <view class="compare-value">¥{{ summary.last_month?.income?.toFixed(2) || '0.00' }}</view>
        <view class="compare-lessons">{{ summary.last_month?.lessons || 0 }}课时</view>
      </view>
      <view class="compare-divider"></view>
      <view class="compare-item">
        <view class="compare-label">累计收入</view>
        <view class="compare-value total">¥{{ summary.total?.income?.toFixed(2) || '0.00' }}</view>
        <view class="compare-lessons">{{ summary.total?.lessons || 0 }}课时</view>
      </view>
    </view>

    <!-- 收入明细 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">收入明细</text>
        <picker mode="date" fields="month" :value="selectedMonth" @change="onMonthChange">
          <view class="month-picker">
            {{ selectedMonth }} <text class="arrow">▼</text>
          </view>
        </picker>
      </view>

      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>

      <view v-else class="income-list">
        <view v-for="item in incomeList" :key="item.id" class="income-item">
          <view class="item-info">
            <view class="item-title">{{ item.student_name }}</view>
            <view class="item-time">{{ item.booking_date }} {{ item.start_time }}-{{ item.end_time }}</view>
          </view>
          <view class="item-amount">+¥{{ item.income.toFixed(2) }}</view>
        </view>

        <view v-if="incomeList.length === 0" class="empty-state">
          <text>暂无收入记录</text>
        </view>
      </view>

      <view v-if="incomeList.length > 0 && hasMore" class="load-more" @click="loadMore">
        <text>加载更多</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { coachApi } from '@/api/index'

interface IncomeSummary {
  this_month: { lessons: number; income: number }
  last_month: { lessons: number; income: number }
  total: { lessons: number; income: number }
  hourly_rate: number
  commission_rate: number
}

interface IncomeItem {
  id: number
  booking_date: string
  start_time: string
  end_time: string
  student_name: string
  hourly_rate: number
  commission_rate: number
  income: number
  completed_at: string | null
}

const currentMonth = ref(new Date().getMonth() + 1)
const selectedMonth = ref(formatMonth(new Date()))
const summary = ref<Partial<IncomeSummary>>({})
const incomeList = ref<IncomeItem[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

function formatMonth(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

async function loadSummary() {
  try {
    const data = await coachApi.getIncomeSummary()
    summary.value = data
  } catch (error: any) {
    console.error('获取收入汇总失败:', error)
  }
}

async function loadIncomeDetails(reset = false) {
  if (reset) {
    page.value = 1
    incomeList.value = []
    hasMore.value = true
  }

  if (!hasMore.value) return

  loading.value = true
  try {
    const data = await coachApi.getIncomeDetails({
      month: selectedMonth.value,
      page: page.value,
      page_size: 20
    })

    const items = data.items || []
    if (items.length < 20) {
      hasMore.value = false
    }

    if (reset) {
      incomeList.value = items
    } else {
      incomeList.value.push(...items)
    }
  } catch (error: any) {
    console.error('获取收入明细失败:', error)
  } finally {
    loading.value = false
  }
}

function loadMore() {
  page.value++
  loadIncomeDetails()
}

function onMonthChange(e: any) {
  selectedMonth.value = e.detail.value
  loadIncomeDetails(true)
}

watch(selectedMonth, () => {
  loadIncomeDetails(true)
})

onMounted(() => {
  loadSummary()
  loadIncomeDetails(true)
})
</script>

<style lang="scss" scoped>
.income-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 40rpx;
}

.overview-card {
  background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
  padding: 40rpx;
  color: #fff;

  .overview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;

    .overview-title {
      font-size: 28rpx;
      opacity: 0.9;
    }

    .overview-month {
      font-size: 26rpx;
      opacity: 0.8;
    }
  }

  .overview-amount {
    margin-bottom: 30rpx;

    .currency {
      font-size: 36rpx;
    }

    .amount {
      font-size: 72rpx;
      font-weight: 600;
    }
  }

  .overview-stats {
    display: flex;
    gap: 60rpx;

    .stat-item {
      .stat-value {
        font-size: 36rpx;
        font-weight: 600;
      }

      .stat-label {
        font-size: 24rpx;
        opacity: 0.8;
        margin-top: 4rpx;
        display: block;
      }
    }
  }
}

.compare-card {
  display: flex;
  background-color: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;

  .compare-item {
    flex: 1;
    text-align: center;

    .compare-label {
      font-size: 26rpx;
      color: #999;
    }

    .compare-value {
      font-size: 36rpx;
      font-weight: 600;
      color: #333;
      margin: 12rpx 0 8rpx;

      &.total {
        color: #2196F3;
      }
    }

    .compare-lessons {
      font-size: 24rpx;
      color: #999;
    }
  }

  .compare-divider {
    width: 1rpx;
    background-color: #f0f0f0;
    margin: 0 20rpx;
  }
}

.section {
  background-color: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;

    .section-title {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
    }

    .month-picker {
      font-size: 28rpx;
      color: #666;
      padding: 8rpx 20rpx;
      background-color: #f5f5f5;
      border-radius: 20rpx;

      .arrow {
        font-size: 20rpx;
        margin-left: 8rpx;
      }
    }
  }
}

.loading-state {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 28rpx;
}

.income-list {
  .income-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .item-info {
      .item-title {
        font-size: 28rpx;
        color: #333;
      }

      .item-time {
        font-size: 24rpx;
        color: #999;
        margin-top: 8rpx;
      }
    }

    .item-amount {
      font-size: 32rpx;
      font-weight: 600;
      color: #4caf50;
    }
  }

  .empty-state {
    text-align: center;
    padding: 40rpx;
    color: #999;
    font-size: 28rpx;
  }
}

.load-more {
  text-align: center;
  padding: 20rpx;
  color: #2196F3;
  font-size: 28rpx;
}
</style>
