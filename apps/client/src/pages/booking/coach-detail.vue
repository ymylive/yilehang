<template>
  <view class="coach-detail-page">
    <view v-if="initialLoading" class="skeleton-group">
      <view class="skeleton-header shimmer"></view>
      <view class="skeleton-stats shimmer"></view>
      <view class="skeleton-review shimmer"></view>
    </view>

    <view v-else>
      <view class="hero-card" v-if="coach">
        <image :src="coach.avatar || '/static/default-avatar.png'" class="hero-avatar" mode="aspectFill" />

        <view class="hero-main">
          <view class="hero-head">
            <text class="coach-name">{{ coach.name }}</text>
            <text class="coach-exp" v-if="coach.years_of_experience">{{ t.yearsLabel }} {{ coach.years_of_experience }} {{ t.yearUnit }}</text>
          </view>

          <view class="coach-tags" v-if="coach.specialty?.length">
            <text v-for="(item, index) in coach.specialty" :key="index" class="coach-tag">{{ item }}</text>
          </view>

          <view class="coach-intro" v-if="coach.introduction">{{ coach.introduction }}</view>
        </view>
      </view>

      <view class="hero-card hero-empty" v-else>
        <text class="coach-name">{{ t.coachLoadFailed }}</text>
        <text class="coach-intro">{{ t.backRetry }}</text>
      </view>

      <view class="stats-card" v-if="coach">
        <view class="stat-item">
          <text class="stat-value">{{ coach.avg_rating?.toFixed(1) || '0.0' }}</text>
          <text class="stat-label">{{ t.rating }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ coach.total_lessons || 0 }}</text>
          <text class="stat-label">{{ t.totalLessons }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ coach.total_students || 0 }}</text>
          <text class="stat-label">{{ t.students }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ coach.review_count || 0 }}</text>
          <text class="stat-label">{{ t.reviewCount }}</text>
        </view>
      </view>

      <view class="card" v-if="coach?.certificates?.length">
        <view class="card-head">
          <text class="card-title">{{ t.certificates }}</text>
        </view>
        <view class="cert-grid">
          <image
            v-for="(cert, index) in coach.certificates"
            :key="index"
            :src="cert"
            class="cert-image"
            mode="aspectFill"
            @click="previewImage(cert)"
          />
        </view>
      </view>

      <view class="card">
        <view class="card-head">
          <text class="card-title">{{ t.studentReviews }}</text>
          <text class="card-sub">{{ t.latestFive }}</text>
        </view>

        <view class="loading-box" v-if="reviewsLoading">{{ t.loadingReviews }}</view>

        <view class="review-list" v-else-if="reviews.length">
          <view class="review-item" v-for="item in reviews" :key="item.id">
            <view class="review-user">
              <image :src="item.student_avatar || '/static/default-avatar.png'" class="user-avatar" mode="aspectFill" />
              <view class="user-main">
                <text class="user-name">{{ item.is_anonymous ? t.anonymous : item.student_name || t.student }}</text>
                <text class="review-time">{{ formatDate(item.created_at) }}</text>
              </view>
              <text class="review-stars">{{ renderStars(item.rating) }}</text>
            </view>

            <text class="review-content" v-if="item.content">{{ item.content }}</text>

            <view class="review-tags" v-if="item.tags?.length">
              <text class="review-tag" v-for="(tag, index) in item.tags" :key="index">{{ tag }}</text>
            </view>
          </view>
        </view>

        <view class="review-empty" v-else>
          <text class="empty-title">{{ t.noReviews }}</text>
          <text class="empty-sub">{{ t.noReviewsSub }}</text>
        </view>
      </view>

      <view class="bottom-bar" v-if="coach">
        <view class="price-block">
          <text class="price-label">{{ t.priceLabel }}</text>
          <view class="price-line">
            <text class="price-currency">{{ t.currency }}</text>
            <text class="price-value" v-if="coach.hourly_rate">{{ coach.hourly_rate }}</text>
            <text class="price-value" v-else>{{ t.customPrice }}</text>
            <text class="price-unit">{{ t.perLesson }}</text>
          </view>
        </view>

        <button class="book-btn" hover-class="btn-hover" :hover-stay-time="60" @click="goToSelectTime">{{ t.bookNow }}</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { coachApi } from '@/api/index'

interface Coach {
  id: number
  coach_no: string
  name: string
  avatar: string | null
  specialty: string[] | null
  introduction: string | null
  certificates: string[] | null
  years_of_experience: number | null
  hourly_rate: number | null
  total_students: number
  total_lessons: number
  avg_rating: number
  review_count: number
}

