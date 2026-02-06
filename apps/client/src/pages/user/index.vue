<template>
  <view class="user-page">
    <view class="hero">
      <view class="hero-glow" aria-hidden="true"></view>
      <view class="hero-orb orb-a" aria-hidden="true"></view>
      <view class="hero-orb orb-b" aria-hidden="true"></view>

      <view class="hero-content">
        <view v-if="userStore.isLoggedIn" class="profile-row" @click="editProfile">
          <image class="avatar" :src="userStore.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <view class="profile-text">
            <text class="name">{{ userStore.user?.nickname || userStore.user?.phone }}</text>
            <text class="role">{{ getRoleText(userStore.user?.role) }}</text>
          </view>
          <view class="profile-action">编辑</view>
        </view>

        <view v-else class="login-row" @click="goLogin">
          <text class="login-title">立即登录</text>
          <text class="login-sub">登录后可查看学员、预约和消费记录</text>
        </view>
      </view>
    </view>

    <view class="content">
      <view class="student-card" v-if="userStore.isLoggedIn && userStore.isParent">
        <view class="section-head">
          <text class="section-title">我的学员</text>
          <text class="section-link" @click="addStudent">添加学员</text>
        </view>

        <view class="student-list" v-if="students.length">
          <view
            class="student-item"
            v-for="student in students"
            :key="student.id"
            :class="{ active: userStore.currentStudent?.id === student.id }"
            @click="selectStudent(student)"
          >
            <view class="student-avatar">{{ student.name.charAt(0) }}</view>
            <view class="student-main">
              <text class="student-name">{{ student.name }}</text>
              <text class="student-meta">剩余课时 {{ student.remaining_lessons }}</text>
            </view>
            <text class="student-mark" v-if="userStore.currentStudent?.id === student.id">已选</text>
          </view>
        </view>

        <view v-else class="student-empty">
          <text>暂无学员，点击右上角添加</text>
        </view>
      </view>

      <view class="menu-card">
        <view class="menu-item" @click="goTo('/pages/membership/index')">
          <view class="menu-icon">卡</view>
          <text class="menu-label">我的会员卡</text>
          <text class="menu-badge" v-if="userStore.currentStudent?.remaining_lessons">{{ userStore.currentStudent.remaining_lessons }}次</text>
          <text class="menu-arrow">&gt;</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/messages')">
          <view class="menu-icon">信</view>
          <text class="menu-label">消息中心</text>
          <text class="menu-arrow">&gt;</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/orders')">
          <view class="menu-icon">单</view>
          <text class="menu-label">我的订单</text>
          <text class="menu-arrow">&gt;</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/coupons')">
          <view class="menu-icon">券</view>
          <text class="menu-label">优惠券</text>
          <text class="menu-arrow">&gt;</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/feedback')">
          <view class="menu-icon">意</view>
          <text class="menu-label">意见反馈</text>
          <text class="menu-arrow">&gt;</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/settings')">
          <view class="menu-icon">设</view>
          <text class="menu-label">设置</text>
          <text class="menu-arrow">&gt;</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/about')">
          <view class="menu-icon">关</view>
          <text class="menu-label">关于我们</text>
          <text class="menu-arrow">&gt;</text>
        </view>
      </view>

      <view class="logout-wrap" v-if="userStore.isLoggedIn">
        <button class="logout-btn" @click="logout">退出登录</button>
      </view>
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
    content: '确定退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
      }
    }
  })
}
</script>

<style scoped>
.user-page {
  min-height: 100vh;
  background: #f7f8fb;
  padding-bottom: 120rpx;
}

.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #ffbc47 0%, #ff8d1f 72%);
  border-radius: 0 0 44rpx 44rpx;
  padding: 36rpx 30rpx 90rpx;
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

.hero-orb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
}

.orb-a {
  width: 128rpx;
  height: 128rpx;
  left: -28rpx;
  bottom: 32rpx;
}

.orb-b {
  width: 88rpx;
  height: 88rpx;
  right: 110rpx;
  top: 44rpx;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.profile-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.42);
  background: #fff;
}

.profile-text {
  flex: 1;
}

.name {
  display: block;
  font-size: 35rpx;
  font-weight: 700;
  color: #fff;
}

.role {
  display: block;
  margin-top: 8rpx;
  width: fit-content;
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  font-size: 21rpx;
  color: rgba(255, 255, 255, 0.92);
  background: rgba(255, 255, 255, 0.2);
}

.profile-action {
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #d47000;
  background: rgba(255, 255, 255, 0.92);
}

.login-row {
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.14);
  border: 1rpx solid rgba(255, 255, 255, 0.22);
  padding: 24rpx;
}

.login-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
}

.login-sub {
  display: block;
  margin-top: 10rpx;
  font-size: 23rpx;
  color: rgba(255, 255, 255, 0.9);
}

.content {
  margin-top: -48rpx;
  position: relative;
  z-index: 3;
  padding: 0 22rpx;
}

.student-card,
.menu-card,
.logout-wrap {
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
}

.student-card {
  padding: 20rpx;
  margin-bottom: 14rpx;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2533;
}

.section-link {
  font-size: 24rpx;
  color: #df7e17;
}

.student-list {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  border-radius: 16rpx;
  background: #f8f9fc;
  padding: 14rpx;
}

.student-item.active {
  background: #fff4e4;
  box-shadow: inset 0 0 0 2rpx rgba(255, 145, 32, 0.5);
}

.student-avatar {
  width: 62rpx;
  height: 62rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #ffbe52, #ff9120);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
}

.student-main {
  flex: 1;
}

.student-name {
  display: block;
  font-size: 27rpx;
  font-weight: 700;
  color: #1f2533;
}

.student-meta {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #8e97aa;
}

.student-mark {
  font-size: 22rpx;
  color: #dd7c16;
}

.student-empty {
  font-size: 24rpx;
  color: #98a1b4;
  padding: 10rpx 0;
}

.menu-card {
  overflow: hidden;
}

.menu-item {
  height: 90rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 0 20rpx;
  border-bottom: 1rpx solid #eef1f6;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: #fff8ee;
}

.menu-icon {
  width: 58rpx;
  height: 58rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #fff6e6, #ffe5c4);
  color: #df7e17;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-label {
  flex: 1;
  font-size: 27rpx;
  color: #2b3448;
}

.menu-badge {
  font-size: 22rpx;
  color: #dd7c16;
  margin-right: 8rpx;
}

.menu-arrow {
  font-size: 22rpx;
  color: #9aa2b5;
}

.logout-wrap {
  margin-top: 14rpx;
  padding: 12rpx;
}

.logout-btn {
  width: 100%;
  height: 84rpx;
  border: none;
  border-radius: 18rpx;
  background: #fff4f1;
  color: #d95b4a;
  font-size: 30rpx;
  font-weight: 700;
}

.logout-btn::after {
  border: none;
}
</style>
