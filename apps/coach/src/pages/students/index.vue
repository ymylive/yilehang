<template>
  <view class="students-page">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <wd-search v-model="searchKeyword" placeholder="搜索学员" @search="handleSearch" />
    </view>

    <!-- 学员列表 -->
    <view class="student-list">
      <view
        v-for="student in filteredStudents"
        :key="student.id"
        class="student-card"
        @click="goToDetail(student.id)"
      >
        <view class="student-avatar">
          {{ student.name.charAt(0) }}
        </view>
        <view class="student-info">
          <view class="student-name">{{ student.name }}</view>
          <view class="student-meta">
            <text>{{ student.gender === 'male' ? '男' : '女' }}</text>
            <text v-if="student.age">{{ student.age }}岁</text>
          </view>
          <view class="student-stats">
            <text>已上{{ student.completed_lessons }}节课</text>
            <text>剩余{{ student.remaining_lessons }}次</text>
          </view>
        </view>
        <view class="student-action">
          <wd-button size="small" plain @click.stop="goToFeedback(student.id)">
            写反馈
          </wd-button>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="filteredStudents.length === 0" class="empty-state">
        <text class="empty-icon">👥</text>
        <text class="empty-text">暂无学员</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Student {
  id: number
  name: string
  gender: string
  age: number | null
  completed_lessons: number
  remaining_lessons: number
}

const searchKeyword = ref('')
const students = ref<Student[]>([])

const filteredStudents = computed(() => {
  if (!searchKeyword.value) return students.value
  return students.value.filter(s =>
    s.name.includes(searchKeyword.value)
  )
})

function handleSearch() {
  // 搜索由 computed 自动处理
}

function goToDetail(id: number) {
  uni.navigateTo({ url: `/pages/students/detail?id=${id}` })
}

function goToFeedback(id: number) {
  uni.navigateTo({ url: `/pages/students/feedback?studentId=${id}` })
}

onMounted(() => {
  // 模拟数据
  students.value = [
    { id: 1, name: '小明', gender: 'male', age: 10, completed_lessons: 15, remaining_lessons: 5 },
    { id: 2, name: '小红', gender: 'female', age: 8, completed_lessons: 20, remaining_lessons: 10 },
    { id: 3, name: '小刚', gender: 'male', age: 12, completed_lessons: 8, remaining_lessons: 12 },
    { id: 4, name: '小美', gender: 'female', age: 9, completed_lessons: 25, remaining_lessons: 3 }
  ]
})
</script>

<style lang="scss" scoped>
.students-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
}

.search-bar {
  padding: 20rpx;
  background-color: #fff;
}

.student-list {
  padding: 20rpx;
}

.student-card {
  display: flex;
  align-items: center;
  background-color: #fff;
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 16rpx;

  .student-avatar {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40rpx;
    font-weight: 600;
  }

  .student-info {
    flex: 1;
    margin-left: 24rpx;

    .student-name {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
    }

    .student-meta {
      font-size: 24rpx;
      color: #999;
      margin-top: 8rpx;

      text {
        margin-right: 16rpx;
      }
    }

    .student-stats {
      font-size: 24rpx;
      color: #666;
      margin-top: 8rpx;

      text {
        margin-right: 20rpx;
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;

  .empty-icon {
    font-size: 80rpx;
    margin-bottom: 20rpx;
  }

  .empty-text {
    font-size: 28rpx;
    color: #999;
  }
}
</style>
