<template>
  <PageErrorBoundary page="user.index" @retry="retryLoad">
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
      <!-- 商家工作台入口 -->
      <view class="merchant-card" v-if="userStore.isLoggedIn && userStore.user?.role === 'merchant'">
        <view class="section-head">
          <text class="section-title">商家工作台</text>
        </view>
        <view class="merchant-actions">
          <view class="merchant-action-item" @click="goTo('/pages/merchant/index')">
            <view class="action-icon"><wd-icon name="shop" size="38rpx" /></view>
            <text class="action-label">工作台</text>
          </view>
          <view class="merchant-action-item" @click="goTo('/pages/merchant/verify')">
            <view class="action-icon"><wd-icon name="scan" size="38rpx" /></view>
            <text class="action-label">扫码核销</text>
          </view>
          <view class="merchant-action-item" @click="goTo('/pages/merchant/orders')">
            <view class="action-icon"><wd-icon name="view-list" size="38rpx" /></view>
            <text class="action-label">订单管理</text>
          </view>
          <view class="merchant-action-item" @click="goTo('/pages/merchant/stats')">
            <view class="action-icon"><wd-icon name="chart-bar" size="38rpx" /></view>
            <text class="action-label">数据统计</text>
          </view>
        </view>
      </view>

      <!-- 教练工作台入口 -->
      <view class="coach-card" v-if="userStore.isLoggedIn && userStore.user?.role === 'coach'">
        <view class="section-head">
          <text class="section-title">教练工作台</text>
        </view>
        <view class="coach-actions">
          <view class="coach-action-item" @click="goTo('/pages/coach/workbench/index')">
            <view class="action-icon"><wd-icon name="dashboard" size="38rpx" /></view>
            <text class="action-label">工作台</text>
          </view>
          <view class="coach-action-item" @click="goTo('/pages/coach/schedule/index')">
            <view class="action-icon"><wd-icon name="calendar" size="38rpx" /></view>
            <text class="action-label">我的课表</text>
          </view>
          <view class="coach-action-item" @click="goTo('/pages/coach/students/index')">
            <view class="action-icon"><wd-icon name="usergroup" size="38rpx" /></view>
            <text class="action-label">我的学员</text>
          </view>
          <view class="coach-action-item" @click="goTo('/pages/coach/income/index')">
            <view class="action-icon"><wd-icon name="wallet" size="38rpx" /></view>
            <text class="action-label">收入统计</text>
          </view>
        </view>
      </view>

      <!-- 学员信息卡片（学员角色） -->
      <view class="student-card" v-if="userStore.isLoggedIn && userStore.isStudent">
        <view class="section-head">
          <text class="section-title">我的信息</text>
        </view>
        <view class="student-self-info">
          <view class="info-row">
            <text class="info-label">学号</text>
            <text class="info-value">{{ userStore.user?.student?.student_no || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">剩余课时</text>
            <text class="info-value highlight">{{ userStore.user?.student?.remaining_lessons || 0 }} 次</text>
          </view>
        </view>
      </view>

      <!-- 我的学员卡片（家长角色） -->
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
            <view class="student-actions">
              <text class="student-mark" v-if="userStore.currentStudent?.id === student.id">已选</text>
              <text class="create-account-btn" v-if="!student.user_id" @click.stop="createStudentAccount(student)">创建账号</text>
            </view>
          </view>
        </view>

        <view v-else class="student-empty">
          <text>暂无学员，点击右上角添加</text>
        </view>
      </view>

      <view class="menu-card" v-if="userStore.isLoggedIn && (userStore.isParent || userStore.isStudent)">
        <view class="menu-item" @click="goTo('/pages/membership/index')" v-if="userStore.isParent || userStore.isStudent">
          <view class="menu-icon"><wd-icon name="books" size="30rpx" /></view>
          <text class="menu-label">我的会员卡</text>
          <text class="menu-badge" v-if="userStore.currentStudent?.remaining_lessons">{{ userStore.currentStudent.remaining_lessons }}次</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/chat/index')">
          <view class="menu-icon"><wd-icon name="chat" size="30rpx" /></view>
          <text class="menu-label">聊天消息</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/messages')">
          <view class="menu-icon"><wd-icon name="notification" size="30rpx" /></view>
          <text class="menu-label">系统通知</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/schedule/index')" v-if="userStore.isParent || userStore.isStudent">
          <view class="menu-icon"><wd-icon name="calendar" size="30rpx" /></view>
          <text class="menu-label">我的课表</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/membership/transactions')" v-if="userStore.isParent || userStore.isStudent">
          <view class="menu-icon"><wd-icon name="view-list" size="30rpx" /></view>
          <text class="menu-label">消费记录</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/review/create')" v-if="userStore.isStudent || userStore.isParent">
          <view class="menu-icon"><wd-icon name="star" size="30rpx" /></view>
          <text class="menu-label">课程评价</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/user/profile')">
          <view class="menu-icon"><wd-icon name="setting" size="30rpx" /></view>
          <text class="menu-label">个人资料</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goTo('/pages/index/index')">
          <view class="menu-icon"><wd-icon name="home" size="30rpx" /></view>
          <text class="menu-label">平台首页</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="logout-wrap" v-if="userStore.isLoggedIn">
        <button class="logout-btn" @click="logout">退出登录</button>
      </view>
    </view>
  <DynamicTabBar />
 </view>
 </PageErrorBoundary>
</template>

<script setup lang="ts">
import DynamicTabBar from '@/components/DynamicTabBar.vue'
import PageErrorBoundary from '@/components/PageErrorBoundary.vue'
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { studentApi } from '@/api'
import { safeNavigate } from '@/utils/safe-nav'

const userStore = useUserStore()
const students = ref<any[]>([])

onMounted(async () => {
  if (userStore.isLoggedIn && userStore.isParent) {
    await loadStudents()
  }
})

function retryLoad() {
  if (userStore.isLoggedIn && userStore.isParent) {
    loadStudents()
  }
}

async function loadStudents() {
  try {
    const res: any = await studentApi.list()
    students.value = Array.isArray(res) ? res : (Array.isArray(res?.items) ? res.items : [])

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
    student: '学员',
    merchant: '商家'
  }
  return map[role || ''] || '用户'
}

function selectStudent(student: any) {
  userStore.setCurrentStudent(student)
  uni.showToast({ title: `已切换到 ${student.name}`, icon: 'none' })
}

function addStudent() {
  safeNavigate('/pages/user/create-student-account')
}

function createStudentAccount(student: any) {
  safeNavigate(`/pages/user/create-student-account?id=${student.id}`)
}

function editProfile() {
  safeNavigate('/pages/user/profile')
}

function goLogin() {
  safeNavigate('/pages/user/login')
}

function goTo(url: string) {
  safeNavigate(url)
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
  padding-bottom: var(--tabbar-content-offset, calc(120rpx + env(safe-area-inset-bottom)));
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
  background: linear-gradient(180deg, #ffffff, #fdfefe);
  border: 1rpx solid rgba(228, 234, 245, 0.9);
  box-shadow: 0 12rpx 26rpx rgba(31, 37, 51, 0.06);
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

.student-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
}

.create-account-btn {
  font-size: 20rpx;
  color: #fff;
  background: linear-gradient(135deg, #ffbe52, #ff9120);
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
}

.student-self-info {
  padding: 10rpx 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 26rpx;
  color: #666;
}

.info-value {
  font-size: 26rpx;
  color: #333;
  font-weight: 600;
}

.info-value.highlight {
  color: #FF8800;
}

.merchant-card,
.coach-card {
  padding: 20rpx;
  margin-bottom: 14rpx;
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 37, 51, 0.05);
}

.merchant-actions,
.coach-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}

.merchant-action-item,
.coach-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 20rpx 0;
  border-radius: 16rpx;
  background: linear-gradient(180deg, #f9fbff, #f4f8ff);
  border: 1rpx solid rgba(222, 232, 247, 0.9);
  transition: transform 180ms ease, box-shadow 180ms ease;
  cursor: pointer;
}

.merchant-action-item:active,
.coach-action-item:active {
  transform: translateY(2rpx);
  box-shadow: 0 8rpx 18rpx rgba(40, 68, 109, 0.12);
}

.action-icon {
  width: 68rpx;
  height: 68rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #edf4ff, #e7f0ff);
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-label {
  font-size: 22rpx;
  color: #666;
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
  transition: background-color 180ms ease, transform 180ms ease;
  cursor: pointer;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: #f8fbff;
  transform: translateY(1rpx);
}

.menu-icon {
  width: 58rpx;
  height: 58rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #edf4ff, #e7f0ff);
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1rpx rgba(203, 217, 239, 0.9);
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
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  padding: 0;
}

.logout-btn::after {
  border: none;
}
</style>
