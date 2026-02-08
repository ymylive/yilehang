<template>
  <view class="confirm-page">
    <view v-if="initialLoading" class="skeleton-group">
      <view class="skeleton-hero shimmer"></view>
      <view class="skeleton-card shimmer"></view>
      <view class="skeleton-card shimmer"></view>
    </view>

    <view v-else>
      <view class="hero-card">
        <text class="hero-title">{{ isReschedule ? t.confirmReschedule : t.confirmBooking }}</text>
        <text class="hero-sub">{{ t.checkBeforeSubmit }}</text>

        <view class="hero-row">
          <text class="hero-label">{{ t.coach }}</text>
          <text class="hero-value">{{ coachName || '-' }}</text>
        </view>
        <view class="hero-row">
          <text class="hero-label">{{ t.date }}</text>
          <text class="hero-value">{{ formatDate(bookingDate) }}</text>
        </view>
        <view class="hero-row">
          <text class="hero-label">{{ t.time }}</text>
          <text class="hero-value">{{ formatTime(startTime) }} - {{ formatTime(endTime) }}</text>
        </view>
      </view>

      <view class="card" v-if="!isReschedule">
        <view class="card-head">
          <text class="card-title">{{ t.creditTitle }}</text>
          <text class="card-sub">{{ t.creditDesc }}</text>
        </view>

        <view v-if="membershipLoading" class="membership-skeleton shimmer"></view>

        <view class="membership" v-else-if="membership">
          <view class="membership-main">
            <text class="membership-name">{{ membership.card_name || membership.card?.name || t.membership }}</text>
            <text class="membership-expire" v-if="membership.expire_date">{{ t.validUntil }} {{ formatDay(membership.expire_date) }}</text>
            <text class="membership-expire" v-else>{{ t.noExpiry }}</text>
          </view>
          <text class="membership-count">{{ t.remaining }} {{ membership.remaining_times }} {{ t.timesUnit }}</text>
        </view>

        <view class="membership-empty" v-else>
          <text class="empty-title">{{ t.noMembership }}</text>
          <text class="empty-sub">{{ t.buyBeforeBooking }}</text>
          <button class="buy-btn" hover-class="btn-hover" :hover-stay-time="60" @click="goToPurchase">{{ t.buyCard }}</button>
        </view>
      </view>

      <view class="card" v-else>
        <view class="card-head">
          <text class="card-title">{{ t.rescheduleNotes }}</text>
        </view>
        <view class="notice-line">{{ t.rescheduleDesc }}</view>
      </view>

      <view class="card">
        <view class="card-head">
          <text class="card-title">{{ t.remarkTitle }}</text>
          <text class="card-sub">{{ t.max200 }}</text>
        </view>
        <textarea
          v-model="remark"
          class="remark-input"
          maxlength="200"
          :placeholder="isReschedule ? t.reschedulePlaceholder : t.bookingPlaceholder"
        />
      </view>

      <view class="card">
        <view class="card-head">
          <text class="card-title">{{ t.rulesTitle }}</text>
        </view>
        <view class="notice-line">1. {{ t.rule1 }}</view>
        <view class="notice-line">2. {{ t.rule2 }}</view>
        <view class="notice-line">3. {{ t.rule3 }}</view>
      </view>

      <view class="bottom-bar">
        <view class="agreement-row">
          <view :class="['agreement-check', { active: agreed }]" @click="toggleAgreement">?</view>
          <text class="agreement-text" @click="toggleAgreement">{{ t.agreeRules }}</text>
          <text class="agreement-link" @click="viewAgreement">{{ t.view }}</text>
        </view>

        <button
          class="submit-btn"
          :disabled="!canSubmit"
          :loading="submitting"
          hover-class="btn-hover"
          :hover-stay-time="60"
          @click="submitBooking"
        >
          {{ isReschedule ? t.confirmReschedule : t.confirmBooking }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { bookingApi, membershipApi } from '@/api/index'

interface Membership {
  id: number
  status: string
  remaining_times: number
  expire_date: string | null
  card_name?: string
  card?: {
    name?: string
  }
}

const t = {
  confirmReschedule: '\u786e\u8ba4\u6539\u671f',
  confirmBooking: '\u786e\u8ba4\u9884\u7ea6',
  checkBeforeSubmit: '\u8bf7\u6838\u5bf9\u65f6\u95f4\u4fe1\u606f\u540e\u63d0\u4ea4',
  coach: '\u6559\u7ec3',
  date: '\u65e5\u671f',
  time: '\u65f6\u95f4',
  weekdaySun: '\u5468\u65e5',
  weekdayMon: '\u5468\u4e00',
  weekdayTue: '\u5468\u4e8c',
  weekdayWed: '\u5468\u4e09',
  weekdayThu: '\u5468\u56db',
  weekdayFri: '\u5468\u4e94',
  weekdaySat: '\u5468\u516d',
  monthUnit: '\u6708',
  dayUnit: '\u65e5',
  creditTitle: '\u8bfe\u65f6\u6263\u8d39',
  creditDesc: '\u6bcf\u6b21\u9884\u7ea6\u6263\u9664 1 \u8bfe\u65f6',
  membership: '\u4f1a\u5458\u5361',
  validUntil: '\u6709\u6548\u671f\u81f3',
  noExpiry: '\u957f\u671f\u6709\u6548',
  remaining: '\u5269\u4f59',
  timesUnit: '\u6b21',
  noMembership: '\u6682\u65e0\u53ef\u7528\u4f1a\u5458\u5361',
  buyBeforeBooking: '\u8bf7\u5148\u8d2d\u4e70\u8bfe\u65f6\u5361\u540e\u518d\u9884\u7ea6',
  buyCard: '\u53bb\u8d2d\u4e70',
  rescheduleNotes: '\u6539\u671f\u8bf4\u660e',
  rescheduleDesc: '\u6539\u671f\u4e0d\u91cd\u590d\u6263\u51cf\u8bfe\u65f6\uff0c\u63d0\u4ea4\u540e\u5c06\u8986\u76d6\u539f\u9884\u7ea6\u65f6\u95f4\u3002',
  remarkTitle: '\u5907\u6ce8\uff08\u9009\u586b\uff09',
  max200: '\u6700\u591a 200 \u5b57',
  reschedulePlaceholder: '\u53ef\u586b\u5199\u6539\u671f\u539f\u56e0\u6216\u9700\u6c42',
  bookingPlaceholder: '\u53ef\u586b\u5199\u4e0a\u8bfe\u9700\u6c42\u6216\u63d0\u9192',
  rulesTitle: '\u9884\u7ea6\u987b\u77e5',
  rule1: '\u8bf7\u81f3\u5c11\u63d0\u524d 2 \u5c0f\u65f6\u53d6\u6d88\u6216\u6539\u671f\u3002',
  rule2: '\u8bf7\u63d0\u524d 10 \u5206\u949f\u5230\u573a\u7b7e\u5230\u3002',
  rule3: '\u82e5\u9047\u6559\u7ec3\u6392\u73ed\u8c03\u6574\uff0c\u5c06\u63d0\u524d\u901a\u77e5\u3002',
  agreeRules: '\u6211\u5df2\u9605\u8bfb\u5e76\u540c\u610f\u9884\u7ea6\u89c4\u5219',
  view: '\u67e5\u770b',
  bookingRules: '\u9884\u7ea6\u89c4\u5219',
  bookingRulesDesc: '\u8bf7\u63d0\u524d\u5230\u573a\u5e76\u9075\u5b88\u8bfe\u7a0b\u5b89\u6392\uff1b\u5982\u9700\u6539\u671f\u6216\u53d6\u6d88\uff0c\u8bf7\u81f3\u5c11\u63d0\u524d 2 \u5c0f\u65f6\u64cd\u4f5c\u3002',
  loadMembershipFail: '\u52a0\u8f7d\u4f1a\u5458\u4fe1\u606f\u5931\u8d25',
  rescheduleSuccess: '\u6539\u671f\u6210\u529f',
  bookingSuccess: '\u9884\u7ea6\u6210\u529f',
  rescheduleFail: '\u6539\u671f\u5931\u8d25',
  bookingFail: '\u9884\u7ea6\u5931\u8d25'
} as const

const coachId = ref(0)
const rescheduleId = ref(0)
const coachName = ref('')
const bookingDate = ref('')
const startTime = ref('')
const endTime = ref('')
const remark = ref('')

const agreed = ref(false)
const submitting = ref(false)
const membership = ref<Membership | null>(null)
const membershipLoading = ref(false)
const initialLoading = ref(true)

const weekdays = [t.weekdaySun, t.weekdayMon, t.weekdayTue, t.weekdayWed, t.weekdayThu, t.weekdayFri, t.weekdaySat]

const isReschedule = computed(() => rescheduleId.value > 0)

const canSubmit = computed(() => {
  if (!agreed.value || submitting.value) return false
  if (isReschedule.value) return true
  return !!membership.value && membership.value.remaining_times > 0
})

function getOptions() {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1]
  return (current as any).$page?.options || {}
}

