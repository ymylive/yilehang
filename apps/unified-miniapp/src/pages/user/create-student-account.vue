<template>
  <view class="page">
    <view class="header">
      <text class="title">为学员创建独立账号</text>
      <text class="subtitle">创建后，学员可以使用自己的账号登录</text>
    </view>

    <!-- 学员信息 -->
    <view class="student-card">
      <image class="avatar" :src="student?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
      <view class="info">
        <text class="name">{{ student?.name || '学员' }}</text>
        <text class="no">学号: {{ student?.student_no || '-' }}</text>
      </view>
    </view>

    <!-- 表单 -->
    <view class="form-section">
      <view class="form-item">
        <text class="label">登录邮箱</text>
        <input
          class="input"
          type="text"
          v-model="email"
          placeholder="请输入邮箱"
        />
      </view>
      <view class="form-item">
        <text class="label">登录密码</text>
        <input
          class="input"
          type="password"
          v-model="password"
          placeholder="请设置密码（至少6位）"
        />
      </view>
      <view class="form-item">
        <text class="label">确认密码</text>
        <input
          class="input"
          type="password"
          v-model="confirmPassword"
          placeholder="请再次输入密码"
        />
      </view>
    </view>

    <!-- 提示 -->
    <view class="tips">
      <text class="tip-item">• 学员账号创建后，学员可独立登录查看自己的课程和成长档案</text>
      <text class="tip-item">• 家长仍可在自己的账号中管理该学员</text>
      <text class="tip-item">• 请妥善保管账号密码</text>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <button class="submit-btn" :loading="submitting" @click="createAccount">
        创建账号
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { studentApi, authApi } from '@/api'

const userStore = useUserStore()

const student = ref<any>(null)
const studentId = ref(0)
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const submitting = ref(false)

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  studentId.value = parseInt((currentPage as any).options?.id) || 0

  if (studentId.value) {
    await loadStudent()
  } else {
    uni.showToast({ title: '参数错误', icon: 'none' })
  }
})

async function loadStudent() {
  try {
    student.value = await studentApi.get(studentId.value)
  } catch (error) {
    console.error('加载学员信息失败', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function validateEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

async function createAccount() {
  // 验证
  if (!email.value.trim()) {
    uni.showToast({ title: '请输入邮箱', icon: 'none' })
    return
  }
  if (!validateEmail(email.value.trim())) {
    uni.showToast({ title: '邮箱格式不正确', icon: 'none' })
    return
  }
  if (!password.value) {
    uni.showToast({ title: '请设置密码', icon: 'none' })
    return
  }
  if (password.value.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' })
    return
  }
  if (password.value !== confirmPassword.value) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await authApi.createStudentAccount(studentId.value, {
      email: email.value.trim(),
      password: password.value
    })

    uni.showToast({ title: '创建成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error: any) {
    console.error('创建账号失败', error)
    uni.showToast({ title: error.message || '创建失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.header {
  padding: 40rpx 30rpx;
  background: #fff;
}

.title {
  display: block;
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 12rpx;
}

.subtitle {
  font-size: 26rpx;
  color: #999;
}

.student-card {
  display: flex;
  align-items: center;
  margin: 20rpx;
  padding: 30rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  border-radius: 16rpx;
  color: #fff;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  border: 2rpx solid rgba(255, 255, 255, 0.5);
}

.info {
  margin-left: 24rpx;
}

.name {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
}

.no {
  font-size: 26rpx;
  opacity: 0.9;
  margin-top: 4rpx;
}

.form-section {
  margin: 20rpx;
  background: #fff;
  border-radius: 12rpx;
  overflow: hidden;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.form-item:last-child {
  border-bottom: none;
}

.label {
  width: 160rpx;
  font-size: 28rpx;
  color: #333;
  flex-shrink: 0;
}

.input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.tips {
  margin: 20rpx;
  padding: 24rpx;
  background: #FFF8E1;
  border-radius: 12rpx;
}

.tip-item {
  display: block;
  font-size: 24rpx;
  color: #F57C00;
  line-height: 1.8;
}

.submit-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background: #fff;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #fff;
  font-size: 32rpx;
  border-radius: 44rpx;
  border: none;
}

.submit-btn[loading] {
  opacity: 0.7;
}
</style>
