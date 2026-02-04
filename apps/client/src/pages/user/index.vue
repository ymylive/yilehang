<template>
  <view class="page">
    <view class="header">
      <text class="title">我的</text>
    </view>

    <!-- 用户信息 -->
    <view class="user-card" v-if="userStore.isLoggedIn">
      <image class="avatar" :src="userStore.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
      <view class="info">
        <text class="name">{{ userStore.user?.nickname || userStore.user?.phone }}</text>
        <text class="role">{{ getRoleText(userStore.user?.role) }}</text>
      </view>
      <view class="edit-btn" @click="editProfile">编辑</view>
    </view>
    <view class="user-card login-card" v-else @click="goLogin">
      <text class="login-text">点击登录</text>
    </view>

    <!-- 学员切换 -->
    <view class="section" v-if="userStore.isLoggedIn && userStore.isParent">
      <view class="section-header">
        <text class="title">我的学员</text>
        <text class="add" @click="addStudent">+ 添加</text>
      </view>
      <view class="student-list">
        <view
          class="student-item"
          v-for="student in students"
          :key="student.id"
          :class="{ active: userStore.currentStudent?.id === student.id }"
          @click="selectStudent(student)"
        >
          <view class="student-avatar">{{ student.name.charAt(0) }}</view>
          <view class="student-info">
            <text class="name">{{ student.name }}</text>
            <text class="lessons">剩余课时: {{ student.remaining_lessons }}</text>
          </view>
          <view class="check" v-if="userStore.currentStudent?.id === student.id">✓</view>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-list">
      <view class="menu-item" @click="goTo('/pages/user/orders')">
        <text class="icon">📋</text>
        <text class="label">我的订单</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/coupons')">
        <text class="icon">🎫</text>
        <text class="label">优惠券</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/feedback')">
        <text class="icon">💬</text>
        <text class="label">意见反馈</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/settings')">
        <text class="icon">⚙️</text>
        <text class="label">设置</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/about')">
        <text class="icon">ℹ️</text>
        <text class="label">关于我们</text>
        <text class="arrow">></text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-btn" v-if="userStore.isLoggedIn" @click="logout">
      退出登录
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { studentApi } from '@/api'

const userStore = useUserStore()

const students = ref<any[]>([])

onMounted(async () => {
  if (userStore.isLoggedIn) {
    await loadStudents()
  }
})

async function loadStudents() {
  try {
    const res = await studentApi.list()
    students.value = res || []

    // 如果没有选中学员，默认选中第一个
    if (!userStore.currentStudent && students.value.length) {
      userStore.setCurrentStudent(students.value[0])
    }
  } catch (error) {
    console.error('加载学员失败', error)
  }
}

function getRoleText(role?: string) {
  const map: Record<string, string> = {
    parent: '家长',
    coach: '教练',
    admin: '管理员',
    student: '学员'
  }
  return map[role || ''] || '用户'
}

function selectStudent(student: any) {
  userStore.setCurrentStudent(student)
  uni.showToast({ title: `已切换到 ${student.name}`, icon: 'none' })
}

function addStudent() {
  uni.navigateTo({ url: '/pages/user/add-student' })
}

function editProfile() {
  uni.navigateTo({ url: '/pages/user/profile' })
}

function goLogin() {
  uni.navigateTo({ url: '/pages/user/login' })
}

function goTo(url: string) {
  uni.navigateTo({ url })
}

function logout() {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
      }
    }
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.header {
  padding: 60rpx 30rpx 30rpx;
  background: #fff;
}

.header .title {
  font-size: 44rpx;
  font-weight: bold;
  color: #333;
}

.user-card {
  display: flex;
  align-items: center;
  padding: 30rpx;
  background: #fff;
  margin-bottom: 20rpx;
}

.login-card {
  justify-content: center;
  padding: 60rpx;
}

.login-text {
  font-size: 32rpx;
  color: #4CAF50;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
}

.info {
  flex: 1;
  margin-left: 24rpx;
}

.info .name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.info .role {
  font-size: 26rpx;
  color: #999;
  margin-top: 8rpx;
}

.edit-btn {
  padding: 12rpx 30rpx;
  background: #f5f5f5;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
}

.section {
  background: #fff;
  margin-bottom: 20rpx;
  padding: 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-header .title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.section-header .add {
  font-size: 28rpx;
  color: #4CAF50;
}

.student-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  background: #f9f9f9;
}

.student-item.active {
  background: #E8F5E9;
  border: 2rpx solid #4CAF50;
}

.student-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #4CAF50;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: bold;
}

.student-info {
  flex: 1;
  margin-left: 20rpx;
}

.student-info .name {
  font-size: 30rpx;
  color: #333;
  display: block;
}

.student-info .lessons {
  font-size: 24rpx;
  color: #999;
}

.check {
  color: #4CAF50;
  font-size: 36rpx;
  font-weight: bold;
}

.menu-list {
  background: #fff;
  margin-bottom: 20rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item .icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.menu-item .label {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.menu-item .arrow {
  color: #ccc;
  font-size: 28rpx;
}

.logout-btn {
  margin: 40rpx 30rpx;
  padding: 30rpx;
  background: #fff;
  border-radius: 16rpx;
  text-align: center;
  font-size: 32rpx;
  color: #F44336;
}
</style>