function safeDecode(value: string) {
  if (!value) return ''
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

function formatDate(value: string) {
  if (!value) return '-'
  const date = new Date(value)
  return `${date.getMonth() + 1}${t.monthUnit}${date.getDate()}${t.dayUnit} ${weekdays[date.getDay()]}`
}

function formatDay(value: string) {
  if (!value) return '-'
  const date = new Date(value)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function formatTime(value: string) {
  if (!value) return '--:--'
  if (value.includes('T')) {
    const date = new Date(value)
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  }
  return value.slice(0, 5)
}

function normalizeMembership(raw: any): Membership {
  return {
    id: Number(raw.id || 0),
    status: String(raw.status || ''),
    remaining_times: Number(raw.remaining_times || 0),
    expire_date: raw.expire_date || null,
    card_name: raw.card_name,
    card: raw.card
  }
}

async function loadMembership() {
  membershipLoading.value = true
  try {
    const response = await membershipApi.list()
    const list = (Array.isArray(response) ? response : response?.items || []).map(normalizeMembership)

    const active = list.filter((item) => item.status === 'active' && item.remaining_times > 0)
    active.sort((a, b) => {
      if (!a.expire_date && !b.expire_date) return 0
      if (!a.expire_date) return 1
      if (!b.expire_date) return -1
      return a.expire_date.localeCompare(b.expire_date)
    })

    membership.value = active[0] || null
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadMembershipFail, icon: 'none' })
  } finally {
    membershipLoading.value = false
  }
}