interface Review {
  id: number
  rating: number
  content: string | null
  tags: string[] | null
  is_anonymous: boolean
  created_at: string
  student_name: string | null
  student_avatar: string | null
}

const t = {
  yearsLabel: '\u6559\u9f84',
  yearUnit: '\u5e74',
  coachLoadFailed: '\u6559\u7ec3\u4fe1\u606f\u52a0\u8f7d\u5931\u8d25',
  backRetry: '\u8bf7\u8fd4\u56de\u91cd\u8bd5',
  rating: '\u8bc4\u5206',
  totalLessons: '\u7d2f\u8ba1\u8bfe\u65f6',
  students: '\u670d\u52a1\u5b66\u5458',
  reviewCount: '\u8bc4\u4ef7\u6570',
  certificates: '\u8d44\u8d28\u8bc1\u4e66',
  studentReviews: '\u5b66\u5458\u8bc4\u4ef7',
  latestFive: '\u6700\u8fd1 5 \u6761',
  loadingReviews: '\u8bc4\u4ef7\u52a0\u8f7d\u4e2d...',
  anonymous: '\u533f\u540d\u5b66\u5458',
  student: '\u5b66\u5458',
  noReviews: '\u6682\u65e0\u8bc4\u4ef7',
  noReviewsSub: '\u5b8c\u6210\u8bfe\u7a0b\u540e\u4f1a\u5c55\u793a\u5b66\u5458\u53cd\u9988',
  priceLabel: '\u8bfe\u65f6\u4ef7\u683c',
  currency: '\u00a5',
  customPrice: '\u9762\u8bae',
  perLesson: '/ \u8bfe\u65f6',
  bookNow: '\u7acb\u5373\u9884\u7ea6',
  loadCoachFail: '\u52a0\u8f7d\u6559\u7ec3\u4fe1\u606f\u5931\u8d25',
  loadReviewsFail: '\u52a0\u8f7d\u8bc4\u4ef7\u5931\u8d25',
  coachNotFound: '\u6559\u7ec3\u4fe1\u606f\u4e0d\u5b58\u5728'
} as const

const coachId = ref(0)
const coach = ref<Coach | null>(null)
const reviews = ref<Review[]>([])
const initialLoading = ref(true)
const reviewsLoading = ref(false)

function getOptions() {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1]
  return (current as any).$page?.options || {}
}

function normalizeReviews(source: any): Review[] {
  const list = Array.isArray(source) ? source : source?.items || []
  return list.map((item: any) => ({
    id: Number(item.id || 0),
    rating: Number(item.rating || 0),
    content: item.content || null,
    tags: Array.isArray(item.tags) ? item.tags : null,
    is_anonymous: !!item.is_anonymous,
    created_at: item.created_at || '',
    student_name: item.student_name || null,
    student_avatar: item.student_avatar || null
  }))
}

function formatDate(value: string) {
  if (!value) return ''
  const date = new Date(value)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function renderStars(score: number) {
  const count = Math.max(0, Math.min(5, Math.round(score)))
  return `${'\u2605'.repeat(count)}${'\u2606'.repeat(5 - count)}`
}

function previewImage(url: string) {
  uni.previewImage({
    urls: coach.value?.certificates || [url],
    current: url
  })
}

function goToSelectTime() {
  uni.navigateTo({
    url: `/pages/booking/select-time?coachId=${coachId.value}`
  })
}

async function loadCoachDetail() {
  try {
    coach.value = await coachApi.get(coachId.value)
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadCoachFail, icon: 'none' })
  }
}

async function loadReviews() {
  reviewsLoading.value = true
  try {
    const response = await coachApi.getReviews(coachId.value, 1, 5)
    reviews.value = normalizeReviews(response)
  } catch (error: any) {
    reviews.value = []
    console.error(t.loadReviewsFail, error)
  } finally {
    reviewsLoading.value = false
  }
}

