<template>
  <view class="confirm-page">
    <!-- 预约信息卡片 -->
    <view class="booking-card">
      <view class="card-title">预约信息</view>

      <view class="info-row">
        <text class="info-label">教练</text>
        <text class="info-value">{{ coachName }}</text>
      </view>

      <view class="info-row">
        <text class="info-label">日期</text>
        <text class="info-value">{{ formatDate(bookingDate) }}</text>
      </view>

      <view class="info-row">
        <text class="info-label">时间</text>
        <text class="info-value">{{ formatTime(startTime) }} - {{ formatTime(endTime) }}</text>
      </view>
    </view>

    <!-- 课时卡信息 -->
    <view class="membership-card">
      <view class="card-title">课时扣费</view>

      <view v-if="membership" class="membership-info">
        <view class="membership-name">{{ membership.card_name || '课时卡' }}</view>
        <view class="membership-balance">
          剩余 <text class="balance-value">{{ membership.remaining_times }}</text> 次
        </view>
      </view>

      <view v-else class="no-membership">
        <text class="warning-text">您暂无可用课时卡</text>
        <view class="btn-purchase" @click="goToPurchase">去购买</view>
      </view>

      <view class="deduct-info" v-if="membership">
        本次预约将扣除 <text class="deduct-value">1</text> 次课时
      </view>
    </view>

    <!-- 备注 -->
    <view class="remark-card">
      <view class="card-title">备注（选填）</view>
      <textarea
        v-model="remark"
        placeholder="请输入备注信息"
        class="remark-input"
        :maxlength="200"
      />
    </view>

    <!-- 预约须知 -->
    <view class="notice-card">
      <view class="card-title">预约须知</view>
      <view class="notice-list">
        <view class="notice-item">1. 预约成功后将自动扣除1次课时</view>
        <view class="notice-item">2. 开课前2小时可免费取消，取消后课时自动退还</view>
        <view class="notice-item">3. 开课前2小时内取消将扣除课时</view>
        <view class="notice-item">4. 如需改期请提前联系教练</view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="agreement">
        <checkbox :checked="agreed" @click="agreed = !agreed" />
        <text class="agreement-text">我已阅读并同意</text>
        <text class="agreement-link" @click="viewAgreement">《预约服务协议》</text>
      </view>
      <button
        class="btn-submit"
        :disabled="!canSubmit"
        :loading="submitting"
        @click="submitBooking"
      >
        确认预约
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

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const canSubmit = computed(() => {
  return agreed.value && membership.value && membership.value.remaining_times > 0
})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 周${weekdays[date.getDay()]}`
}

function formatTime(timeStr: string): string {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}

async function loadMembership() {
  try {
    const data = await membershipApi.getMyMemberships()
    const list = data.items || data || []
    // 找到有效的课时卡
    membership.value = list.find((m: Membership) =>
      m.status === 'active' && m.remaining_times > 0
    ) || null
  } catch (error) {
    console.error('加载课时卡失败', error)
  }
}

function goToPurchase() {
  uni.navigateTo({
    url: '/pages/membership/index'
  })
}

function viewAgreement() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
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

    uni.showToast({ title: '预约成功', icon: 'success' })

    // 跳转到课表页面
    setTimeout(() => {
      uni.switchTab({
        url: '/pages/schedule/index'
      })
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '预约失败', icon: 'none' })
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
      color: #4caf50;
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
      color: #4caf50;
    }
  }

  .btn-submit {
    width: 100%;
    height: 88rpx;
    background-color: #4caf50;
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
