<template>
  <view class="page">
    <view class="top-bg">
      <view class="deco-circle c1"></view>
      <view class="deco-circle c2"></view>
      <view class="deco-circle c3"></view>
    </view>

    <view class="brand-area">
      <view class="logo-box">
        <image class="logo-img" src="/static/logo.png" mode="aspectFit" />
      </view>
      <text class="app-name">易乐航</text>
      <text class="app-slogan">让运动更快乐</text>
    </view>

    <view class="login-card">
      <view class="tab-bar">
        <view
          :class="['tab-item', { active: loginMode === 'password' }]"
          @click="loginMode = 'password'"
        >
          <text class="tab-text">密码登录</text>
        </view>
        <view
          :class="['tab-item', { active: loginMode === 'code' }]"
          @click="loginMode = 'code'"
        >
          <text class="tab-text">验证码登录</text>
        </view>
        <view class="tab-indicator" :style="{ left: loginMode === 'password' ? '0' : '50%' }"></view>
      </view>

      <view class="form-area">
        <view class="input-group">
          <text class="input-label">手机号</text>
          <view class="input-wrapper">
            <input
              class="input-field"
              type="number"
              v-model="phone"
              placeholder="请输入手机号"
              :maxlength="11"
              placeholder-class="placeholder"
            />
          </view>
        </view>

        <view v-if="loginMode === 'password'" class="input-group">
          <text class="input-label">密码</text>
          <view class="input-wrapper">
            <input
              class="input-field"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="请输入密码"
              placeholder-class="placeholder"
            />
            <view class="input-suffix" @click="showPassword = !showPassword">
              <text>{{ showPassword ? '隐藏' : '显示' }}</text>
            </view>
          </view>
        </view>

        <view v-else class="input-group">
          <text class="input-label">验证码</text>
          <view class="input-wrapper code-wrapper">
            <input
              class="input-field"
              v-model="code"
              placeholder="请输入验证码"
              maxlength="6"
              placeholder-class="placeholder"
            />
            <button
              class="code-btn"
              :class="{ disabled: codeSending || codeCountdown > 0 }"
              @click="sendCode"
              :disabled="codeSending || codeCountdown > 0"
            >
              {{ codeCountdown > 0 ? `${codeCountdown}s` : '获取验证码' }}
            </button>
          </view>
        </view>

        <button class="login-btn" @click="handleLogin" :loading="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <view class="quick-links">
          <text class="link-text" @click="goRegister">注册账号</text>
          <text v-if="loginMode === 'password'" class="link-text" @click="forgotPassword">忘记密码</text>
        </view>
      </view>
    </view>

    <view class="other-login">
      <view class="divider">
        <view class="line"></view>
        <text class="divider-text">其他登录方式</text>
        <view class="line"></view>
      </view>
      <view class="social-login">
        <view class="social-btn wechat" @click="wechatLogin">
          <text class="social-icon">微信</text>
        </view>
      </view>
    </view>

    <view class="agreement">
      <view class="checkbox-area" @click="agreed = !agreed">
        <view :class="['checkbox', { checked: agreed }]">
          <text v-if="agreed" class="check-icon">✓</text>
        </view>
      </view>
      <text class="agree-text">我已阅读并同意</text>
      <text class="agree-link" @click="viewAgreement('user')">《用户协议》</text>
      <text class="agree-text">和</text>
      <text class="agree-link" @click="viewAgreement('privacy')">《隐私政策》</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const loginMode = ref<'password' | 'code'>('password')
const phone = ref('')
const password = ref('')
const code = ref('')
const showPassword = ref(false)
const loading = ref(false)
const agreed = ref(false)
const codeSending = ref(false)
const codeCountdown = ref(0)

