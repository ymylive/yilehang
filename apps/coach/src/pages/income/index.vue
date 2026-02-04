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
        <text class="amount">{{ monthIncome.toFixed(2) }}</text>
      </view>
      <view class="overview-stats">
        <view class="stat-item">
          <text class="stat-value">{{ monthLessons }}</text>
          <text class="stat-label">课时数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ monthStudents }}</text>
          <text class="stat-label">学员数</text>
        </view>
      </view>
    </view>

    <!-- 收入明细 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">收入明细</text>
        <view class="filter-tabs">
          <text
            :class="['tab', { active: currentTab === 'week' }]"
            @click="currentTab = 'week'"
          >本周</text>
          <text
            :class="['tab', { active: currentTab === 'month' }]"
            @click="currentTab = 'month'"
          >本月</text>
        </view>
      </view>

      <view class="income-list">
        <view v-for="item in incomeList" :key="item.id" class="income-item">
          <view class="item-info">
            <view class="item-title">{{ item.student_name }} - {{ item.course_type === 'private' ? '私教课' : '小班课' }}</view>
            <view class="item-time">{{ formatDateTime(item.created_at) }}</view>
          </view>
          <view class="item-amount">+¥{{ item.amount.toFixed(2) }}</view>
        </view>

        <view v-if="incomeList.length === 0" class="empty-state">
          <text>暂无收入记录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface IncomeItem {
  id: number
  student_name: string
  course_type: string
  amount: number
  created_at: string
}

const currentMonth = ref(new Date().getMonth() + 1)
const monthIncome = ref(0)
const monthLessons = ref(0)
const monthStudents = ref(0)
const currentTab = ref('month')
const incomeList = ref<IncomeItem[]>([])

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}-${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  // 模拟数据
  monthIncome.value = 8500
  monthLessons.value = 42
  monthStudents.value = 15

  incomeList.value = [
    { id: 1, student_name: '小明', course_type: 'private', amount: 200, created_at: new Date().toISOString() },
    { id: 2, student_name: '小红', course_type: 'private', amount: 200, created_at: new Date(Date.now() - 86400000).toISOString() },
    { id: 3, student_name: '小刚', course_type: 'private', amount: 200, created_at: new Date(Date.now() - 172800000).toISOString() },
    { id: 4, student_name: '小美', course_type: 'group', amount: 150, created_at: new Date(Date.now() - 259200000).toISOString() }
  ]
})
</script>

<style lang="scss" scoped>
.income-page {
  min-height: 100vh;
  background-color: #f5f5f5;
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

    .filter-tabs {
      display: flex;
      gap: 20rpx;

      .tab {
        font-size: 26rpx;
        color: #999;
        padding: 8rpx 20rpx;
        border-radius: 20rpx;

        &.active {
          background-color: #e3f2fd;
          color: #2196F3;
        }
      }
    }
  }
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
</style>
