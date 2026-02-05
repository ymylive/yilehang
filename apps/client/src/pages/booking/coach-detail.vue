<template>
  <view class="coach-detail-page">
    <!-- 鏁欑粌淇℃伅澶撮儴 -->
    <view class="coach-header">
      <view class="coach-avatar">
        <image
          :src="coach?.avatar || '/static/default-avatar.png'"
          mode="aspectFill"
        />
      </view>
      <view class="coach-basic">
        <view class="coach-name">{{ coach?.name }}</view>
        <view class="coach-experience" v-if="coach?.years_of_experience">
          浠庝笟{{ coach.years_of_experience }}骞?        </view>
        <view class="coach-specialty">
          <text v-for="(s, i) in (coach?.specialty || [])" :key="i" class="specialty-tag">
            {{ s }}
          </text>
        </view>
      </view>
    </view>

    <!-- 缁熻鏁版嵁 -->
    <view class="stats-card">
      <view class="stat-item">
        <view class="stat-value">{{ coach?.avg_rating?.toFixed(1) || '0.0' }}</view>
        <view class="stat-label">璇勫垎</view>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <view class="stat-value">{{ coach?.total_lessons || 0 }}</view>
        <view class="stat-label">鎺堣鏁?/view>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <view class="stat-value">{{ coach?.total_students || 0 }}</view>
        <view class="stat-label">瀛﹀憳鏁?/view>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <view class="stat-value">{{ coach?.review_count || 0 }}</view>
        <view class="stat-label">璇勪环鏁?/view>
      </view>
    </view>

    <!-- 涓汉浠嬬粛 -->
    <view class="section-card" v-if="coach?.introduction">
      <view class="section-title">涓汉浠嬬粛</view>
      <view class="section-content">
        {{ coach.introduction }}
      </view>
    </view>

    <!-- 璧勮川璇佷功 -->
    <view class="section-card" v-if="coach?.certificates?.length">
      <view class="section-title">璧勮川璇佷功</view>
      <view class="certificates">
        <image
          v-for="(cert, i) in coach.certificates"
          :key="i"
          :src="cert"
          mode="aspectFill"
          class="cert-image"
          @click="previewImage(cert)"
        />
      </view>
    </view>

    <!-- 瀛﹀憳璇勪环 -->
    <view class="section-card">
      <view class="section-header">
        <view class="section-title">瀛﹀憳璇勪环</view>
        <view class="section-more" @click="viewAllReviews">
          鏌ョ湅鍏ㄩ儴
          <text class="arrow">></text>
        </view>
      </view>
      <view class="reviews-list">
        <view v-for="review in reviews" :key="review.id" class="review-item">
          <view class="review-header">
            <view class="reviewer-info">
              <image
                :src="review.student_avatar || '/static/default-avatar.png'"
                class="reviewer-avatar"
              />
              <text class="reviewer-name">{{ review.is_anonymous ? '鍖垮悕鐢ㄦ埛' : review.student_name }}</text>
            </view>
            <view class="review-rating">
              <text v-for="i in 5" :key="i" :class="['star', { active: i <= review.rating }]">鈽?/text>
            </view>
          </view>
          <view class="review-content" v-if="review.content">
            {{ review.content }}
          </view>
          <view class="review-tags" v-if="review.tags?.length">
            <text v-for="(tag, i) in review.tags" :key="i" class="review-tag">{{ tag }}</text>
          </view>
          <view class="review-time">{{ formatDate(review.created_at) }}</view>
        </view>
        <view v-if="reviews.length === 0" class="no-reviews">
          鏆傛棤璇勪环
        </view>
      </view>
    </view>

    <!-- 搴曢儴鎿嶄綔鏍?-->
    <view class="bottom-bar">
      <view class="price-info" v-if="coach?.hourly_rate">
        <text class="price-label">璇炬椂璐?/text>
        <text class="price-value">楼{{ coach.hourly_rate }}</text>
        <text class="price-unit">/璇炬椂</text>
      </view>
      <wd-button type="primary" block @click="goToSelectTime">
        绔嬪嵆绾﹁
      </wd-button>
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
  booking_id: number
  student_id: number
  coach_id: number
  rating: number
  content: string | null
  tags: string[] | null
  is_anonymous: boolean
  coach_reply: string | null
  created_at: string
  student_name: string | null
  student_avatar: string | null
}

const coachId = ref(0)
const coach = ref<Coach | null>(null)
const reviews = ref<Review[]>([])
const loading = ref(false)

