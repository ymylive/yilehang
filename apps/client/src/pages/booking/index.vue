<template>
  <view class="booking-page">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索教练"
        @search="handleSearch"
      />
    </view>

    <!-- 筛选标签 -->
    <view class="filter-tags">
      <scroll-view scroll-x class="tags-scroll">
        <view
          v-for="tag in specialtyTags"
          :key="tag.value"
          :class="['tag-item', { active: selectedTag === tag.value }]"
          @click="selectTag(tag.value)"
        >
          {{ tag.label }}
        </view>
      </scroll-view>
    </view>

    <!-- 教练列表 -->
    <view class="coach-list">
      <view
        v-for="coach in coaches"
        :key="coach.id"
        class="coach-card"
        @click="goToCoachDetail(coach.id)"
      >
        <view class="coach-avatar">
          <image
            :src="coach.avatar || '/static/default-avatar.png'"
            mode="aspectFill"
          />
        </view>
        <view class="coach-info">
          <view class="coach-name">{{ coach.name }}</view>
          <view class="coach-specialty">
            <text v-for="(s, i) in (coach.specialty || []).slice(0, 3)" :key="i" class="specialty-tag">
              {{ s }}
            </text>
          </view>
          <view class="coach-stats">
            <view class="stat-item">
              <text class="stat-value">{{ coach.avg_rating.toFixed(1) }}</text>
              <text class="stat-label">评分</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ coach.total_lessons }}</text>
              <text class="stat-label">课时</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ coach.total_students }}</text>
              <text class="stat-label">学员</text>
            </view>
          </view>
        </view>
        <view class="coach-action">
          <view class="price" v-if="coach.hourly_rate">
            <text class="price-value">{{ coach.hourly_rate }}</text>
            <text class="price-unit">元/课时</text>
          </view>
          <wd-button size="small" type="primary" @click.stop="goToSelectTime(coach.id)">
            立即约课
          </wd-button>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="coaches.length === 0 && !loading" class="empty-state">
        <image src="/static/empty.png" mode="aspectFit" class="empty-image" />
        <text class="empty-text">暂无教练</text>
      </view>

      <!-- 加载更多 -->
      <view v-if="loading" class="loading-more">
        <wd-loading />
        <text>加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { coachApi } from '@/api'

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

const specialtyTags = [
  { label: '全部', value: '' },
  { label: '篮球', value: 'basketball' },
  { label: '足球', value: 'football' },
  { label: '游泳', value: 'swimming' },
  { label: '跆拳道', value: 'taekwondo' },
  { label: '舞蹈', value: 'dance' },
  { label: '体操', value: 'gymnastics' }
]

async function loadCoaches() {
  if (loading.value) return
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
    if (page.value === 1) {
      coaches.value = data
    } else {
      coaches.value = [...coaches.value, ...data]
    }
  } catch (error: any) {
    uni.showToast({ title: error.message || '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadCoaches()
}

function selectTag(tag: string) {
  selectedTag.value = tag
  page.value = 1
  loadCoaches()
}

function goToCoachDetail(coachId: number) {
  uni.navigateTo({
    url: `/pages/booking/coach-detail?id=${coachId}`
  })
}

function goToSelectTime(coachId: number) {
  uni.navigateTo({
    url: `/pages/booking/select-time?coachId=${coachId}`
  })
}

onMounted(() => {
  loadCoaches()
})
</script>

<style lang="scss" scoped>
.booking-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.search-bar {
  padding: 20rpx;
  background-color: #fff;
}

.filter-tags {
  background-color: #fff;
  padding: 0 20rpx 20rpx;

  .tags-scroll {
    white-space: nowrap;
  }

  .tag-item {
    display: inline-block;
    padding: 12rpx 28rpx;
    margin-right: 16rpx;
    background-color: #f5f5f5;
    border-radius: 30rpx;
    font-size: 26rpx;
    color: #666;

    &.active {
      background-color: #e8f5e9;
      color: #4caf50;
    }
  }
}

.coach-list {
  padding: 20rpx;
}

.coach-card {
  display: flex;
  background-color: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);

  .coach-avatar {
    width: 140rpx;
    height: 140rpx;
    border-radius: 12rpx;
    overflow: hidden;
    flex-shrink: 0;

    image {
      width: 100%;
      height: 100%;
    }
  }

  .coach-info {
    flex: 1;
    margin-left: 24rpx;
    overflow: hidden;

    .coach-name {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
      margin-bottom: 12rpx;
    }

    .coach-specialty {
      margin-bottom: 16rpx;

      .specialty-tag {
        display: inline-block;
        padding: 4rpx 12rpx;
        margin-right: 8rpx;
        background-color: #fff3e0;
        color: #ff9800;
        font-size: 22rpx;
        border-radius: 4rpx;
      }
    }

    .coach-stats {
      display: flex;

      .stat-item {
        margin-right: 32rpx;
        text-align: center;

        .stat-value {
          display: block;
          font-size: 28rpx;
          font-weight: 600;
          color: #333;
        }

        .stat-label {
          font-size: 22rpx;
          color: #999;
        }
      }
    }
  }

  .coach-action {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: space-between;

    .price {
      text-align: right;

      .price-value {
        font-size: 36rpx;
        font-weight: 600;
        color: #f44336;
      }

      .price-unit {
        font-size: 22rpx;
        color: #999;
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;

  .empty-image {
    width: 200rpx;
    height: 200rpx;
    margin-bottom: 20rpx;
  }

  .empty-text {
    font-size: 28rpx;
    color: #999;
  }
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;

  text {
    margin-left: 10rpx;
  }
}
</style>
