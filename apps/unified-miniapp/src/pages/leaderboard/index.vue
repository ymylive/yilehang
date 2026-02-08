<template>
  <view class="page">
    <!-- 标签切换 -->
    <view class="tabs">
      <view
        :class="['tab', { active: currentTab === 'energy' }]"
        @click="currentTab = 'energy'"
      >
        <text class="tab-icon">⚡</text>
        <text class="tab-text">能量榜</text>
      </view>
      <view
        :class="['tab', { active: currentTab === 'training' }]"
        @click="currentTab = 'training'"
      >
        <text class="tab-icon">🏃</text>
        <text class="tab-text">训练榜</text>
      </view>
    </view>

    <!-- 时间筛选 -->
    <view class="period-filter">
      <view
        :class="['period-item', { active: period === 'week' }]"
        @click="period = 'week'"
      >本周</view>
      <view
        :class="['period-item', { active: period === 'month' }]"
        @click="period = 'month'"
      >本月</view>
      <view
        :class="['period-item', { active: period === 'all' }]"
        @click="period = 'all'"
      >总榜</view>
    </view>

    <!-- 我的排名 -->
    <view class="my-rank" v-if="myRank">
      <view class="my-rank-card">
        <view class="my-avatar">
          <text class="avatar-text">我</text>
        </view>
        <view class="my-info">
          <text class="my-name">我的排名</text>
          <text class="my-value">{{ myValue }} {{ currentTab === 'energy' ? '能量' : '次' }}</text>
        </view>
        <view class="my-rank-num">
          <text class="rank-label">第</text>
          <text class="rank-value">{{ myRank }}</text>
          <text class="rank-label">名</text>
        </view>
      </view>
    </view>

    <!-- 排行榜列表 -->
    <view class="leaderboard">
      <!-- 前三名 -->
      <view class="top-three" v-if="leaderboard.length >= 3">
        <view class="top-item second" @click="showDetail(leaderboard[1])">
          <view class="top-avatar">
            <text class="avatar-text">{{ leaderboard[1].student_name.charAt(0) }}</text>
          </view>
          <view class="top-medal">🥈</view>
          <text class="top-name">{{ leaderboard[1].student_name }}</text>
          <text class="top-value">{{ leaderboard[1].value }}</text>
        </view>
        <view class="top-item first" @click="showDetail(leaderboard[0])">
          <view class="top-avatar crown">
            <text class="avatar-text">{{ leaderboard[0].student_name.charAt(0) }}</text>
          </view>
          <view class="top-medal">🥇</view>
          <text class="top-name">{{ leaderboard[0].student_name }}</text>
          <text class="top-value">{{ leaderboard[0].value }}</text>
        </view>
        <view class="top-item third" @click="showDetail(leaderboard[2])">
          <view class="top-avatar">
            <text class="avatar-text">{{ leaderboard[2].student_name.charAt(0) }}</text>
          </view>
          <view class="top-medal">🥉</view>
          <text class="top-name">{{ leaderboard[2].student_name }}</text>
          <text class="top-value">{{ leaderboard[2].value }}</text>
        </view>
      </view>

      <!-- 其他排名 -->
      <view class="rank-list">
        <view
          class="rank-item"
          v-for="item in restLeaderboard"
          :key="item.rank"
        >
          <text class="rank-num">{{ item.rank }}</text>
          <view class="rank-avatar">
            <text class="avatar-text">{{ item.student_name.charAt(0) }}</text>
          </view>
          <view class="rank-info">
            <text class="rank-name">{{ item.student_name }}</text>
            <text class="rank-level" v-if="item.level_icon">{{ item.level_icon }}</text>
          </view>
          <text class="rank-value">{{ item.value }}</text>
        </view>
      </view>

      <view class="empty-state" v-if="!leaderboard.length">
        <text class="empty-icon">🏆</text>
        <text class="empty-text">暂无排行数据</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { leaderboardApi } from '@/api'

const currentTab = ref('energy')
const period = ref('week')
const leaderboard = ref<any[]>([])
const myRank = ref<number | null>(null)
const myValue = ref<number | null>(null)