async function sendCode() {
  if (!phone.value) {
    uni.showToast({ title: '请输入手机号', icon: 'none' })
    return
  }

  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(phone.value)) {
    uni.showToast({ title: '手机号格式不正确', icon: 'none' })
    return
  }

  codeSending.value = true
  try {
    await userStore.sendSmsCode(phone.value)
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    codeCountdown.value = 60
    const timer = setInterval(() => {
      codeCountdown.value--
      if (codeCountdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (error) {
    uni.showToast({ title: '验证码发送失败', icon: 'none' })
  } finally {
    codeSending.value = false
  }
}

async function handleLogin() {
  if (!phone.value) {
    uni.showToast({ title: '请输入手机号', icon: 'none' })
    return
  }

  if (loginMode.value === 'password' && !password.value) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  if (loginMode.value === 'code' && !code.value) {
    uni.showToast({ title: '请输入验证码', icon: 'none' })
    return
  }

  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议与隐私政策', icon: 'none' })
    return
  }

  loading.value = true
  try {
    if (loginMode.value === 'password') {
      await userStore.login(phone.value, password.value)
    } else {
      await userStore.loginWithSms(phone.value, code.value)
    }
    await userStore.fetchUserInfo()
    uni.switchTab({ url: '/pages/index/index' })
  } catch (error: any) {
    uni.showToast({ title: error.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goRegister() {
  uni.navigateTo({ url: '/pages/user/register' })
}

function forgotPassword() {
  uni.showToast({ title: '请联系管理员重置密码', icon: 'none' })
}

function wechatLogin() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function viewAgreement(type: 'user' | 'privacy') {
  uni.showToast({ title: type === 'user' ? '用户协议开发中' : '隐私政策开发中', icon: 'none' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #fff;
  padding-bottom: 80rpx;
}

.top-bg {
  height: 260rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  position: relative;
  overflow: hidden;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.deco-circle.c1 {
  width: 180rpx;
  height: 180rpx;
  top: -60rpx;
  right: -40rpx;
}

.deco-circle.c2 {
  width: 120rpx;
  height: 120rpx;
  bottom: 40rpx;
  left: -40rpx;
}

.deco-circle.c3 {
  width: 80rpx;
  height: 80rpx;
  bottom: 120rpx;
  right: 80rpx;
}

.brand-area {
  margin-top: -120rpx;
  text-align: center;
}

.logo-box {
  width: 140rpx;
  height: 140rpx;
  background: #fff;
  margin: 0 auto;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.08);
}

.logo-img {
  width: 100rpx;
  height: 100rpx;
}

.app-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
  margin-top: 16rpx;
  display: block;
}

.app-slogan {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.login-card {
  margin: 30rpx;
  padding: 30rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.06);
}

.tab-bar {
  display: flex;
  position: relative;
  margin-bottom: 20rpx;
  background: #f6f6f6;
  border-radius: 30rpx;
  overflow: hidden;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: #666;
  z-index: 1;
}

.tab-item.active {
  color: #FF8800;
  font-weight: 600;
}

.tab-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 50%;
  background: #fff;
  border-radius: 30rpx;
  transition: left 0.2s ease;
}

.form-area .input-group {
  margin-bottom: 20rpx;
}

.input-label {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 8rpx;
  display: block;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f6f6f6;
  border-radius: 16rpx;
  padding: 0 20rpx;
}

.input-field {
  flex: 1;
  height: 90rpx;
  font-size: 28rpx;
  color: #333;
}

.input-suffix {
  font-size: 24rpx;
  color: #FF8800;
}

.code-wrapper .code-btn {
  margin-left: 12rpx;
  font-size: 24rpx;
  color: #FF8800;
  background: transparent;
}

.code-wrapper .code-btn.disabled {
  color: #ccc;
}

.login-btn {
  height: 90rpx;
  border-radius: 16rpx;
  background: #FF8800;
  color: #fff;
  font-size: 30rpx;
  margin-top: 10rpx;
}

.quick-links {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
}

.link-text {
  font-size: 24rpx;
  color: #999;
}

.other-login {
  margin: 20rpx 30rpx;
  text-align: center;
}

.divider {
  display: flex;
  align-items: center;
  gap: 10rpx;
  color: #999;
  font-size: 22rpx;
  margin-bottom: 20rpx;
}

.divider .line {
  flex: 1;
  height: 1rpx;
  background: #eee;
}

.social-login {
  display: flex;
  justify-content: center;
}

.social-btn {
  width: 90rpx;
  height: 90rpx;
  border-radius: 50%;
  background: #f6f6f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  color: #07C160;
}

.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #999;
  margin-top: 20rpx;
  padding: 0 30rpx;
  flex-wrap: wrap;
}

.checkbox {
  width: 28rpx;
  height: 28rpx;
  border-radius: 6rpx;
  border: 1rpx solid #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox.checked {
  background: #FF8800;
  border-color: #FF8800;
  color: #fff;
}

.agree-link {
  color: #FF8800;
}
</style>
