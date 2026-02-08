<template>
  <view class="students-page">
    <view class="header-card">
      <wd-search
        v-model="searchKeyword"
        :placeholder="t.searchPlaceholder"
        @search="handleSearch"
      />
      <view class="summary-row">
        <view class="summary-item">
          <text class="summary-value">{{ filteredStudents.length }}</text>
          <text class="summary-label">{{ t.visible }}</text>
        </view>
        <view class="summary-divider"></view>
        <view class="summary-item">
          <text class="summary-value">{{ activeStudents }}</text>
          <text class="summary-label">{{ t.activeLessons }}</text>
        </view>
      </view>
    </view>

    <view v-if="loading" class="empty-state">
      <view class="empty-icon">{{ t.loadingIcon }}</view>
      <text class="empty-title">{{ t.loading }}</text>
      <text class="empty-sub">{{ t.loadingSub }}</text>
    </view>

    <view class="student-list" v-else-if="filteredStudents.length">
      <view
        v-for="student in filteredStudents"
        :key="student.id"
        class="student-card"
        @click="goToDetail(student.id)"
      >
        <view class="student-avatar" :class="avatarTone(student.id)">
          {{ student.name.charAt(0) }}
        </view>

        <view class="student-main">
          <view class="name-row">
            <text class="student-name">{{ student.name }}</text>
            <text class="gender-tag" :class="student.gender === 'male' ? 'male' : 'female'">
              {{ student.gender === 'male' ? t.male : t.female }}
            </text>
            <text v-if="student.age" class="age-tag">{{ student.age }}{{ t.ageUnit }}</text>
          </view>
          <view class="data-row">
            <view class="data-item">
              <text class="data-label">{{ t.completedLessons }}</text>
              <text class="data-value">{{ student.completed_lessons }}</text>
            </view>
            <view class="data-divider"></view>
            <view class="data-item">
              <text class="data-label">{{ t.remainingLessons }}</text>
              <text class="data-value highlight">{{ student.remaining_lessons }}</text>
            </view>
          </view>
        </view>

        <view class="student-action">
          <button class="feedback-btn" @click.stop="goToFeedback(student.id)">{{ t.feedback }}</button>
        </view>
      </view>
    </view>

    <view v-else class="empty-state">
      <view class="empty-icon">{{ t.emptyIcon }}</view>
      <text class="empty-title">{{ t.emptyTitle }}</text>
      <text class="empty-sub">{{ t.emptySub }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { coachStudentsApi } from '@/api/index'

interface Student {
  id: number
  name: string
  gender: string
  age: number | null
  completed_lessons: number
  remaining_lessons: number
}

const t = {
  searchPlaceholder: '\u641c\u7d22\u5b66\u5458\u59d3\u540d',
  visible: '\u5f53\u524d\u53ef\u89c1',
  activeLessons: '\u6709\u4f59\u8bfe',
  loadingIcon: '\u8f7d',
  loading: '\u52a0\u8f7d\u4e2d...',
  loadingSub: '\u6b63\u5728\u83b7\u53d6\u5b66\u5458\u6570\u636e',
  male: '\u7537',
  female: '\u5973',
  ageUnit: '\u5c81',
  completedLessons: '\u5df2\u4e0a\u8bfe',
  remainingLessons: '\u5269\u4f59\u8bfe\u65f6',
  feedback: '\u5199\u53cd\u9988',
  emptyIcon: '\u5458',
  emptyTitle: '\u6682\u65e0\u5339\u914d\u5b66\u5458',
  emptySub: '\u53ef\u8c03\u6574\u5173\u952e\u8bcd\u540e\u518d\u8bd5',
  loadFailed: '\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5'
} as const

const searchKeyword = ref('')
const students = ref<Student[]>([])
const loading = ref(false)

const filteredStudents = computed(() => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) return students.value
  return students.value.filter(student => student.name.includes(keyword))
})

const activeStudents = computed(() => {
  return filteredStudents.value.filter(student => student.remaining_lessons > 0).length
})

function calcAge(birthDate?: string) {
  if (!birthDate) return null
  const birth = new Date(birthDate)
  if (Number.isNaN(birth.getTime())) return null
  const now = new Date()
  let age = now.getFullYear() - birth.getFullYear()
  const monthDiff = now.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birth.getDate())) {
    age -= 1
  }
  return age > 0 ? age : null
}

