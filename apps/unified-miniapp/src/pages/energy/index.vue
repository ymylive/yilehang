<template>
  <view class="page">
    <!-- 顶部能量卡片 -->
    <view class="energy-header">
      <view class="header-bg">
        <view class="bg-orb orb-1"></view>
        <view class="bg-orb orb-2"></view>
      </view>
      <view class="header-content">
        <view class="balance-section">
          <text class="balance-label">我的能量</text>
          <view class="balance-row">
            <text class="balance-value">{{ account.balance }}</text>
            <text class="balance-unit">⚡</text>
          </view>
        </view>
        <view class="level-section">
          <view class="level-badge">
            <text class="level-icon">{{ account.level_icon }}</text>
            <text class="level-name">{{ account.level_name }}</text>
          </view>
          <view class="level-progress" v-if="account.next_level_points">
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: levelProgress + '%' }"></view>
            </view>
            <text class="progress-text">距离下一等级还需 {{ account.next_level_points - account.total_earned }} 能量</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view class="quick-actions">
      <view class="action-card" @click="goTo('/pages/energy/redeem')">
        <view class="action-icon">🎁</view>
        <text class="action-name">兑换商城</text>
      </view>
      <view class="action-card" @click="goTo('/pages/leaderboard/index')">
        <view class="action-icon">🏆</view>
        <text class="action-name">排行榜</text>
      </view>
      <view class="action-card" @click="showRules = true">
        <view class="action-icon">📋</view>
        <text class="action-name">积分规则</text>
      </view>
    </view>

    <!-- 今日/本周统计 -->
    <view class="stats-section">
      <view class="stat-item">
        <text class="stat-value">{{ summary.today_earned }}</text>
        <text class="stat-label">今日获取</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-value">{{ summary.week_earned }}</text>
        <text class="stat-label">本周获取</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-value">{{ account.total_earned }}</text>
        <text class="stat-label">累计获取</text>
      </view>
    </view>

    <!-- 交易记录 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">能量明细</text>
        <view class="filter-tabs">
          <text
            :class="['tab', { active: filter === '' }]"
            @click="filter = ''"
          >全部</text>
          <text
            :class="['tab', { active: filter === 'earn' }]"
            @click="filter = 'earn'"
          >获取</text>
          <text
            :class="['tab', { active: filter === 'spend' }]"
            @click="filter = 'spend'"
          >消费</text>
        </view>
      </view>

      <view class="transaction-list" v-if="transactions.length">
        <view
          class="transaction-item"
          v-for="item in transactions"
          :key="item.id"
        >
          <view class="trans-icon" :class="item.type">
            {{ item.type === 'earn' ? '↑' : '↓' }}
          </view>
          <view class="trans-info">
            <text class="trans-desc">{{ item.description }}</text>
            <text class="trans-time">{{ formatTime(item.created_at) }}</text>
          </view>
          <text :class="['trans-amount', item.type]">
            {{ item.amount > 0 ? '+' : '' }}{{ item.amount }}
          </text>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-icon">📝</text>
        <text class="empty-text">暂无记录</text>
      </view>

      <view class="load-more" v-if="hasMore" @click="loadMore">
        <text>加载更多</text>
      </view>
    </view>

    <!-- 积分规则弹窗 -->
    <view class="rules-modal" v-if="showRules" @click="showRules = false">
      <view class="rules-card" @click.stop>
        <view class="rules-header">
          <text class="rules-title">积分规则</text>
          <text class="rules-close" @click="showRules = false">×</text>
        </view>
        <scroll-view class="rules-content" scroll-y>
          <view class="rule-item" v-for="rule in rules" :key="rule.id">
            <view class="rule-info">
              <text class="rule-name">{{ rule.name }}</text>
              <text class="rule-desc">{{ rule.description }}</text>
            </view>
            <text class="rule-points">+{{ rule.points }}</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { energyApi } from '@/api'

const userStore = useUserStore()

const account = ref({
  balance: 0,
  total_earned: 0,
  total_spent: 0,
  level: 1,
  level_name: '新手',
  level_icon: '🌱',
  next_level_points: 100
})

const summary = ref({
  today_earned: 0,
  week_earned: 0
})

const transactions = ref<any[]>([])
const rules = ref<any[]>([])
const filter = ref('')
const page = ref(1)
const hasMore = ref(true)
const showRules = ref(false)

const levelProgress = computed(() => {
  if (!account.value.next_level_points) return 100
  const current = account.value.total_earned
  const next = account.value.next_level_points
  // 简化计算，假设每级需要的点数
  const prevLevel = next - 100 // 简化
  return Math.min(100, ((current - prevLevel) / (next - prevLevel)) * 100)
})

onMounted(async () => {
  await Promise.all([
    loadAccount(),
    loadSummary(),
    loadTransactions(),
    loadRules()
  ])
})

watch(filter, () => {
  page.value = 1
  transactions.value = []
  loadTransactions()
})