onMounted(async () => {
  const options = getOptions()
  coachId.value = Number(options.id || options.coachId || 0)

  if (!coachId.value) {
    uni.showToast({ title: t.coachNotFound, icon: 'none' })
    initialLoading.value = false
    return
  }

  try {
    await Promise.all([loadCoachDetail(), loadReviews()])
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

.coach-detail-page {
  min-height: 100vh;
  background: var(--c-bg-page);
  padding: 24rpx;
  padding-bottom: 220rpx;
}

.hero-card,
.stats-card,
.card {
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.04);
  margin-bottom: 14rpx;
  animation: fadeInUp 0.35s ease-out;
}

.hero-card {
  display: flex;
  padding: 20rpx;
}

.hero-empty {
  flex-direction: column;
}

.hero-avatar {
  width: 110rpx;
  height: 110rpx;
  border-radius: 26rpx;
  background: #f3f5fb;
  flex-shrink: 0;
  margin-right: 14rpx;
}

.hero-main {
  flex: 1;
  min-width: 0;
}

.hero-head {
  display: flex;
  align-items: baseline;
}

.coach-name {
  font-size: 33rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.coach-exp {
  font-size: 22rpx;
  color: #8f98ac;
  margin-left: 10rpx;
}

.coach-tags {
  margin-top: 10rpx;
}

.coach-tag {
  display: inline-block;
  border-radius: 999rpx;
  padding: 5rpx 12rpx;
  margin-right: 8rpx;
  margin-bottom: 8rpx;
  font-size: 21rpx;
  color: #fa8c16;
  background: #fff7e6;
  border: 1rpx solid rgba(250, 140, 22, 0.1);
}

.coach-intro {
  margin-top: 10rpx;
  font-size: 23rpx;
  line-height: 1.6;
  color: #616b82;
}

.stats-card {
  display: flex;
  padding: 18rpx 0;
}

.stat-item {
  flex: 1;
  text-align: center;
  position: relative;
}

.stat-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 20%;
  bottom: 20%;
  width: 2rpx;
  background: #f2f4f7;
}

.stat-value {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.stat-label {
  display: block;
  margin-top: 6rpx;
  font-size: 21rpx;
  color: #98a1b5;
}

.card {
  padding: 20rpx;
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
  color: #9aa2b5;
}

.cert-grid {
  display: flex;
  flex-wrap: wrap;
  margin-right: -8rpx;
}

.cert-image {
  width: calc(33.33% - 8rpx);
  height: 150rpx;
  border-radius: 14rpx;
  background: #f3f5fb;
  margin-right: 8rpx;
  margin-bottom: 8rpx;
}

.loading-box {
  border-radius: 16rpx;
  background: #f8f9fd;
  text-align: center;
  padding: 36rpx 12rpx;
  font-size: 23rpx;
  color: #8f98ac;
}

.review-item {
  padding: 22rpx 0;
  border-bottom: 2rpx solid #f7f8fa;
}

.review-item:last-child {
  border-bottom: none;
}

.review-user {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: 16rpx;
  background: #f0f3fa;
  margin-right: 10rpx;
}

.user-main {
  flex: 1;
  min-width: 0;
}

.user-name {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: #2b3448;
}

.review-time {
  display: block;
  margin-top: 6rpx;
  font-size: 21rpx;
  color: #99a2b5;
}

.review-stars {
  font-size: 22rpx;
  color: #f4a11f;
}

.review-content {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: #5e6880;
}

.review-tags {
  margin-top: 8rpx;
}

.review-tag {
  display: inline-block;
  border-radius: 999rpx;
  padding: 4rpx 10rpx;
  margin-right: 8rpx;
  margin-bottom: 6rpx;
  font-size: 20rpx;
  color: #8691a8;
  background: #edf1f7;
}

.review-empty {
  border-radius: 16rpx;
  background: #f8f9fd;
  text-align: center;
  padding: 36rpx 12rpx;
}

.empty-title {
  display: block;
  font-size: 26rpx;
  color: #4f5870;
}

.empty-sub {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #a0a8ba;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 14rpx 20rpx calc(14rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(14rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 -6rpx 16rpx rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
}

.price-block {
  min-width: 176rpx;
  margin-right: 12rpx;
}

.price-label {
  display: block;
  font-size: 21rpx;
  color: #9aa2b5;
}

.price-line {
  margin-top: 4rpx;
  display: flex;
  align-items: baseline;
}

.price-currency {
  font-size: 24rpx;
  color: #ff7d00;
  font-weight: 700;
  margin-right: 4rpx;
}

.price-value {
  font-size: 40rpx;
  font-weight: 800;
  color: #ff7d00;
}

.price-unit {
  margin-left: 6rpx;
  font-size: 21rpx;
  color: #9aa2b5;
}

.book-btn {
  flex: 1;
  height: 82rpx;
  border: none;
  border-radius: 20rpx;
  background: linear-gradient(135deg, var(--c-primary-start), var(--c-primary-end));
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 12rpx 32rpx rgba(255, 144, 36, 0.16);
}

.book-btn::after {
  border: none;
}

.btn-hover {
  transform: scale(0.98);
  opacity: 0.95;
}

.skeleton-header,
.skeleton-stats,
.skeleton-review {
  border-radius: 24rpx;
  margin-bottom: 14rpx;
}

.skeleton-header {
  height: 160rpx;
}

.skeleton-stats {
  height: 120rpx;
}

.skeleton-review {
  height: 320rpx;
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
