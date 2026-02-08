<template>
  <view class="reviews-page">
    <view class="hero">
      <view class="hero-glow" aria-hidden="true"></view>
      <view class="hero-content">
        <text class="hero-title">{{ t.reviewCenter }}</text>
        <text class="hero-sub">{{ t.reviewSub }}</text>
        <view class="hero-stats">
          <view class="hero-stat-item">
            <text class="hero-stat-value">{{ reviews.length }}</text>
            <text class="hero-stat-label">{{ t.filterAll }}</text>
          </view>
          <view class="hero-stat-divider"></view>
          <view class="hero-stat-item">
            <text class="hero-stat-value">{{ unrepliedCount }}</text>
            <text class="hero-stat-label">{{ t.filterUnreplied }}</text>
          </view>
          <view class="hero-stat-divider"></view>
          <view class="hero-stat-item">
            <text class="hero-stat-value">{{ repliedCount }}</text>
            <text class="hero-stat-label">{{ t.filterReplied }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="content">
      <view class="filter-card">
        <view
          v-for="item in filters"
          :key="item.key"
          :class="['filter-pill', { active: currentFilter === item.key }]"
          @click="currentFilter = item.key"
        >
          <text>{{ item.label }}</text>
          <text v-if="item.key === 'unreplied' && unrepliedCount" class="dot"></text>
        </view>
      </view>

      <view v-if="loading && page === 1" class="state-wrap">
        <text class="state-text">{{ t.loading }}</text>
      </view>

      <view v-else-if="filteredReviews.length" class="review-list">
        <view v-for="review in filteredReviews" :key="review.id" class="review-card">
          <view class="review-head">
            <view class="user">
              <view class="avatar">{{ (review.is_anonymous ? t.avatarAnonymous : (review.student_name || t.studentShort).charAt(0)) }}</view>
              <view class="user-meta">
                <text class="name">{{ review.is_anonymous ? t.anonymousStudent : (review.student_name || t.studentDefault) }}</text>
                <text class="time">{{ formatDateTime(review.created_at) }}</text>
              </view>
            </view>
            <view class="rating">
              <view class="stars">
                <text
                  v-for="(active, starIdx) in getStarStates(review.rating)"
                  :key="`${review.id}-${starIdx}`"
                  :class="['star', { active }]"
                >{{ t.star }}</text>
              </view>
              <text class="score">{{ review.rating.toFixed(1) }}</text>
            </view>
          </view>

          <view class="content-block">
            <text class="content-text">{{ review.content || t.emptyReviewText }}</text>
            <view v-if="review.tags.length" class="tags">
              <text v-for="tag in review.tags" :key="tag" class="tag">{{ tag }}</text>
            </view>
          </view>

          <view v-if="review.reply" class="reply-block">
            <text class="reply-label">{{ t.myReply }}</text>
            <text class="reply-content">{{ review.reply }}</text>
          </view>

          <view v-else class="reply-editor">
            <textarea
              v-if="replyingReviewId === review.id"
              class="reply-input"
              v-model="replyDraft"
              maxlength="200"
              :placeholder="t.replyPlaceholder"
            />
            <view class="reply-actions">
              <button
                v-if="replyingReviewId === review.id"
                class="btn ghost"
                @click="cancelReply"
              >{{ t.cancel }}</button>
              <button
                v-if="replyingReviewId === review.id"
                class="btn primary"
                :disabled="submitting"
                @click="submitReply(review)"
              >{{ submitting ? t.submitting : t.submitReply }}</button>
              <button
                v-else
                class="btn outline"
                @click="startReply(review)"
              >{{ t.replyReview }}</button>
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
        <text class="state-text">{{ t.noMatched }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { coachReviewApi } from '@/api/index'

type FilterType = 'all' | 'unreplied' | 'replied'

interface ReviewItem {
  id: number
  student_name: string
  is_anonymous: boolean
  rating: number
  content: string
  tags: string[]
  created_at: string
  reply: string
  reply_at: string
}

const t = {
  reviewCenter: '\u8bc4\u4ef7\u4e2d\u5fc3',
  reviewSub: '\u67e5\u770b\u5b66\u5458\u8bc4\u4ef7\u5e76\u53ca\u65f6\u56de\u590d',
  filterAll: '\u5168\u90e8',
  filterUnreplied: '\u672a\u56de\u590d',
  filterReplied: '\u5df2\u56de\u590d',
  loading: '\u52a0\u8f7d\u4e2d...',
  avatarAnonymous: '\u533f',
  studentShort: '\u5b66',
  anonymousStudent: '\u533f\u540d\u5b66\u5458',
  studentDefault: '\u5b66\u5458',
  star: '\u2605',
  emptyReviewText: '\u8be5\u5b66\u5458\u672a\u586b\u5199\u6587\u5b57\u8bc4\u4ef7\u3002',
  myReply: '\u6211\u7684\u56de\u590d',
  replyPlaceholder: '\u5199\u4e0b\u4f60\u7684\u56de\u590d\uff0c\u5efa\u8bae\u79ef\u6781\u4e14\u5177\u4f53\u3002',
  cancel: '\u53d6\u6d88',
  submitting: '\u63d0\u4ea4\u4e2d...',
  submitReply: '\u63d0\u4ea4\u56de\u590d',
  replyReview: '\u56de\u590d\u8bc4\u4ef7',
  loadMore: '\u52a0\u8f7d\u66f4\u591a',
  noMore: '\u6ca1\u6709\u66f4\u591a\u4e86',
  noMatched: '\u6682\u65e0\u5339\u914d\u8bc4\u4ef7',
  monthUnit: '\u6708',
  dayUnit: '\u65e5',
  loadReviewsFailed: '\u83b7\u53d6\u8bc4\u4ef7\u5931\u8d25',
  replyContentRequired: '\u8bf7\u8f93\u5165\u56de\u590d\u5185\u5bb9',
  replySuccess: '\u56de\u590d\u6210\u529f',
  replyFailed: '\u56de\u590d\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5'
} as const

const pageSize = 20
const page = ref(1)
const hasMore = ref(true)
const loading = ref(false)
const submitting = ref(false)
const reviews = ref<ReviewItem[]>([])
const currentFilter = ref<FilterType>('all')
const replyingReviewId = ref<number | null>(null)
const replyDraft = ref('')

const filters: Array<{ key: FilterType; label: string }> = [
  { key: 'all', label: t.filterAll },
  { key: 'unreplied', label: t.filterUnreplied },
  { key: 'replied', label: t.filterReplied }
]

const filteredReviews = computed(() => {
  if (currentFilter.value === 'unreplied') {
    return reviews.value.filter(item => !item.reply)
  }
  if (currentFilter.value === 'replied') {
    return reviews.value.filter(item => !!item.reply)
  }
  return reviews.value
})

const unrepliedCount = computed(() => reviews.value.filter(item => !item.reply).length)
const repliedCount = computed(() => reviews.value.filter(item => !!item.reply).length)

function toArray(value: unknown): string[] {
  if (Array.isArray(value)) return value.filter(item => typeof item === 'string') as string[]
  if (typeof value === 'string' && value.trim()) {
    const text = value.trim()
    if (text.startsWith('[') && text.endsWith(']')) {
      try {
        const parsed = JSON.parse(text)
        if (Array.isArray(parsed)) {
          return parsed.filter(item => typeof item === 'string') as string[]
        }
      } catch {
        return [text]
      }
    }
    return [text]
  }
  return []
}

function normalizeReview(raw: any): ReviewItem {
  return {
    id: Number(raw?.id || 0),
    student_name: String(raw?.student_name || raw?.student?.name || t.studentDefault),
    is_anonymous: Boolean(raw?.is_anonymous),
    rating: Number(raw?.rating || 0),
    content: String(raw?.content || ''),
    tags: toArray(raw?.tags),
    created_at: String(raw?.created_at || ''),
    reply: String(raw?.coach_reply || raw?.reply || ''),
    reply_at: String(raw?.coach_reply_at || raw?.reply_at || '')
  }
}

function normalizeList(data: any): ReviewItem[] {
  const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
  return list.map(normalizeReview).filter(item => item.id > 0)
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return '--'
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${month}${t.monthUnit}${day}${t.dayUnit} ${hour}:${minute}`
}

function getStarStates(rating: number): boolean[] {
  const round = Math.max(0, Math.min(5, Math.round(rating)))
  return Array.from({ length: 5 }, (_, index) => index < round)
}

async function loadReviews(reset = false) {
  if (reset) {
    page.value = 1
    hasMore.value = true
    reviews.value = []
  }
  if (!hasMore.value) return

  loading.value = true
  const currentPage = page.value
  try {
    const data = await coachReviewApi.getMyReviews({
      page: currentPage,
      page_size: pageSize
    })

    const items = normalizeList(data)
    if (reset) {
      reviews.value = items
    } else {
      const existing = new Set(reviews.value.map(item => item.id))
      const incoming = items.filter(item => !existing.has(item.id))
      reviews.value.push(...incoming)
    }

    hasMore.value = items.length >= pageSize
    if (hasMore.value) {
      page.value = currentPage + 1
    }
  } catch (error) {
    console.error('load reviews failed:', error)
    uni.showToast({ title: t.loadReviewsFailed, icon: 'none' })
  } finally {
    loading.value = false
    uni.stopPullDownRefresh()
  }
}

function startReply(review: ReviewItem) {
  replyingReviewId.value = review.id
  replyDraft.value = ''
}

function cancelReply() {
  replyingReviewId.value = null
  replyDraft.value = ''
}

async function submitReply(review: ReviewItem) {
  const content = replyDraft.value.trim()
  if (!content) {
    uni.showToast({ title: t.replyContentRequired, icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await coachReviewApi.replyReview(review.id, content)
    const target = reviews.value.find(item => item.id === review.id)
    if (target) {
      target.reply = content
      target.reply_at = new Date().toISOString()
    }
    cancelReply()
    uni.showToast({ title: t.replySuccess, icon: 'success' })
  } catch (error) {
    console.error('submit review reply failed:', error)
    uni.showToast({ title: t.replyFailed, icon: 'none' })
  } finally {
    submitting.value = false
  }
}

function loadMore() {
  if (loading.value || !hasMore.value) return
  loadReviews(false)
}

onReachBottom(() => {
  loadMore()
})

onPullDownRefresh(() => {
  loadReviews(true)
})

onMounted(() => {
  loadReviews(true)
})
</script>

<style lang="scss" scoped>
.reviews-page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: calc(120rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #ffbc47 0%, #ff8d1f 72%);
  border-radius: 0 0 44rpx 44rpx;
  padding: 30rpx 28rpx 100rpx;
  animation: fadeUp 0.3s ease-out;
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
  color: rgba(255, 255, 255, 0.9);
}

.hero-stats {
  margin-top: 22rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.14);
  border: 1rpx solid rgba(255, 255, 255, 0.24);
  display: flex;
  align-items: center;
  padding: 20rpx 0;
}

.hero-stat-item {
  flex: 1;
  text-align: center;
}

.hero-stat-value {
  display: block;
  font-size: 32rpx;
  font-weight: 800;
  color: #fff;
}

.hero-stat-label {
  display: block;
  margin-top: 8rpx;
  font-size: 21rpx;
  color: rgba(255, 255, 255, 0.85);
}

.hero-stat-divider {
  width: 2rpx;
  height: 38rpx;
  background: rgba(255, 255, 255, 0.28);
}

.content {
  margin-top: -56rpx;
  padding: 0 22rpx;
  position: relative;
  z-index: 3;
}

.filter-card {
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  padding: 14rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10rpx;
  animation: fadeUp 0.4s ease-out 0.1s both;
}

.filter-pill {
  height: 64rpx;
  border-radius: 18rpx;
  background: #f6f8fc;
  color: #7f879a;
  font-size: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.filter-pill.active {
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  color: #fff;
  font-weight: 700;
}

.dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background: #ff4f4f;
  position: absolute;
  top: 14rpx;
  right: 20rpx;
}

.review-list {
  margin-top: 14rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.review-card {
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  padding: 20rpx;
  transition: all 0.2s ease;
  animation: fadeUp 0.4s ease-out;
  animation-fill-mode: both;
}

.review-card:nth-child(1) { animation-delay: 0.15s; }
.review-card:nth-child(2) { animation-delay: 0.2s; }
.review-card:nth-child(3) { animation-delay: 0.25s; }
.review-card:nth-child(4) { animation-delay: 0.3s; }

.review-card:active {
  transform: scale(0.995);
}

.review-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10rpx;
}

.user {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #ffbf5e, #ff8f1f);
  color: #fff;
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1f2533;
}

.time {
  font-size: 21rpx;
  color: #8f98ad;
}

.rating {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6rpx;
}

.stars {
  display: flex;
  align-items: center;
  gap: 3rpx;
}

.star {
  font-size: 21rpx;
  color: #e5e6eb;
}

.star.active {
  color: #f3a11d;
}

.score {
  font-size: 24rpx;
  font-weight: 700;
  color: #e2871a;
}

.content-block {
  margin-top: 14rpx;
}

.content-text {
  font-size: 25rpx;
  line-height: 1.6;
  color: #4a5368;
}

.tags {
  margin-top: 10rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.tag {
  border-radius: 999rpx;
  padding: 4rpx 10rpx;
  font-size: 20rpx;
  color: #8b93a8;
  background: #f4f6fb;
}

.reply-block {
  margin-top: 14rpx;
  border-radius: 14rpx;
  background: #FFF7ED;
  padding: 14rpx;
}

.reply-label {
  display: block;
  font-size: 21rpx;
  color: #de7f16;
}

.reply-content {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #4f5870;
  line-height: 1.6;
}

.reply-editor {
  margin-top: 14rpx;
}

.reply-input {
  width: 100%;
  min-height: 136rpx;
  border-radius: 14rpx;
  background: #f7f8fb;
  border: 2rpx solid #e5e6eb;
  padding: 16rpx;
  font-size: 24rpx;
  color: #3d465d;
  box-sizing: border-box;
}

.reply-input:focus {
  border-color: #ff8d1f;
  background: #fffefb;
}

.reply-actions {
  margin-top: 10rpx;
  display: flex;
  justify-content: flex-end;
  gap: 10rpx;
}

.btn {
  border: none;
  border-radius: 999rpx;
  padding: 12rpx 24rpx;
  font-size: 22rpx;
  line-height: 1;
}

.btn::after {
  border: none;
}

.btn.primary {
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  color: #fff;
}

.btn.ghost {
  background: #eff2f7;
  color: #6d768c;
}

.btn.outline {
  background: #fff;
  color: #df7f17;
  border: 2rpx solid #ffd3a2;
}

.btn[disabled] {
  opacity: 0.6;
}

.btn:active {
  transform: scale(0.97);
}

.state-wrap {
  margin-top: 14rpx;
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 52rpx 24rpx;
  text-align: center;
}

.state-text {
  font-size: 24rpx;
  color: #99a1b2;
}

.load-more-wrap {
  text-align: center;
  padding: 10rpx 0 4rpx;
}

.load-more-btn {
  display: inline-block;
  border: none;
  border-radius: 999rpx;
  padding: 12rpx 26rpx;
  font-size: 22rpx;
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

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
