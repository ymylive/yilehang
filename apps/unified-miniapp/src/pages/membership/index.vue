<template>
  <view class="membership-page">
    <!-- 余额卡片 -->
    <view class="balance-card">
      <view class="balance-header">
        <text class="balance-title">剩余课时</text>
        <text class="balance-link" @click="goToTransactions">消费记录 ></text>
      </view>
      <view class="balance-value">
        <text class="value">{{ totalRemaining }}</text>
        <text class="unit">次</text>
      </view>
    </view>

    <!-- 我的会员卡 -->
    <view class="section">
      <view class="section-title">我的会员卡</view>

      <view v-if="memberships.length > 0" class="card-list">
        <view
          v-for="item in memberships"
          :key="item.id"
          class="membership-item"
        >
          <view class="item-header">
            <view class="card-name">{{ item.card?.name }}</view>
            <view :class="['card-status', item.status]">
              {{ getStatusText(item.status) }}
            </view>
          </view>
          <view class="item-body">
            <view class="remaining">
              <text class="remaining-value">{{ item.remaining_times }}</text>
              <text class="remaining-label">剩余课时</text>
            </view>
            <view class="expire" v-if="item.expire_date">
              <text class="expire-label">有效期至</text>
              <text class="expire-value">{{ formatDate(item.expire_date) }}</text>
            </view>
            <view class="expire" v-else>
              <text class="expire-label">有效期至</text>
              <text class="expire-value">永久有效</text>
            </view>
          </view>
          <view class="item-footer">
            <text class="purchase-date">购买日期: {{ formatDateTime(item.purchase_date) }}</text>
          </view>
        </view>
      </view>

      <view v-else class="empty-state">
        <image :src="emptyIcon" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无会员卡</text>
      </view>
    </view>

    <!-- 购买会员卡 -->
    <view class="section">
      <view class="section-title">购买会员卡</view>
      <view class="section-subtitle">可咨询门店或联系教练获取优惠与套餐</view>

      <view class="purchase-list">
        <view
          v-for="card in availableCards"
          :key="card.id"
          class="purchase-item"
        >
          <view class="card-info">
            <view class="card-name">{{ card.name }}</view>
            <view class="card-desc">{{ card.description || getCardDesc(card) }}</view>
          </view>
          <view class="card-price">
            <view class="price-current">
              <text class="currency">¥</text>
              <text class="amount">{{ card.price }}</text>
            </view>
            <view class="price-original" v-if="card.original_price && card.original_price > card.price">
              ¥{{ card.original_price }}
            </view>
          </view>
        </view>
      </view>

      <view class="contact-tip">
        <wd-icon name="phone" size="32rpx" />
        <text>购买与咨询请联系门店或教练</text>
      </view>
    </view>
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { ref, computed, onMounted } from 'vue'
import { membershipApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

interface MembershipCard {
  id: number
  name: string
  card_type: string
  total_times: number | null
  duration_days: number | null
  price: number
  original_price: number | null
  course_type: string | null
  description: string | null
}

interface StudentMembership {
  id: number
  student_id: number
  card_id: number
  remaining_times: number
  expire_date: string | null
  status: string
  purchase_date: string
  card?: MembershipCard
}

const memberships = ref<StudentMembership[]>([])
const availableCards = ref<MembershipCard[]>([])
const loading = ref(false)
const emptyIcon = getSemanticIcon('membership-empty')

const totalRemaining = computed(() => {
  return memberships.value
    .filter(m => m.status === 'active')
    .reduce((sum, m) => sum + m.remaining_times, 0)
})

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    active: '使用中',
    expired: '已过期',
    exhausted: '已用完'
  }
  return map[status] || status
}

function getCardDesc(card: MembershipCard): string {
  if (card.card_type === 'times' && card.total_times) {
    return `${card.total_times}次课程`
  }
  if (card.card_type === 'duration' && card.duration_days) {
    return `${card.duration_days}天有效`
  }
  return ''
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function goToTransactions() {
  uni.navigateTo({
    url: '/pages/membership/transactions'
  })
}

async function loadMemberships() {
  try {
    memberships.value = await membershipApi.list()
  } catch (error: any) {
    uni.showToast({ title: error.message || '加载失败', icon: 'none' })
  }
}

async function loadAvailableCards() {
  try {
    availableCards.value = await membershipApi.getCards()
  } catch (error) {
    console.error('加载可购会员卡失败', error)
  }
}

onMounted(() => {
  loadMemberships()
  loadAvailableCards()
})
</script>

<style lang="scss" scoped>
.membership-page {
  min-height: 100vh;
  background-color: #FFFBF5;
  padding-bottom: calc(150rpx + env(safe-area-inset-bottom));
}

.balance-card {
  background: linear-gradient(135deg, #FF8800 0%, #FFB347 100%);
  margin: 20rpx;
  padding: 40rpx;
  border-radius: 24rpx;
  color: #fff;
  animation: fadeUp 0.4s ease-out;
}

.balance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.balance-title {
  font-size: 30rpx;
}

.balance-link {
  font-size: 24rpx;
  opacity: 0.9;
}

.balance-value {
  display: flex;
  align-items: baseline;
}

.balance-value .value {
  font-size: 64rpx;
  font-weight: bold;
}

.balance-value .unit {
  font-size: 28rpx;
  margin-left: 8rpx;
}

.section {
  background: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  animation: fadeUp 0.4s ease-out;

  &:nth-child(2) { animation-delay: 0.1s; animation-fill-mode: both; }
  &:nth-child(3) { animation-delay: 0.2s; animation-fill-mode: both; }
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 12rpx;
}

.section-subtitle {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 20rpx;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.membership-item {
  background: #FFF7ED;
  border-radius: 16rpx;
  padding: 24rpx;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.99);
  }
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.card-status {
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
}

.card-status.active {
  background: #E8F5E9;
  color: #4CAF50;
}

.card-status.expired,
.card-status.exhausted {
  background: #FFEBEE;
  color: #F44336;
}

.item-body {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
}

.remaining-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #FF8800;
}

.remaining-label {
  font-size: 22rpx;
  color: #666;
  margin-left: 8rpx;
}

.expire-label {
  font-size: 22rpx;
  color: #999;
}

.expire-value {
  font-size: 24rpx;
  color: #333;
  margin-top: 6rpx;
}

.item-footer {
  margin-top: 12rpx;
  font-size: 22rpx;
  color: #999;
}

.purchase-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.purchase-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFF7ED;
  border-radius: 16rpx;
  padding: 20rpx;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.99);
  }
}

.card-info .card-name {
  font-size: 28rpx;
  color: #333;
}

.card-info .card-desc {
  font-size: 22rpx;
  color: #999;
  margin-top: 6rpx;
}

.card-price {
  text-align: right;
}

.price-current {
  font-size: 28rpx;
  color: #FF8800;
}

.price-original {
  font-size: 22rpx;
  color: #bbb;
  text-decoration: line-through;
}

.contact-tip {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 20rpx;
  font-size: 24rpx;
  color: #666;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