function toggleAgreement() {
  agreed.value = !agreed.value
}

function goToPurchase() {
  uni.navigateTo({ url: '/pages/membership/index' })
}

function viewAgreement() {
  uni.showModal({
    title: t.bookingRules,
    content: t.bookingRulesDesc,
    showCancel: false
  })
}

async function submitBooking() {
  if (!canSubmit.value) return

  submitting.value = true
  try {
    if (isReschedule.value) {
      await bookingApi.reschedule(rescheduleId.value, {
        new_date: bookingDate.value,
        new_start_time: startTime.value,
        new_end_time: endTime.value
      })
    } else {
      await bookingApi.create({
        coach_id: coachId.value,
        booking_date: bookingDate.value,
        start_time: startTime.value,
        end_time: endTime.value,
        remark: remark.value || undefined
      })
    }

    uni.showToast({ title: isReschedule.value ? t.rescheduleSuccess : t.bookingSuccess, icon: 'success' })

    setTimeout(() => {
      uni.switchTab({ url: '/pages/schedule/index' })
    }, 1200)
  } catch (error: any) {
    uni.showToast({ title: error.message || (isReschedule.value ? t.rescheduleFail : t.bookingFail), icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const options = getOptions()

  coachId.value = Number(options.coachId || 0)
  rescheduleId.value = Number(options.rescheduleId || 0)
  coachName.value = safeDecode(options.coachName || '')
  bookingDate.value = options.date || ''
  startTime.value = safeDecode(options.startTime || '')
  endTime.value = safeDecode(options.endTime || '')

  try {
    if (!isReschedule.value) {
      await loadMembership()
    }
  } finally {
    initialLoading.value = false
  }
})
</script>

<style lang="scss" scoped>
:root {
  --c-primary-start: #ffc04d;
  --c-primary-end: #ff9024;
  --c-text-main: #1d2129;
  --c-text-sub: #86909c;
  --c-bg-page: #f7f8fa;
}

.confirm-page {
  min-height: 100vh;
  background: var(--c-bg-page);
  padding: 24rpx;
  padding-bottom: 220rpx;
}

.hero-card,
.card {
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.04);
  padding: 20rpx;
  margin-bottom: 14rpx;
  animation: fadeInUp 0.35s ease-out;
}

.hero-card {
  position: relative;
  background: radial-gradient(circle at top right, #ffc760 0%, #ff9424 72%);
  overflow: hidden;
}

.hero-card::after {
  content: '';
  position: absolute;
  left: 20rpx;
  right: 20rpx;
  bottom: 12rpx;
  height: 2rpx;
  background: repeating-linear-gradient(to right, rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0.35) 10rpx, transparent 10rpx, transparent 16rpx);
}

.hero-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
}

