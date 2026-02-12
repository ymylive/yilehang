<template>
  <view class="admin-analytics">
    <view class="header">
      <text class="title">数据分析</text>
    </view>
    <view class="filter-bar">
      <view class="filter-item" :class="{ active: period === 'week' }" @click="period = 'week'">
        <text>本周</text>
      </view>
      <view class="filter-item" :class="{ active: period === 'month' }" @click="period = 'month'">
        <text>本月</text>
      </view>
      <view class="filter-item" :class="{ active: period === 'year' }" @click="period = 'year'">
        <text>本年</text>
      </view>
    </view>
    <view class="chart-section">
      <view class="section-title">用户增长趋势</view>
      <view class="chart-placeholder">
        <text class="placeholder-text">图表区域</text>
      </view>
    </view>
    <view class="chart-section">
      <view class="section-title">预约统计</view>
      <view class="chart-placeholder">
        <text class="placeholder-text">图表区域</text>
      </view>
    </view>
    <view class="data-table">
      <view class="section-title">详细数据</view>
      <view class="table-header">
        <text class="col">日期</text>
        <text class="col">新增用户</text>
        <text class="col">预约数</text>
        <text class="col">收入</text>
      </view>
      <view class="table-row" v-for="row in tableData" :key="row.date">
        <text class="col">{{ row.date }}</text>
        <text class="col">{{ row.newUsers }}</text>
        <text class="col">{{ row.bookings }}</text>
        <text class="col">{{ row.revenue }}</text>
      </view>
    </view>
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, onMounted } from 'vue'

const period = ref('week')
const tableData = ref([
  { date: '02-07', newUsers: 15, bookings: 32, revenue: '¥2,580' },
  { date: '02-06', newUsers: 12, bookings: 28, revenue: '¥2,240' },
  { date: '02-05', newUsers: 18, bookings: 35, revenue: '¥2,800' },
  { date: '02-04', newUsers: 10, bookings: 25, revenue: '¥2,000' },
  { date: '02-03', newUsers: 14, bookings: 30, revenue: '¥2,400' },
])

onMounted(() => {
  console.log('Analytics page loaded')
})
</script>

<style lang="scss" scoped>
.admin-analytics {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20rpx;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
}

.header {
  padding: 30rpx;
  .title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
  }
}

.filter-bar {
  display: flex;
  background: #fff;
  border-radius: 16rpx;
  padding: 10rpx;
  margin-bottom: 20rpx;

  .filter-item {
    flex: 1;
    text-align: center;
    padding: 16rpx 0;
    border-radius: 12rpx;
    font-size: 28rpx;
    color: #666;

    &.active {
      background: #ff8800;
      color: #fff;
    }
  }
}

.chart-section {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;

  .section-title {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 20rpx;
  }

  .chart-placeholder {
    height: 300rpx;
    background: #f9f9f9;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;

    .placeholder-text {
      color: #999;
      font-size: 28rpx;
    }
  }
}

.data-table {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;

  .section-title {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 20rpx;
  }

  .table-header {
    display: flex;
    padding: 16rpx 0;
    border-bottom: 2rpx solid #f0f0f0;

    .col {
      flex: 1;
      text-align: center;
      font-size: 24rpx;
      color: #999;
      font-weight: bold;
    }
  }

  .table-row {
    display: flex;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .col {
      flex: 1;
      text-align: center;
      font-size: 26rpx;
      color: #333;
    }
  }
}
</style>