function normalizeStudent(raw: any): Student {
  return {
    id: Number(raw?.id || 0),
    name: String(raw?.name || raw?.student_name || '\u5b66\u5458'),
    gender: String(raw?.gender || 'male'),
    age: Number(raw?.age || 0) || calcAge(raw?.birth_date),
    completed_lessons: Number(raw?.completed_lessons ?? raw?.total_lessons ?? 0),
    remaining_lessons: Number(raw?.remaining_lessons ?? raw?.remaining_times ?? 0)
  }
}

function normalizeList(data: any): Student[] {
  const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
  return list.map(normalizeStudent).filter(item => item.id > 0)
}

function avatarTone(id: number) {
  const tones = ['tone-a', 'tone-b', 'tone-c']
  return tones[id % tones.length]
}

function handleSearch() {
  // computed handles filtering
}

function goToDetail(id: number) {
  uni.navigateTo({ url: `/pages/coach/students/detail?id=${id}` })
}

function goToFeedback(id: number) {
  uni.navigateTo({ url: `/pages/coach/students/feedback?studentId=${id}` })
}

async function loadStudents() {
  loading.value = true
  try {
    const data = await coachStudentsApi.getStudents({ page: 1, page_size: 200 })
    students.value = normalizeList(data)
  } catch (error: any) {
    uni.showToast({ title: error.message || t.loadFailed, icon: 'none' })
    students.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadStudents()
})
</script>

<style lang="scss" scoped>
.students-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding: 20rpx;
  padding-bottom: calc(120rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.header-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 20rpx;
  box-shadow: 0 10rpx 22rpx rgba(31, 37, 51, 0.05);
}

:deep(.wd-search) {
  --wot-search-height: 68rpx;
}

:deep(.wd-search__container) {
  border-radius: 999rpx;
  background: #f2f3f5;
  border: none;
}

:deep(.wd-search__input) {
  color: #1f2533;
}

.summary-row {
  margin-top: 16rpx;
  display: flex;
  align-items: center;
  border-radius: 16rpx;
  background: #fff8ee;
  padding: 14rpx 10rpx;
}

.summary-item {
  flex: 1;
  text-align: center;
}

.summary-value {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: #2a3245;
}

.summary-label {
  display: block;
  margin-top: 4rpx;
  font-size: 21rpx;
  color: #8e97aa;
}

.summary-divider {
  width: 2rpx;
  height: 42rpx;
  background: #f0dfc9;
}

.student-list {
  margin-top: 18rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.student-card {
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 20rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  transition: all 0.2s ease;
}

.student-card:active {
  transform: scale(0.99);
}

.student-avatar {
  width: 92rpx;
  height: 92rpx;
  border-radius: 26rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 34rpx;
  font-weight: 700;
  flex-shrink: 0;
  border: 2rpx solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 8rpx 18rpx rgba(255, 143, 31, 0.2);
}

.student-avatar.tone-a {
  background: linear-gradient(135deg, #ffbf5d, #ff8f1f);
}

.student-avatar.tone-b {
  background: linear-gradient(135deg, #ffcf7f, #ff9b34);
}

.student-avatar.tone-c {
  background: linear-gradient(135deg, #ffc996, #ff8948);
}

.student-main {
  flex: 1;
  min-width: 0;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.student-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2533;
}

.gender-tag,
.age-tag {
  font-size: 20rpx;
  border-radius: 999rpx;
  padding: 3rpx 10rpx;
  color: #727c91;
  background: #f4f6fa;
}

.gender-tag.male {
  color: #da7f13;
  background: #fff1df;
}

.gender-tag.female {
  color: #cf6d14;
  background: #ffe9cf;
}

.data-row {
  display: flex;
  align-items: center;
  margin-top: 12rpx;
}

.data-item {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
}

.data-label {
  font-size: 22rpx;
  color: #8790a4;
}

.data-value {
  font-size: 27rpx;
  color: #4d566d;
  font-weight: 700;
}

.data-value.highlight {
  color: #e38518;
  font-size: 31rpx;
}

.data-divider {
  width: 2rpx;
  height: 22rpx;
  background: #e8ebf1;
  margin: 0 16rpx;
}

.student-action {
  flex-shrink: 0;
}

.feedback-btn {
  border: none;
  border-radius: 999rpx;
  padding: 10rpx 18rpx;
  line-height: 1;
  font-size: 22rpx;
  color: #d7740b;
  background: #fff2e0;
}

.feedback-btn::after {
  border: none;
}

.empty-state {
  margin-top: 18rpx;
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
  padding: 52rpx 24rpx;
  text-align: center;
}

.empty-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #fff1dd, #ffdcb9);
  color: #ff8d1f;
  font-size: 36rpx;
  font-weight: 700;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
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
</style>
