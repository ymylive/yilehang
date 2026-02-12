<template>
  <view class="page">
    <!-- 标签切换 -->
    <view class="tabs">
      <view
        :class="['tab', { active: currentTab === 'energy' }]"
        @click="currentTab = 'energy'"
      >
        <view class="tab-icon">
          <wd-icon name="star-filled" size="30rpx" :color="currentTab === 'energy' ? '#ffffff' : '#2563eb'" />
        </view>
        <text class="tab-text">能量榜</text>
      </view>
      <view
        :class="['tab', { active: currentTab === 'training' }]"
        @click="currentTab = 'training'"
      >
        <view class="tab-icon">
          <wd-icon name="app" size="30rpx" :color="currentTab === 'training' ? '#ffffff' : '#2563eb'" />
        </view>
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
          <view class="top-medal">
            <wd-icon name="star-filled" size="36rpx" color="#94a3b8" />
          </view>
          <text class="top-name">{{ leaderboard[1].student_name }}</text>
          <text class="top-value">{{ leaderboard[1].value }}</text>
        </view>
        <view class="top-item first" @click="showDetail(leaderboard[0])">
          <view class="top-avatar crown">
            <text class="avatar-text">{{ leaderboard[0].student_name.charAt(0) }}</text>
          </view>
          <view class="top-medal">
            <wd-icon name="star-filled" size="42rpx" color="#f59e0b" />
          </view>
          <text class="top-name">{{ leaderboard[0].student_name }}</text>
          <text class="top-value">{{ leaderboard[0].value }}</text>
        </view>
        <view class="top-item third" @click="showDetail(leaderboard[2])">
          <view class="top-avatar">
            <text class="avatar-text">{{ leaderboard[2].student_name.charAt(0) }}</text>
          </view>
          <view class="top-medal">
            <wd-icon name="star-filled" size="34rpx" color="#c08457" />
          </view>
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
            <view class="rank-level" v-if="item.level_icon">
              <wd-icon :name="resolveLevelIcon(item.level_icon)" size="24rpx" color="#f59e0b" />
            </view>
          </view>
          <text class="rank-value">{{ item.value }}</text>
        </view>
      </view>

      <view class="empty-state" v-if="!leaderboard.length">
        <view class="empty-icon">
          <wd-icon name="chart-bar" size="62rpx" color="#94a3b8" />
        </view>
        <text class="empty-text">暂无排行数据</text>
      </view>
    </view>
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { leaderboardApi } from '@/api'

const currentTab = ref('energy')
const period = ref('week')
const leaderboard = ref<any[]>([])
const myRank = ref<number | null>(null)
const myValue = ref<number | null>(null)
const leaderboardLoading = ref(false)
let leaderboardRequestId = 0
let activeLeaderboardKey = ''

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
  const requestTab = currentTab.value
  const requestPeriod = period.value
  const requestKey = `${requestTab}:${requestPeriod}`

  if (leaderboardLoading.value && activeLeaderboardKey === requestKey) {
    return
  }

  activeLeaderboardKey = requestKey
  const requestId = ++leaderboardRequestId
  leaderboardLoading.value = true

  try {
    const params = { period: requestPeriod, limit: 50 }
    const res = requestTab === 'energy'
      ? await leaderboardApi.getEnergyLeaderboard(params)
      : await leaderboardApi.getTrainingLeaderboard(params)

    if (
      requestId !== leaderboardRequestId
      || requestTab !== currentTab.value
      || requestPeriod !== period.value
    ) {
      return
    }

    leaderboard.value = res.items
    myRank.value = res.my_rank
    myValue.value = res.my_value
  } catch (error) {
    // #ifdef DEV
    console.error('加载排行榜失败', error)
    // #endif
  } finally {
    if (requestId === leaderboardRequestId) {
      leaderboardLoading.value = false
    }
  }
}

function showDetail(item: any) {
  // 可以跳转到学员详情或展示更多信息
  // #ifdef DEV
  console.log('查看详情', item)
  // #endif
}

function resolveLevelIcon(levelIcon?: string) {
  const icon = String(levelIcon || '').trim()
  const emojiMap: Record<string, string> = {
    '\u{1F331}': 'star',
    '\u2B50': 'star-filled',
    '\u{1F3C6}': 'chart-bar',
    '\u{1F451}': 'dashboard'
  }
  if (emojiMap[icon]) {
    return emojiMap[icon]
  }
  return /^[a-z0-9-]+$/i.test(icon) ? icon : 'star'
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
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
  cursor: pointer;
}

.tab:active {
  transform: translateY(2rpx);
}

.tab.active {
  background: linear-gradient(135deg, #FFB347, #FF8800);
}

.tab-icon {
  width: 54rpx;
  height: 54rpx;
  border-radius: 14rpx;
  background: rgba(255, 255, 255, 0.86);
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab.active .tab-icon {
  background: rgba(255, 255, 255, 0.22);
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
  cursor: pointer;
  transition: transform 220ms ease;
}

.top-item:active {
  transform: translateY(2rpx);
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
  width: 60rpx;
  height: 60rpx;
  margin-top: -20rpx;
  border-radius: 18rpx;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1rpx rgba(226, 232, 240, 0.9);
}

.top-item.first .top-medal {
  width: 68rpx;
  height: 68rpx;
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
  width: 40rpx;
  height: 40rpx;
  border-radius: 12rpx;
  background: #fff7ed;
  display: flex;
  align-items: center;
  justify-content: center;
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
  width: 108rpx;
  height: 108rpx;
  border-radius: 26rpx;
  background: #f1f5f9;
  margin: 0 auto 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}
</style>