.hero-sub {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.92);
}

.hero-row {
  margin-top: 12rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.15);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  padding: 12rpx 14rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hero-label {
  font-size: 23rpx;
  color: rgba(255, 255, 255, 0.88);
}

.hero-value {
  font-size: 24rpx;
  color: #fff;
  font-weight: 700;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.card-sub {
  font-size: 22rpx;
  color: #99a2b5;
}

.membership {
  border-radius: 18rpx;
  background: linear-gradient(135deg, #2e3344 0%, #1a1d26 100%);
  padding: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.membership-main {
  flex: 1;
}

.membership-name {
  display: block;
  font-size: 27rpx;
  font-weight: 700;
  color: #f2d8b0;
}

.membership-expire {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: rgba(242, 216, 176, 0.68);
}

.membership-count {
  font-size: 30rpx;
  font-weight: 700;
  background: linear-gradient(to bottom, #ffe8c8, #e6c28a);
  -webkit-background-clip: text;
  color: transparent;
}

.membership-skeleton {
  height: 126rpx;
  border-radius: 18rpx;
}

.membership-empty {
  border-radius: 16rpx;
  background: #fff1ef;
  padding: 14rpx;
}

.empty-title {
  display: block;
  font-size: 26rpx;
  color: #d05749;
}

.empty-sub {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #a78682;
}

.buy-btn {
  margin-top: 12rpx;
  width: 180rpx;
  height: 66rpx;
  line-height: 66rpx;
  border: none;
  border-radius: 999rpx;
  background: #ff9640;
  color: #fff;
  font-size: 24rpx;
}

.buy-btn::after {
  border: none;
}

.remark-input {
  width: 100%;
  min-height: 150rpx;
  border-radius: 16rpx;
  background: #f7f8fc;
  padding: 14rpx;
  box-sizing: border-box;
  font-size: 24rpx;
  color: #2b3448;
}

.notice-line {
  font-size: 24rpx;
  color: #616b82;
  line-height: 1.8;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 16rpx 20rpx calc(16rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 -8rpx 24rpx rgba(30, 36, 50, 0.08);
}

.agreement-row {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
  padding: 10rpx 0;
}

.agreement-check {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  border: 2rpx solid #c5ccdb;
  color: transparent;
  font-size: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  margin-right: 10rpx;
}

.agreement-check.active {
  border-color: var(--c-primary-end);
  background: var(--c-primary-end);
  color: #fff;
  transform: scale(1.08);
}

.agreement-text {
  font-size: 23rpx;
  color: #69748d;
}

.agreement-link {
  font-size: 23rpx;
  color: #df7f17;
  margin-left: auto;
}

.submit-btn {
  width: 100%;
  height: 84rpx;
  border: none;
  border-radius: 20rpx;
  background: linear-gradient(135deg, var(--c-primary-start), var(--c-primary-end));
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 12rpx 32rpx rgba(255, 144, 36, 0.16);
}

.submit-btn::after {
  border: none;
}

.submit-btn[disabled] {
  background: #d6dbe6;
  box-shadow: none;
}

.btn-hover {
  transform: scale(0.98);
  opacity: 0.95;
}

.skeleton-group {
  animation: fadeInUp 0.2s ease-out;
}

.skeleton-hero,
.skeleton-card {
  border-radius: 24rpx;
  margin-bottom: 14rpx;
}

.skeleton-hero {
  height: 240rpx;
}

.skeleton-card {
  height: 220rpx;
}

.shimmer {
  background: linear-gradient(90deg, #f0f2f5 25%, #e6e8eb 37%, #f0f2f5 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}

@keyframes shimmer {
  0% {
    background-position: -100% 0;
  }
  100% {
    background-position: 100% 0;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
