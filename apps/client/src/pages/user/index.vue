<template>
  <view class="page">
    <view class="header">
      <text class="title">鎴戠殑</text>
    </view>

    <!-- 鐢ㄦ埛淇℃伅 -->
    <view class="user-card" v-if="userStore.isLoggedIn">
      <image class="avatar" :src="userStore.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
      <view class="info">
        <text class="name">{{ userStore.user?.nickname || userStore.user?.phone }}</text>
        <text class="role">{{ getRoleText(userStore.user?.role) }}</text>
      </view>
      <view class="edit-btn" @click="editProfile">缂栬緫</view>
    </view>
    <view class="user-card login-card" v-else @click="goLogin">
      <text class="login-text">鐐瑰嚮鐧诲綍</text>
    </view>

    <!-- 瀛﹀憳鍒囨崲 -->
    <view class="section" v-if="userStore.isLoggedIn && userStore.isParent">
      <view class="section-header">
        <text class="title">鎴戠殑瀛﹀憳</text>
        <text class="add" @click="addStudent">+ 娣诲姞</text>
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
            <text class="lessons">鍓╀綑璇炬椂: {{ student.remaining_lessons }}</text>
          </view>
          <view class="check" v-if="userStore.currentStudent?.id === student.id">鉁?/view>
        </view>
      </view>
    </view>

    <!-- 鍔熻兘鑿滃崟 -->
    <view class="menu-list">
      <view class="menu-item" @click="goTo('/pages/membership/index')">
        <text class="icon">馃挸</text>
        <text class="label">鎴戠殑璇炬椂鍗?/text>
        <text class="badge" v-if="userStore.currentStudent?.remaining_lessons">{{ userStore.currentStudent.remaining_lessons }}娆?/text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/messages')">
        <text class="icon">馃敂</text>
        <text class="label">娑堟伅閫氱煡</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/orders')">
        <text class="icon">馃搵</text>
        <text class="label">鎴戠殑璁㈠崟</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/coupons')">
        <text class="icon">馃帿</text>
        <text class="label">浼樻儬鍒?/text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/feedback')">
        <text class="icon">馃挰</text>
        <text class="label">鎰忚鍙嶉</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/settings')">
        <text class="icon">鈿欙笍</text>
        <text class="label">璁剧疆</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/user/about')">
        <text class="icon">鈩癸笍</text>
        <text class="label">鍏充簬鎴戜滑</text>
        <text class="arrow">></text>
      </view>
    </view>

    <!-- 閫€鍑虹櫥褰?-->
    <view class="logout-btn" v-if="userStore.isLoggedIn" @click="logout">
      閫€鍑虹櫥褰?    </view>
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

    // 濡傛灉娌℃湁閫変腑瀛﹀憳锛岄粯璁ら€変腑绗竴涓?    if (!userStore.currentStudent && students.value.length) {
      userStore.setCurrentStudent(students.value[0])
    }
  } catch (error) {
    console.error('鍔犺浇瀛﹀憳澶辫触', error)
  }
}

function getRoleText(role?: string) {
  const map: Record<string, string> = {
    parent: '瀹堕暱',
    coach: '鏁欑粌',
    admin: '绠＄悊鍛?,
    student: '瀛﹀憳'
  }
  return map[role || ''] || '鐢ㄦ埛'
}

function selectStudent(student: any) {
  userStore.setCurrentStudent(student)
  uni.showToast({ title: `宸插垏鎹㈠埌 ${student.name}`, icon: 'none' })
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
    title: '鎻愮ず',
    content: '纭畾瑕侀€€鍑虹櫥褰曞悧锛?,
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
  color: #FF8800;
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
  color: #FF8800;
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
  border: 2rpx solid #FF8800;
}

.student-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #FF8800;
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
  color: #FF8800;
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

.menu-item .badge {
  padding: 4rpx 16rpx;
  background: #e8f5e9;
  color: #FF8800;
  font-size: 24rpx;
  border-radius: 20rpx;
  margin-right: 16rpx;
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