async function loadAccount() {
  try {
    const res = await energyApi.getAccount()
    account.value = res
  } catch (error) {
    console.error('加载账户失败', error)
  }
}

async function loadSummary() {
  try {
    const res = await energyApi.getSummary()
    summary.value = res
  } catch (error) {
    console.error('加载摘要失败', error)
  }
}

async function loadTransactions() {
  try {
    const params: any = { page: page.value, page_size: 20 }
    if (filter.value) params.type = filter.value

    const res = await energyApi.getTransactions(params)
    if (page.value === 1) {
      transactions.value = res.items
    } else {
      transactions.value.push(...res.items)
    }
    hasMore.value = transactions.value.length < res.total
  } catch (error) {
    console.error('加载交易记录失败', error)
  }
}

async function loadRules() {
  try {
    const res = await energyApi.getRules()
    rules.value = res
  } catch (error) {
    console.error('加载规则失败', error)
  }
}

function loadMore() {
  page.value++
  loadTransactions()
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`

  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
}

function goTo(url: string) {
  uni.navigateTo({ url })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
}

.energy-header {
  position: relative;
  padding: 60rpx 30rpx 40rpx;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
  border-radius: 0 0 60rpx 60rpx;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.orb-1 {
  width: 200rpx;
  height: 200rpx;
  top: -50rpx;
  right: -30rpx;
}

.orb-2 {
  width: 150rpx;
  height: 150rpx;
  bottom: 20rpx;
  left: -40rpx;
}

.header-content {
  position: relative;
  z-index: 1;
}

.balance-section {
  text-align: center;
  margin-bottom: 30rpx;
}

.balance-label {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.balance-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-top: 10rpx;
}

.balance-value {
  font-size: 80rpx;
  font-weight: 800;
  color: #FFFFFF;
}

.balance-unit {
  font-size: 40rpx;
  margin-left: 10rpx;
}

.level-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.level-badge {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 12rpx 24rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999rpx;
}

.level-icon {
  font-size: 32rpx;
}

.level-name {
  font-size: 26rpx;
  color: #FFFFFF;
  font-weight: 600;
}

.level-progress {
  width: 100%;
  max-width: 400rpx;
}

.progress-bar {
  height: 12rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #FFFFFF;
  border-radius: 6rpx;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 8rpx;
  text-align: center;
  display: block;
}

.quick-actions {
  display: flex;
  justify-content: space-around;
  padding: 0 30rpx;
  margin-top: -30rpx;
  position: relative;
  z-index: 2;
}

.action-card {
  flex: 1;
  max-width: 200rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
}

.action-icon {
  font-size: 48rpx;
  margin-bottom: 12rpx;
}

.action-name {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.stats-section {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin: 30rpx;
  padding: 30rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 40rpx;
  font-weight: 700;
  color: #FF8800;
  display: block;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.stat-divider {
  width: 2rpx;
  height: 60rpx;
  background: #EEE;
}

.section {
  margin: 30rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.filter-tabs {
  display: flex;
  gap: 16rpx;
}

.tab {
  font-size: 24rpx;
  color: #999;
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
}

.tab.active {
  background: #FFF3E0;
  color: #FF8800;
}

.transaction-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.transaction-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #FAFAFA;
  border-radius: 16rpx;
}

.trans-icon {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
  margin-right: 20rpx;
}

.trans-icon.earn {
  background: #E8F5E9;
  color: #4CAF50;
}

.trans-icon.spend {
  background: #FFF3E0;
  color: #FF8800;
}

.trans-info {
  flex: 1;
}

.trans-desc {
  font-size: 28rpx;
  color: #333;
  display: block;
}

.trans-time {
  font-size: 22rpx;
  color: #999;
  margin-top: 6rpx;
}

.trans-amount {
  font-size: 32rpx;
  font-weight: 700;
}

.trans-amount.earn {
  color: #4CAF50;
}

.trans-amount.spend {
  color: #FF8800;
}

.empty-state {
  text-align: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 60rpx;
  display: block;
  margin-bottom: 16rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.load-more {
  text-align: center;
  padding: 20rpx;
  color: #FF8800;
  font-size: 26rpx;
}

.rules-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.rules-card {
  width: 85%;
  max-height: 70vh;
  background: #FFFFFF;
  border-radius: 24rpx;
  overflow: hidden;
}

.rules-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 2rpx solid #F0F0F0;
}

.rules-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.rules-close {
  font-size: 40rpx;
  color: #999;
}

.rules-content {
  max-height: 60vh;
  padding: 20rpx 30rpx;
}

.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 2rpx solid #F5F5F5;
}

.rule-item:last-child {
  border-bottom: none;
}

.rule-info {
  flex: 1;
}

.rule-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  display: block;
}

.rule-desc {
  font-size: 24rpx;
  color: #999;
  margin-top: 6rpx;
}

.rule-points {
  font-size: 32rpx;
  font-weight: 700;
  color: #FF8800;
}
</style>
