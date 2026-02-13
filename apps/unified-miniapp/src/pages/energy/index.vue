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
            <image :src="energyBoltIcon" class="balance-unit" mode="aspectFit" />
          </view>
        </view>
        <view class="level-section">
          <view class="level-badge">
            <view class="level-icon">
              <wd-icon :name="resolveLevelIcon(account.level_icon)" size="28rpx" color="#FFFFFF" />
            </view>
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
        <view class="action-icon">
          <wd-icon name="gift" size="44rpx" color="#2563eb" />
        </view>
        <text class="action-name">兑换商城</text>
      </view>
      <view class="action-card" @click="goTo('/pages/leaderboard/index')">
        <view class="action-icon">
          <wd-icon name="chart-bar" size="44rpx" color="#2563eb" />
        </view>
        <text class="action-name">排行榜</text>
      </view>
      <view class="action-card" @click="showRules = true">
        <view class="action-icon">
          <wd-icon name="note" size="44rpx" color="#2563eb" />
        </view>
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
            <image
              :src="transactionDirectionIcons[item.type === 'earn' ? 'earn' : 'spend']"
              class="trans-icon-image"
              mode="aspectFit"
            />
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
        <view class="empty-icon">
          <image :src="energyEmptyIcon" class="empty-icon-image" mode="aspectFit" />
        </view>
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
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { energyApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

const userStore = useUserStore()
const energyBoltIcon = getSemanticIcon('icon-energy-bolt')
const transactionDirectionIcons = {
  earn: getSemanticIcon('icon-arrow-up'),
  spend: getSemanticIcon('icon-arrow-down')
} as const
const energyEmptyIcon = getSemanticIcon('energy-empty')

const account = ref({
  balance: 0,
  total_earned: 0,
  total_spent: 0,
  level: 1,
  level_name: '新手',
  level_icon: 'star',
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
const transactionsLoading = ref(false)
let transactionsRequestId = 0
let activeTransactionKey = ''

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
  hasMore.value = true
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
  const requestPage = page.value
  const requestFilter = filter.value
  const requestKey = `${requestFilter}:${requestPage}`

  if (transactionsLoading.value && activeTransactionKey === requestKey) {
    return
  }

  activeTransactionKey = requestKey
  const requestId = ++transactionsRequestId
  transactionsLoading.value = true

  try {
    const params: any = { page: requestPage, page_size: 20 }
    if (requestFilter) params.type = requestFilter

    const res = await energyApi.getTransactions(params)
    if (
      requestId !== transactionsRequestId
      || requestPage !== page.value
      || requestFilter !== filter.value
    ) {
      return
    }

    if (requestPage === 1) {
      transactions.value = res.items
    } else {
      transactions.value.push(...res.items)
    }
    hasMore.value = transactions.value.length < res.total
  } catch (error) {
    console.error('加载交易记录失败', error)
  } finally {
    if (requestId === transactionsRequestId) {
      transactionsLoading.value = false
    }
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
  if (!hasMore.value || transactionsLoading.value) {
    return
  }
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

function goTo(url: string) {
  uni.navigateTo({ url })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
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
  width: 40rpx;
  height: 40rpx;
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
  width: 52rpx;
  height: 52rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.26);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1rpx rgba(255, 255, 255, 0.22);
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
  transition: transform 220ms ease, box-shadow 220ms ease;
  cursor: pointer;
}

.action-card:active {
  transform: translateY(2rpx);
  box-shadow: 0 6rpx 18rpx rgba(29, 78, 216, 0.18);
}

.action-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 22rpx;
  background: linear-gradient(135deg, #e8f0ff, #eef5ff);
  margin-bottom: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1rpx rgba(191, 210, 247, 0.6);
}

.action-name {
  font-size: 26rpx;
  color: #334155;
  font-weight: 500;
}

.tab,
.load-more {
  transition: all 200ms ease;
}

.tab:active,
.load-more:active {
  transform: translateY(1rpx);
  opacity: 0.88;
}

.empty-state {
  text-align: center;
  padding: 60rpx 0;
}

.empty-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 24rpx;
  background: #f1f5f9;
  margin: 0 auto 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;
}

.empty-icon-image {
  width: 64rpx;
  height: 64rpx;
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

.trans-icon-image {
  width: 28rpx;
  height: 28rpx;
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