async function loadCoachDetail() {
  loading.value = true
  try {
    coach.value = await coachApi.get(coachId.value)
  } catch (error: any) {
    uni.showToast({ title: error.message || '鍔犺浇澶辫触', icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function loadReviews() {
  try {
    const data = await coachApi.getReviews(coachId.value, 1, 5)
    reviews.value = data
  } catch (error) {
    console.error('鍔犺浇璇勪环澶辫触', error)
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function previewImage(url: string) {
  uni.previewImage({
    urls: coach.value?.certificates || [url],
    current: url
  })
}

function viewAllReviews() {
  uni.navigateTo({
    url: `/pages/booking/reviews-list?coachId=${coachId.value}`
  })
}

function goToSelectTime() {
  uni.navigateTo({
    url: `/pages/booking/select-time?coachId=${coachId.value}`
  })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any).$page?.options || {}
  coachId.value = parseInt(options.id) || 0

  if (coachId.value) {
    loadCoachDetail()
    loadReviews()
  }
})
</script>

<style lang="scss" scoped>
.coach-detail-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 140rpx;
}

.coach-header {
  display: flex;
  padding: 40rpx;
  background-color: #fff;

  .coach-avatar {
    width: 160rpx;
    height: 160rpx;
    border-radius: 16rpx;
    overflow: hidden;
    flex-shrink: 0;

    image {
      width: 100%;
      height: 100%;
    }
  }

  .coach-basic {
    flex: 1;
    margin-left: 30rpx;

    .coach-name {
      font-size: 40rpx;
      font-weight: 600;
      color: #333;
      margin-bottom: 12rpx;
    }

    .coach-experience {
      font-size: 26rpx;
      color: #666;
      margin-bottom: 16rpx;
    }

    .coach-specialty {
      .specialty-tag {
        display: inline-block;
        padding: 6rpx 16rpx;
        margin-right: 12rpx;
        background-color: #e8f5e9;
        color: #FF8800;
        font-size: 24rpx;
        border-radius: 6rpx;
      }
    }
  }
}

.stats-card {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background-color: #fff;
  padding: 30rpx 0;
  margin-top: 2rpx;

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 40rpx;
      font-weight: 600;
      color: #333;
    }

    .stat-label {
      font-size: 24rpx;
      color: #999;
      margin-top: 8rpx;
    }
  }

  .stat-divider {
    width: 1rpx;
    height: 60rpx;
    background-color: #eee;
  }
}

.section-card {
  background-color: #fff;
  margin-top: 20rpx;
  padding: 30rpx;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
  }

  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
  }

  .section-more {
    font-size: 26rpx;
    color: #999;

    .arrow {
      margin-left: 8rpx;
    }
  }

  .section-content {
    font-size: 28rpx;
    color: #666;
    line-height: 1.6;
  }
}

.certificates {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;

  .cert-image {
    width: 200rpx;
    height: 150rpx;
    border-radius: 8rpx;
  }
}

.reviews-list {
  .review-item {
    padding: 24rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .review-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16rpx;

      .reviewer-info {
        display: flex;
        align-items: center;

        .reviewer-avatar {
          width: 56rpx;
          height: 56rpx;
          border-radius: 50%;
          margin-right: 16rpx;
        }

        .reviewer-name {
          font-size: 28rpx;
          color: #333;
        }
      }

      .review-rating {
        .star {
          font-size: 28rpx;
          color: #ddd;

          &.active {
            color: #ffb800;
          }
        }
      }
    }

    .review-content {
      font-size: 28rpx;
      color: #666;
      line-height: 1.5;
      margin-bottom: 12rpx;
    }

    .review-tags {
      margin-bottom: 12rpx;

      .review-tag {
        display: inline-block;
        padding: 4rpx 12rpx;
        margin-right: 12rpx;
        background-color: #f5f5f5;
        color: #666;
        font-size: 22rpx;
        border-radius: 4rpx;
      }
    }

    .review-time {
      font-size: 24rpx;
      color: #999;
    }
  }

  .no-reviews {
    text-align: center;
    padding: 40rpx;
    color: #999;
    font-size: 28rpx;
  }
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: #fff;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);

  .price-info {
    margin-right: 30rpx;

    .price-label {
      font-size: 24rpx;
      color: #999;
    }

    .price-value {
      font-size: 40rpx;
      font-weight: 600;
      color: #f44336;
    }

    .price-unit {
      font-size: 24rpx;
      color: #999;
    }
  }

  :deep(.wd-button) {
    flex: 1;
  }
}
</style>
