<template>
  <view class="income-page">
    <view class="hero">
      <view class="hero-glow" aria-hidden="true"></view>
      <view class="hero-content">
        <view class="hero-head">
          <view>
            <text class="hero-title">{{ t.incomeStats }}</text>
            <text class="hero-sub">{{ selectedMonth }} {{ t.incomeDetail }}</text>
          </view>
          <picker mode="date" fields="month" :value="selectedMonth" @change="onMonthChange">
            <view class="month-picker">
              <text>{{ selectedMonth }}</text>
              <text class="arrow">&gt;</text>
            </view>
          </picker>
        </view>

        <view class="hero-amount-wrap">
          <text class="hero-amount-label">{{ t.monthEstimateIncome }}</text>
          <view class="hero-amount-row">
            <text class="currency">{{ t.currencySymbol }}</text>
            <text class="hero-amount">{{ formatMoney(summary.this_month?.income) }}</text>
          </view>
        </view>

        <view class="hero-stats">
          <view class="hero-stat-item">
            <text class="hero-stat-value">{{ summary.this_month?.lessons || 0 }}</text>
            <text class="hero-stat-label">{{ t.monthLessons }}</text>
          </view>
          <view class="hero-stat-divider"></view>
          <view class="hero-stat-item">
            <text class="hero-stat-value">{{ t.currencySymbol }}{{ formatMoney(summary.hourly_rate) }}</text>
            <text class="hero-stat-label">{{ t.hourlyRate }}</text>
          </view>
          <view class="hero-stat-divider"></view>
          <view class="hero-stat-item">
            <text class="hero-stat-value">{{ formatPercent(summary.commission_rate) }}</text>
            <text class="hero-stat-label">{{ t.commissionRate }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="content">
      <view class="compare-grid">
        <view class="compare-card">
          <text class="compare-label">{{ t.lastMonthIncome }}</text>
          <text class="compare-value">{{ t.currencySymbol }}{{ formatMoney(summary.last_month?.income) }}</text>
          <text class="compare-meta">{{ summary.last_month?.lessons || 0 }} {{ t.lessonUnit }}</text>
        </view>
        <view class="compare-card">
          <text class="compare-label">{{ t.totalIncome }}</text>
          <text class="compare-value highlight">{{ t.currencySymbol }}{{ formatMoney(summary.total?.income) }}</text>
          <text class="compare-meta">{{ summary.total?.lessons || 0 }} {{ t.lessonUnit }}</text>
        </view>
      </view>

      <view class="section-card">
        <view class="section-head">
          <text class="section-title">{{ t.incomeDetail }}</text>
          <text class="section-tip" v-if="incomeList.length">{{ t.totalPrefix }} {{ incomeList.length }} {{ t.totalSuffix }}</text>
        </view>

        <view v-if="loading && page === 1" class="state-wrap">
          <text class="state-text">{{ t.loading }}</text>
        </view>

        <view v-else-if="incomeList.length" class="list-wrap">
          <view v-for="item in incomeList" :key="item.id" class="income-item">
            <view class="item-main">
              <view class="item-top">
                <text class="student-name">{{ item.student_name }}</text>
                <text class="amount">+{{ t.currencySymbol }}{{ formatMoney(item.income) }}</text>
              </view>
              <view class="item-bottom">
                <text>{{ formatBookingTime(item.booking_date, item.start_time, item.end_time) }}</text>
              </view>
            </view>
          </view>

          <view class="load-more-wrap">
            <button v-if="hasMore && !loading" class="load-more-btn" @click="loadMore">{{ t.loadMore }}</button>
            <text v-else-if="loading" class="load-more-text">{{ t.loading }}</text>
            <text v-else class="load-more-text">{{ t.noMore }}</text>
          </view>
        </view>

        <view v-else class="state-wrap">
          <text class="state-text">{{ t.emptyMonthIncome }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { coachProfileApi } from '@/api/index'

interface IncomeSummary {
  this_month: { lessons: number; income: number }
  last_month: { lessons: number; income: number }
  total: { lessons: number; income: number }
  hourly_rate: number
  commission_rate: number
}

interface IncomeItem {
  id: number
  booking_date: string
  start_time: string
  end_time: string
  student_name: string
  income: number
}

const t = {
  incomeStats: '\u6536\u5165\u7edf\u8ba1',
  incomeDetail: '\u6536\u5165\u660e\u7ec6',
  monthEstimateIncome: '\u672c\u6708\u9884\u4f30\u6536\u5165',
  monthLessons: '\u672c\u6708\u8bfe\u65f6',
  hourlyRate: '\u8bfe\u65f6\u8d39',
  commissionRate: '\u63d0\u6210\u6bd4\u4f8b',
  lastMonthIncome: '\u4e0a\u6708\u6536\u5165',
  totalIncome: '\u7d2f\u8ba1\u6536\u5165',
  lessonUnit: '\u8282\u8bfe',
  totalPrefix: '\u5171',
  totalSuffix: '\u6761',
  loading: '\u52a0\u8f7d\u4e2d...',
  loadMore: '\u52a0\u8f7d\u66f4\u591a',
  noMore: '\u6ca1\u6709\u66f4\u591a\u4e86',
  emptyMonthIncome: '\u8be5\u6708\u4efd\u6682\u65e0\u6536\u5165\u8bb0\u5f55',
  loadFailed: '\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5',
  studentDefault: '\u5b66\u5458',
  monthUnit: '\u6708',
  dayUnit: '\u65e5',
  currencySymbol: '\u00a5'
} as const

const pageSize = 20
const selectedMonth = ref(formatMonth(new Date()))
const summary = ref<Partial<IncomeSummary>>({})
const incomeList = ref<IncomeItem[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

function formatMonth(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

function formatMoney(value: number | null | undefined): string {
  const num = Number(value || 0)
  return num.toFixed(2)
}

function formatPercent(value: number | null | undefined): string {
  return `${Math.round((value || 0) * 100)}%`
}

function normalizeTime(value: any): string {
  if (!value) return ''
  const text = String(value)
  if (text.includes('T')) {
    const d = new Date(text)
    if (Number.isNaN(d.getTime())) return text
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:00`
  }
  return text
}

function normalizeIncomeItem(raw: any, fallbackId: number): IncomeItem {
  return {
    id: Number(raw?.id || fallbackId),
    booking_date: String(raw?.booking_date || raw?.date || raw?.start_time || '').slice(0, 10),
    start_time: normalizeTime(raw?.start_time || raw?.start_at),
    end_time: normalizeTime(raw?.end_time || raw?.end_at),
    student_name: String(raw?.student_name || raw?.student?.name || t.studentDefault),
    income: Number(raw?.income ?? raw?.amount ?? 0)
  }
}

function normalizeIncomeList(data: any, offset = 0): IncomeItem[] {
  const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
  return list
    .map((raw, index) => normalizeIncomeItem(raw, offset + index + 1))
    .filter(item => item.booking_date || item.start_time)
}

function formatBookingTime(dateStr: string, start: string, end: string): string {
  const startText = start ? start.slice(0, 5) : '--:--'
  const endText = end ? end.slice(0, 5) : '--:--'

  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) {
    return `${startText}-${endText}`
  }

  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}${t.monthUnit}${day}${t.dayUnit} ${startText}-${endText}`
}

async function loadSummary() {
  try {
    const data = await coachProfileApi.getIncomeSummary()
    summary.value = data || {}
  } catch (error) {
    console.error('load income summary failed:', error)
  }
}

async function loadIncomeDetails(reset = false) {
  if (reset) {
    page.value = 1
    hasMore.value = true
    incomeList.value = []
  }
  if (!hasMore.value) return

  loading.value = true
  const currentPage = page.value
  try {
    const data = await coachProfileApi.getIncomeDetails({
      month: selectedMonth.value,
      page: currentPage,
      page_size: pageSize
    })

    const items = normalizeIncomeList(data, (currentPage - 1) * pageSize)
    if (reset) {
      incomeList.value = items
    } else {
      incomeList.value.push(...items)
    }

    hasMore.value = items.length >= pageSize
    if (hasMore.value) {
      page.value = currentPage + 1
    }
  } catch (error) {
    console.error('load income details failed:', error)
    uni.showToast({ title: t.loadFailed, icon: 'none' })
  } finally {
    loading.value = false
    uni.stopPullDownRefresh()
  }
}

function onMonthChange(e: any) {
  selectedMonth.value = e.detail.value
  loadIncomeDetails(true)
}

function loadMore() {
  if (loading.value || !hasMore.value) return
  loadIncomeDetails(false)
}

onReachBottom(() => {
  loadMore()
})

onPullDownRefresh(() => {
  Promise.all([loadSummary(), loadIncomeDetails(true)]).finally(() => {
    uni.stopPullDownRefresh()
  })
})

onMounted(() => {
  loadSummary()
  loadIncomeDetails(true)
})
</script>

<style lang="scss" scoped>
.income-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding-bottom: calc(120rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #ffbc47 0%, #ff8d1f 72%);
  border-radius: 0 0 44rpx 44rpx;
  padding: 32rpx 30rpx 106rpx;
}

.hero-glow {
  position: absolute;
  top: -120rpx;
  right: -140rpx;
  width: 360rpx;
  height: 360rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 244, 214, 0.92) 0%, rgba(255, 187, 80, 0.42) 48%, rgba(255, 146, 23, 0.04) 78%);
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
}

.hero-sub {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.88);
}

.month-picker {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 22rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.arrow {
  font-size: 20rpx;
}

.hero-amount-wrap {
  margin-top: 26rpx;
}

.hero-amount-label {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  font-size: 24rpx;
}

.hero-amount-row {
  margin-top: 8rpx;
  display: flex;
  align-items: baseline;
}

.currency {
  font-size: 34rpx;
  color: #fff;
}

.hero-amount {
  margin-left: 8rpx;
  font-size: 66rpx;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  letter-spacing: 1rpx;
}

.hero-stats {
  margin-top: 24rpx;
  background: rgba(255, 255, 255, 0.14);
  border: 1rpx solid rgba(255, 255, 255, 0.24);
  border-radius: 22rpx;
  padding: 20rpx 0;
  display: flex;
  align-items: center;
}

.hero-stat-item {
  flex: 1;
  text-align: center;
}

.hero-stat-value {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #fff;
  font-variant-numeric: tabular-nums;
}

.hero-stat-label {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.85);
}

.hero-stat-divider {
  width: 2rpx;
  height: 38rpx;
  background: rgba(255, 255, 255, 0.28);
}

.content {
  margin-top: -58rpx;
  position: relative;
  z-index: 3;
  padding: 0 24rpx;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14rpx;
}

.compare-card {
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 22rpx rgba(31, 37, 51, 0.06);
  padding: 20rpx;
}

.compare-label {
  display: block;
  font-size: 22rpx;
  color: #8992a6;
}

.compare-value {
  display: block;
  margin-top: 8rpx;
  font-size: 34rpx;
  line-height: 1.2;
  font-weight: 800;
  color: #1f2533;
  font-variant-numeric: tabular-nums;
}

.compare-value.highlight {
  color: #e7891e;
}

.compare-meta {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: #9aa2b5;
}

.section-card {
  margin-top: 16rpx;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 12rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 24rpx;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14rpx;
}

.section-title {
  font-size: 31rpx;
  font-weight: 700;
  color: #1f2533;
}

.section-tip {
  font-size: 22rpx;
  color: #8e97ab;
}

.state-wrap {
  padding: 48rpx 0;
  text-align: center;
}

.state-text {
  font-size: 24rpx;
  color: #99a1b2;
}

.list-wrap {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.income-item {
  border-radius: 18rpx;
  background: #fff9f0;
  border: 1rpx solid #ffe5c2;
  padding: 16rpx;
  transition: all 0.2s ease;
}

.income-item:active {
  transform: scale(0.99);
  background: #fff3e4;
}

.item-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.student-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1f2533;
}

.amount {
  font-size: 28rpx;
  font-weight: 700;
  color: #e48517;
  font-variant-numeric: tabular-nums;
}

.item-bottom {
  margin-top: 10rpx;
  font-size: 22rpx;
  color: #8d96ab;
}

.load-more-wrap {
  text-align: center;
  padding: 20rpx 0 6rpx;
}

.load-more-btn {
  display: inline-block;
  border: none;
  border-radius: 999rpx;
  padding: 12rpx 26rpx;
  font-size: 24rpx;
  color: #fff;
  background: linear-gradient(135deg, #ffbc47, #ff8d1f);
}

.load-more-btn::after {
  border: none;
}

.load-more-text {
  font-size: 22rpx;
  color: #9aa2b5;
}
</style>
