<template>
  <view class="booking-page">
    <view class="header-card">
      <wd-search v-model="searchKeyword" placeholder="搜索教练姓名" @search="handleSearch" />
      <scroll-view scroll-x class="tag-scroll" :show-scrollbar="false">
        <view
          v-for="tag in specialtyTags"
          :key="tag.value"
          :class="['tag-item', { active: selectedTag === tag.value }]"
          @click="selectTag(tag.value)"
        >
          <image :src="tag.icon" class="tag-icon" mode="aspectFit" />
          <text>{{ tag.label }}</text>
        </view>
      </scroll-view>
    </view>

    <view class="coach-list" v-if="displayCoaches.length">
      <view class="coach-card" v-for="coach in displayCoaches" :key="coach.id" @click="goToCoachDetail(coach.id)">
        <image :src="coach.avatar || '/static/default-avatar.png'" class="coach-avatar" mode="aspectFill" />

        <view class="coach-main">
          <view class="coach-head">
            <text class="coach-name">{{ coach.name }}</text>
            <text class="coach-price" v-if="coach.hourly_rate">¥{{ coach.hourly_rate }}/课时</text>
          </view>

          <view class="coach-tags" v-if="coach.specialty?.length">
            <text v-for="(s, i) in coach.specialty.slice(0, 3)" :key="i" class="coach-tag">{{ s }}</text>
          </view>

          <view class="coach-stats">
            <text>评分 {{ coach.avg_rating.toFixed(1) }}</text>
            <text>课时 {{ coach.total_lessons }}</text>
            <text>学员 {{ coach.total_students }}</text>
          </view>
        </view>

        <view class="coach-action">
          <button class="book-btn" @click.stop="goToSelectTime(coach.id)">立即预约</button>
        </view>
      </view>

      <view class="load-more-wrap">
        <button v-if="hasMore && !loading" class="load-more-btn" @click="loadMore">加载更多</button>
        <text v-else-if="loading" class="load-more-text">加载中...</text>
        <text v-else class="load-more-text">没有更多了</text>
      </view>
    </view>

    <view class="empty-state" v-else-if="!loading">
      <view class="empty-icon">
        <image :src="emptyIcon" class="empty-icon-image" mode="aspectFit" />
      </view>
      <text class="empty-title">暂无匹配教练</text>
      <text class="empty-sub">试试切换标签或清空关键词</text>
    </view>

    <view class="loading-state" v-else>
      <text>加载中...</text>
    </view>
  <DynamicTabBar />
</view>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import { computed, ref, onMounted } from 'vue'
import { onReachBottom } from '@dcloudio/uni-app'
import { coachApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

interface Coach {
  id: number
  coach_no: string
  name: string
  avatar: string | null
  specialty: string[] | null
  introduction: string | null
  years_of_experience: number | null
  hourly_rate: number | null
  total_students: number
  total_lessons: number
  avg_rating: number
  review_count: number
}

const searchKeyword = ref('')
const selectedTag = ref('')
const coaches = ref<Coach[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const hasMore = ref(true)
const emptyIcon = getSemanticIcon('booking-empty')

const specialtyTags = [
  { label: '全部', value: '', icon: '/static/sports/all.svg' },
  { label: '篮球', value: '篮球', icon: '/static/sports/basketball.svg' },
  { label: '足球', value: '足球', icon: '/static/sports/football.svg' },
  { label: '游泳', value: '游泳', icon: '/static/sports/swimming.svg' },
  { label: '跆拳道', value: '跆拳道', icon: '/static/sports/taekwondo.svg' },
  { label: '舞蹈', value: '舞蹈', icon: '/static/sports/dance.svg' },
  { label: '体操', value: '体操', icon: '/static/sports/gymnastics.svg' }
]

const displayCoaches = computed(() => {
  const key = searchKeyword.value.trim().toLowerCase()
  if (!key) return coaches.value
  return coaches.value.filter(item => item.name.toLowerCase().includes(key))
})

async function loadCoaches(reset = false) {
  if (loading.value) return
  if (reset) {
    page.value = 1
    hasMore.value = true
    coaches.value = []
  }
  if (!hasMore.value) return

  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize
    }
    if (selectedTag.value) {
      params.specialty = selectedTag.value
    }

    const data = await coachApi.list(params)
    const list = Array.isArray(data) ? data : data?.items || []

    if (reset) {
      coaches.value = list
    } else {
      coaches.value = [...coaches.value, ...list]
    }

    hasMore.value = list.length >= pageSize
    if (hasMore.value) {
      page.value += 1
    }
  } catch (error: any) {
    uni.showToast({ title: error.message || '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // local filter by computed
}

function selectTag(tag: string) {
  selectedTag.value = tag
  loadCoaches(true)
}

function goToCoachDetail(coachId: number) {
  uni.navigateTo({ url: `/pages/booking/coach-detail?id=${coachId}` })
}

function goToSelectTime(coachId: number) {
  uni.navigateTo({ url: `/pages/booking/select-time?coachId=${coachId}` })
}

function loadMore() {
  if (loading.value || !hasMore.value) return
  loadCoaches(false)
}

onReachBottom(() => {
  loadMore()
})

onMounted(() => {
  loadCoaches(true)
})
</script>

<style lang="scss" scoped>
.booking-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.header-card {
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 18rpx;
}

.tag-scroll {
  margin-top: 12rpx;
  white-space: nowrap;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 56rpx;
  border-radius: 999rpx;
  padding: 0 20rpx;
  margin-right: 10rpx;
  background: #f4f6fb;
  color: #7f879a;
  font-size: 22rpx;
  gap: 6rpx;
}

.tag-icon {
  width: 26rpx;
  height: 26rpx;
}

.tag-item.active {
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  color: #fff;
  font-weight: 700;
}

.coach-list {
  margin-top: 14rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.coach-card {
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 18rpx;
  display: flex;
  gap: 14rpx;
}

.coach-card:active {
  transform: translateY(2rpx);
}

.coach-avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 24rpx;
  background: #f4f6fb;
  flex-shrink: 0;
}

.coach-main {
  flex: 1;
  min-width: 0;
}

.coach-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8rpx;
}

.coach-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2533;
}

.coach-price {
  font-size: 22rpx;
  color: #de7f16;
}

.coach-tags {
  margin-top: 10rpx;
  display: flex;
  gap: 8rpx;
  flex-wrap: wrap;
}

.coach-tag {
  border-radius: 999rpx;
  padding: 4rpx 10rpx;
  font-size: 20rpx;
  color: #8b93a8;
  background: #f4f6fb;
}

.coach-stats {
  margin-top: 10rpx;
  display: flex;
  gap: 14rpx;
  font-size: 22rpx;
  color: #8e97aa;
}

.coach-action {
  display: flex;
  align-items: flex-end;
}

.book-btn {
  border: none;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  color: #fff;
  font-size: 22rpx;
  font-weight: 700;
  padding: 10rpx 18rpx;
  line-height: 1;
}

.book-btn::after {
  border: none;
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

.empty-state,
.loading-state {
  margin-top: 14rpx;
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 56rpx 24rpx;
  text-align: center;
}

.empty-icon {
  width: 88rpx;
  height: 88rpx;
  margin: 0 auto;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #fff1dd, #ffdcb9);
  color: #ff8d1f;
  font-size: 36rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon-image {
  width: 56rpx;
  height: 56rpx;
}

.empty-title {
  display: block;
  margin-top: 16rpx;
  font-size: 28rpx;
  color: #4f5870;
}

.empty-sub {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #99a1b2;
}

.loading-state {
  font-size: 24rpx;
  color: #99a1b2;
}
</style>