const restLeaderboard = computed(() => {
  return leaderboard.value.slice(3)
})

onMounted(() => {
  loadLeaderboard()
})

watch([currentTab, period], () => {
  loadLeaderboard()
})

async function loadLeaderboard() {
  try {
    const params = { period: period.value, limit: 50 }
    const res = currentTab.value === 'energy'
      ? await leaderboardApi.getEnergyLeaderboard(params)
      : await leaderboardApi.getTrainingLeaderboard(params)

    leaderboard.value = res.items
    myRank.value = res.my_rank
    myValue.value = res.my_value
  } catch (error) {
    // #ifdef DEV
    console.error('加载排行榜失败', error)
    // #endif
  }
}

function showDetail(item: any) {
  // 可以跳转到学员详情或展示更多信息
  // #ifdef DEV
  console.log('查看详情', item)
  // #endif
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
}

.tabs {
  display: flex;
  background: #FFFFFF;
  padding: 20rpx;
  gap: 20rpx;
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  padding: 24rpx;
  border-radius: 20rpx;
  background: #F5F5F5;
  transition: all 0.3s ease;
}

.tab.active {
  background: linear-gradient(135deg, #FFB347, #FF8800);
}

.tab-icon {
  font-size: 32rpx;
}

.tab-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #666;
}

.tab.active .tab-text {
  color: #FFFFFF;
}

.period-filter {
  display: flex;
  justify-content: center;
  gap: 20rpx;
  padding: 20rpx;
  background: #FFFFFF;
}

.period-item {
  padding: 12rpx 32rpx;
  border-radius: 999rpx;
  font-size: 26rpx;
  color: #666;
  background: #F5F5F5;
}

.period-item.active {
  background: #FFF3E0;
  color: #FF8800;
}

.my-rank {
  padding: 20rpx;
}

.my-rank-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  border-radius: 24rpx;
}

.my-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 32rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.my-info {
  flex: 1;
  margin-left: 20rpx;
}

.my-name {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  display: block;
}

.my-value {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 6rpx;
}

.my-rank-num {
  display: flex;
  align-items: baseline;
}

.rank-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.rank-value {
  font-size: 48rpx;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0 6rpx;
}

.leaderboard {
  padding: 20rpx;
}

.top-three {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding: 40rpx 20rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  margin-bottom: 20rpx;
}

.top-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200rpx;
}

.top-item.first {
  order: 2;
  margin: 0 -20rpx;
  z-index: 1;
}

.top-item.second {
  order: 1;
}

.top-item.third {
  order: 3;
}

.top-avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFD6A5, #FFB347);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.top-item.first .top-avatar {
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #FFD700, #FFA500);
}

.top-avatar .avatar-text {
  font-size: 36rpx;
  color: #FFFFFF;
}

.top-item.first .top-avatar .avatar-text {
  font-size: 44rpx;
}

.top-medal {
  font-size: 40rpx;
  margin-top: -20rpx;
}

.top-item.first .top-medal {
  font-size: 48rpx;
}

.top-name {
  font-size: 26rpx;
  color: #333;
  font-weight: 600;
  margin-top: 12rpx;
}

.top-value {
  font-size: 24rpx;
  color: #FF8800;
  font-weight: 700;
  margin-top: 6rpx;
}

.rank-list {
  background: #FFFFFF;
  border-radius: 24rpx;
  overflow: hidden;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-bottom: 2rpx solid #F5F5F5;
}

.rank-item:last-child {
  border-bottom: none;
}

.rank-num {
  width: 60rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #999;
  text-align: center;
}

.rank-avatar {
  width: 70rpx;
  height: 70rpx;
  border-radius: 50%;
  background: #FFF3E0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 16rpx;
}

.rank-avatar .avatar-text {
  font-size: 28rpx;
  color: #FF8800;
}

.rank-info {
  flex: 1;
  margin-left: 20rpx;
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.rank-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.rank-level {
  font-size: 24rpx;
}

.rank-value {
  font-size: 28rpx;
  font-weight: 700;
  color: #FF8800;
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
  background: #FFFFFF;
  border-radius: 24rpx;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}
</style>
