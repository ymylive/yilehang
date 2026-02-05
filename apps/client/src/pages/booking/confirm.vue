<template>
  <view class="confirm-page">
    <!-- 棰勭害淇℃伅鍗＄墖 -->
    <view class="booking-card">
      <view class="card-title">棰勭害淇℃伅</view>

      <view class="info-row">
        <text class="info-label">鏁欑粌</text>
        <text class="info-value">{{ coachName }}</text>
      </view>

      <view class="info-row">
        <text class="info-label">鏃ユ湡</text>
        <text class="info-value">{{ formatDate(bookingDate) }}</text>
      </view>

      <view class="info-row">
        <text class="info-label">鏃堕棿</text>
        <text class="info-value">{{ formatTime(startTime) }} - {{ formatTime(endTime) }}</text>
      </view>
    </view>

    <!-- 璇炬椂鍗′俊鎭?-->
    <view class="membership-card">
      <view class="card-title">璇炬椂鎵ｈ垂</view>

      <view v-if="membership" class="membership-info">
        <view class="membership-name">{{ membership.card_name || '璇炬椂鍗? }}</view>
        <view class="membership-balance">
          鍓╀綑 <text class="balance-value">{{ membership.remaining_times }}</text> 娆?        </view>
      </view>

      <view v-else class="no-membership">
        <text class="warning-text">鎮ㄦ殏鏃犲彲鐢ㄨ鏃跺崱</text>
        <view class="btn-purchase" @click="goToPurchase">鍘昏喘涔?/view>
      </view>

      <view class="deduct-info" v-if="membership">
        鏈棰勭害灏嗘墸闄?<text class="deduct-value">1</text> 娆¤鏃?      </view>
    </view>

    <!-- 澶囨敞 -->
    <view class="remark-card">
      <view class="card-title">澶囨敞锛堥€夊～锛?/view>
      <textarea
        v-model="remark"
        placeholder="璇疯緭鍏ュ娉ㄤ俊鎭?
        class="remark-input"
        :maxlength="200"
      />
    </view>

    <!-- 棰勭害椤荤煡 -->
    <view class="notice-card">
      <view class="card-title">棰勭害椤荤煡</view>
      <view class="notice-list">
        <view class="notice-item">1. 棰勭害鎴愬姛鍚庡皢鑷姩鎵ｉ櫎1娆¤鏃?/view>
        <view class="notice-item">2. 寮€璇惧墠2灏忔椂鍙厤璐瑰彇娑堬紝鍙栨秷鍚庤鏃惰嚜鍔ㄩ€€杩?/view>
        <view class="notice-item">3. 寮€璇惧墠2灏忔椂鍐呭彇娑堝皢鎵ｉ櫎璇炬椂</view>
        <view class="notice-item">4. 濡傞渶鏀规湡璇锋彁鍓嶈仈绯绘暀缁?/view>
      </view>
    </view>

    <!-- 搴曢儴鎿嶄綔鏍?-->
    <view class="bottom-bar">
      <view class="agreement">
        <checkbox :checked="agreed" @click="agreed = !agreed" />
        <text class="agreement-text">鎴戝凡闃呰骞跺悓鎰?/text>
        <text class="agreement-link" @click="viewAgreement">銆婇绾︽湇鍔″崗璁€?/text>
      </view>
      <button
        class="btn-submit"
        :disabled="!canSubmit"
        :loading="submitting"
        @click="submitBooking"
      >
        纭棰勭害
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { bookingApi, membershipApi } from '@/api/index'

interface Membership {
  id: number
  student_id: number
  card_id: number
  card_name?: string
  remaining_times: number
  expire_date: string | null
  status: string
}

const coachId = ref(0)
const coachName = ref('')
const bookingDate = ref('')
const startTime = ref('')
const endTime = ref('')
const remark = ref('')
const agreed = ref(false)
const submitting = ref(false)
const membership = ref<Membership | null>(null)

const weekdays = ['鏃?, '涓€', '浜?, '涓?, '鍥?, '浜?, '鍏?]

const canSubmit = computed(() => {
  return agreed.value && membership.value && membership.value.remaining_times > 0
})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}骞?{date.getMonth() + 1}鏈?{date.getDate()}鏃?鍛?{weekdays[date.getDay()]}`
}

function formatTime(timeStr: string): string {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}

async function loadMembership() {
  try {
    const data = await membershipApi.getMyMemberships()
    const list = data.items || data || []
    // 鎵惧埌鏈夋晥鐨勮鏃跺崱
    membership.value = list.find((m: Membership) =>
      m.status === 'active' && m.remaining_times > 0
    ) || null
  } catch (error) {
    console.error('鍔犺浇璇炬椂鍗″け璐?, error)
  }
}

function goToPurchase() {
  uni.navigateTo({
    url: '/pages/membership/index'
  })
}

function viewAgreement() {
  uni.showToast({ title: '鍔熻兘寮€鍙戜腑', icon: 'none' })
}

async function submitBooking() {
  if (!canSubmit.value || submitting.value) return

  submitting.value = true
  try {
    await bookingApi.create({
      coach_id: coachId.value,
      booking_date: bookingDate.value,
      start_time: startTime.value,
      end_time: endTime.value,
      notes: remark.value || undefined,
      membership_id: membership.value?.id
    })

    uni.showToast({ title: '棰勭害鎴愬姛', icon: 'success' })

    // 璺宠浆鍒拌琛ㄩ〉闈?    setTimeout(() => {
      uni.switchTab({
        url: '/pages/schedule/index'
      })
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '棰勭害澶辫触', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}

  coachId.value = parseInt(options.coachId) || 0
  coachName.value = decodeURIComponent(options.coachName || '')
  bookingDate.value = options.date || ''
  startTime.value = options.startTime || ''
  endTime.value = options.endTime || ''

  loadMembership()
})
</script>

<style lang="scss" scoped>
.confirm-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 200rpx;
}

.booking-card,
.membership-card,
.remark-card,
.notice-card {
  background-color: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;

  .card-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 24rpx;
  }
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f5f5f5;

  &:last-child {
    border-bottom: none;
  }

  .info-label {
    font-size: 28rpx;
    color: #666;
  }

  .info-value {
    font-size: 28rpx;
    color: #333;
    font-weight: 500;
  }
}

.membership-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;

  .membership-name {
    font-size: 28rpx;
    color: #333;
  }

  .membership-balance {
    font-size: 26rpx;
    color: #666;

    .balance-value {
      font-size: 36rpx;
      font-weight: 600;
      color: #FF8800;
    }
  }
}

.no-membership {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background-color: #fff3e0;
  border-radius: 12rpx;

  .warning-text {
    font-size: 28rpx;
    color: #ff9800;
  }

  .btn-purchase {
    padding: 12rpx 24rpx;
    background-color: #ff9800;
    color: #fff;
    font-size: 26rpx;
    border-radius: 20rpx;
  }
}

.deduct-info {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #999;
  text-align: center;

  .deduct-value {
    color: #f44336;
    font-weight: 600;
  }
}

.remark-input {
  width: 100%;
  height: 160rpx;
  padding: 20rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.notice-list {
  .notice-item {
    font-size: 26rpx;
    color: #666;
    line-height: 2;
  }
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background-color: #fff;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);

  .agreement {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16rpx;

    checkbox {
      transform: scale(0.8);
    }

    .agreement-text {
      font-size: 24rpx;
      color: #666;
      margin-left: 8rpx;
    }

    .agreement-link {
      font-size: 24rpx;
      color: #FF8800;
    }
  }

  .btn-submit {
    width: 100%;
    height: 88rpx;
    background-color: #FF8800;
    color: #fff;
    font-size: 32rpx;
    border-radius: 44rpx;
    border: none;

    &[disabled] {
      background-color: #ccc;
    }
  }
}
</style>
