<template>
  <view class="membership-page">
    <!-- 课时余额卡片 -->
    <view class="balance-card">
      <view class="balance-header">
        <text class="balance-title">课时余额</text>
        <text class="balance-link" @click="goToTransactions">消费记录 ></text>
      </view>
      <view class="balance-value">
        <text class="value">{{ totalRemaining }}</text>
        <text class="unit">次</text>
      </view>
    </view>

    <!-- 我的课时卡列表 -->
    <view class="section">
      <view class="section-title">我的课时卡</view>

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
              <text class="remaining-label">剩余次数</text>
            </view>
            <view class="expire" v-if="item.expire_date">
              <text class="expire-label">有效期至</text>
              <text class="expire-value">{{ formatDate(item.expire_date) }}</text>
            </view>
            <view class="expire" v-else>
              <text class="expire-label">有效期</text>
              <text class="expire-value">永久有效</text>
            </view>
          </view>
          <view class="item-footer">
            <text class="purchase-date">购买时间：{{ formatDateTime(item.purchase_date) }}</text>
          </view>
        </view>
      </view>

      <view v-else class="empty-state">
        <image src="/static/empty.png" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无课时卡</text>
      </view>
    </view>

    <!-- 可购买的课时卡 -->
    <view class="section">
      <view class="section-title">购买课时卡</view>
      <view class="section-subtitle">线下付款后，管理员将为您充值</view>

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
        <text>如需购买请联系客服或到店咨询</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { membershipApi } from '@/api'

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
    return `${card.total_times}次课时`
  }
  if (card.card_type === 'duration' && card.duration_days) {
    return `${card.duration_days}天有效期`
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
    console.error('加载课时卡类型失败', error)
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
  background-color: #f5f5f5;
  padding-bottom: 40rpx;
}

.balance-card {
  background: linear-gradient(135deg, #4caf50 0%, #81c784 100%);
  margin: 20rpx;
  padding: 40rpx;
  border-radius: 20rpx;
  color: #fff;

  .balance-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;

    .balance-title {
      font-size: 28rpx;
      opacity: 0.9;
    }

    .balance-link {
      font-size: 26rpx;
      opacity: 0.8;
    }
  }

  .balance-value {
    .value {
      font-size: 80rpx;
      font-weight: 600;
    }

    .unit {
      font-size: 32rpx;
      margin-left: 8rpx;
    }
  }
}

.section {
  background-color: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;

  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 8rpx;
  }

  .section-subtitle {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 24rpx;
  }
}

.card-list {
  .membership-item {
    background-color: #f9f9f9;
    border-radius: 12rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;

    &:last-child {
      margin-bottom: 0;
    }

    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20rpx;

      .card-name {
        font-size: 30rpx;
        font-weight: 600;
        color: #333;
      }

      .card-status {
        font-size: 24rpx;
        padding: 6rpx 16rpx;
        border-radius: 20rpx;

        &.active {
          background-color: #e8f5e9;
          color: #4caf50;
        }

        &.expired {
          background-color: #ffebee;
          color: #f44336;
        }

        &.exhausted {
          background-color: #f5f5f5;
          color: #999;
        }
      }
    }

    .item-body {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20rpx 0;
      border-top: 1rpx dashed #e0e0e0;
      border-bottom: 1rpx dashed #e0e0e0;

      .remaining {
        .remaining-value {
          font-size: 48rpx;
          font-weight: 600;
          color: #4caf50;
        }

        .remaining-label {
          display: block;
          font-size: 24rpx;
          color: #999;
          margin-top: 4rpx;
        }
      }

      .expire {
        text-align: right;

        .expire-label {
          display: block;
          font-size: 24rpx;
          color: #999;
        }

        .expire-value {
          font-size: 28rpx;
          color: #333;
        }
      }
    }

    .item-footer {
      margin-top: 16rpx;

      .purchase-date {
        font-size: 24rpx;
        color: #999;
      }
    }
  }
}

.purchase-list {
  .purchase-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24rpx;
    background-color: #f9f9f9;
    border-radius: 12rpx;
    margin-bottom: 16rpx;

    &:last-child {
      margin-bottom: 0;
    }

    .card-info {
      .card-name {
        font-size: 30rpx;
        font-weight: 600;
        color: #333;
        margin-bottom: 8rpx;
      }

      .card-desc {
        font-size: 24rpx;
        color: #999;
      }
    }

    .card-price {
      text-align: right;

      .price-current {
        color: #f44336;

        .currency {
          font-size: 28rpx;
        }

        .amount {
          font-size: 40rpx;
          font-weight: 600;
        }
      }

      .price-original {
        font-size: 24rpx;
        color: #999;
        text-decoration: line-through;
      }
    }
  }
}

.contact-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 30rpx;
  padding: 20rpx;
  background-color: #fff3e0;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #ff9800;

  text {
    margin-left: 12rpx;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;

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
</style>
