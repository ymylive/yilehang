<template>
  <view class="page page-enter anim-page-enter">
    <view class="hero anim-fade-up">
      <view class="hero-bubble bubble-1"></view>
      <view class="hero-bubble bubble-2"></view>
      <view class="hero-bubble bubble-3"></view>
      <view class="brand">
        <view class="logo-fallback">易</view>
        <text class="title">易乐航</text>
        <text class="subtitle">青春运动成长平台</text>
      </view>
    </view>

    <view class="card anim-fade-up anim-delay-1">
      <view class="mode-tabs">
        <view :class="['mode-tab', { active: loginMode === 'wechat' }]" @click="loginMode = 'wechat'">微信登录</view>
        <view :class="['mode-tab', { active: loginMode === 'account' }]" @click="loginMode = 'account'">账号登录</view>
        <view :class="['mode-tab', { active: loginMode === 'email' }]" @click="loginMode = 'email'">邮箱登录</view>
      </view>

      <!-- 微信登录 -->
      <template v-if="loginMode === 'wechat'">
        <text class="card-title">微信登录</text>
        <text class="card-subtitle">微信授权后快速登录</text>

        <!-- #ifdef MP-WEIXIN -->
        <button class="wechat-btn" :loading="loading" @click="wechatLogin">
          {{ loading ? '登录中...' : '微信一键登录' }}
        </button>
        <!-- #endif -->

        <!-- #ifndef MP-WEIXIN -->
        <view class="h5-wechat-tip">
          <text class="tip-text">微信登录仅支持在微信小程序中使用</text>
          <text class="tip-sub">请切换到"账号登录"或"邮箱登录"</text>
        </view>
        <!-- #endif -->
      </template>

      <!-- 账号密码登录 -->
      <template v-else-if="loginMode === 'account'">
        <text class="card-title">账号登录</text>
        <text class="card-subtitle">支持用户名 / 手机号 / 邮箱 + 密码</text>
        <view class="input-box">
          <input class="input-field" v-model="account" placeholder="请输入用户名 / 手机号 / 邮箱" />
        </view>
        <view class="input-box">
          <input class="input-field" :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="请输入密码" />
          <text class="toggle-pwd" @click="showPassword = !showPassword">{{ showPassword ? '隐藏' : '显示' }}</text>
        </view>
        <button class="account-btn" :loading="loading" @click="accountLogin">
          {{ loading ? '登录中...' : '账号登录' }}
        </button>
      </template>

      <!-- 邮箱验证码登录 -->
      <template v-else>
        <text class="card-title">邮箱登录</text>
        <text class="card-subtitle">输入邮箱获取验证码，快速登录</text>
        <view class="input-box">
          <input class="input-field" type="text" v-model="email" placeholder="请输入邮箱地址" />
        </view>
        <view class="input-box code-box-wrap">
          <input class="input-field" type="number" v-model="emailCode" placeholder="请输入验证码" maxlength="6" />
          <button class="code-btn" :disabled="countdown > 0 || sendingCode" @click="sendCode">
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </view>
        <button class="account-btn" :loading="loading" @click="emailLogin">
          {{ loading ? '登录中...' : '邮箱登录' }}
        </button>
      </template>

      <view class="register-entry" @click="goRegister">
        <text class="register-tip">没有账号？</text>
        <text class="register-link">邮箱验证码注册</text>
      </view>

      <view class="agreement">
        <view class="checkbox" :class="{ checked: agreed }" @click="agreed = !agreed">
          <text v-if="agreed">✓</text>
        </view>
        <text class="agreement-text">我已阅读并同意</text>
        <text class="agreement-link" @click="viewAgreement('user')">《用户协议》</text>
        <text class="agreement-text">和</text>
        <text class="agreement-link" @click="viewAgreement('privacy')">《隐私政策》</text>
      </view>
    </view>

    <view class="intro-section anim-fade-up anim-delay-2">
      <view class="intro-card">
        <text class="intro-title">为什么选择易乐航</text>
        <text class="intro-item">• 体育 + 辅导联动，让放学后两小时更高效</text>
        <text class="intro-item">• 训练过程可视化反馈，成长看得见</text>
        <text class="intro-item">• 家长、教练、商家三方协同，形成成长闭环</text>
        <view class="intro-link" @click="goIntro">
          <text>查看平台介绍</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { routeByRole } from '@/utils/role-guard'

const userStore = useUserStore()
const loading = ref(false)
const agreed = ref(false)
const loginMode = ref<'wechat' | 'account' | 'email'>('wechat')

// 账号登录
const account = ref('')
const password = ref('')
const showPassword = ref(false)

// 邮箱验证码登录
const email = ref('')
const emailCode = ref('')
const sendingCode = ref(false)
const countdown = ref(0)

function ensureAgreement() {
  if (!agreed.value) {
    uni.showToast({ title: '请先勾选用户协议', icon: 'none' })
    return false
  }
  return true
}

function validEmail(e: string) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(e)
}

function getOrCreateDeviceId() {
  const key = 'device_id'
  const existing = uni.getStorageSync(key)
  if (existing) return String(existing)

  const generated = `dev-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
  uni.setStorageSync(key, generated)
  return generated
}

// ========== 微信登录 ==========
async function wechatLogin() {
  if (loading.value) return
  if (!ensureAgreement()) return

  // #ifdef MP-WEIXIN
  loading.value = true
  try {
    const loginRes: any = await new Promise((resolve, reject) => {
      uni.login({ provider: 'weixin', success: resolve, fail: reject })
    })

    if (!loginRes?.code) {
      throw new Error('未获取到微信登录凭证')
    }

    // getUserProfile 已被微信废弃，直接用 code 登录
    // 用户信息通过 open-data 组件展示或后续补充
    const deviceId = getOrCreateDeviceId()
    await userStore.wechatLogin(loginRes.code, undefined, deviceId)
    const user = await userStore.fetchUserInfo()
    routeByRole(user?.role)
  } catch (error: any) {
    const msg = error?.errMsg || error?.message || '微信登录失败'
    uni.showToast({ title: msg, icon: 'none' })
  } finally {
    loading.value = false
  }
  // #endif
}

// ========== 账号密码登录 ==========
async function accountLogin() {
  if (loading.value) return
  if (!ensureAgreement()) return

  if (!account.value.trim()) {
    uni.showToast({ title: '请输入用户名/手机号/邮箱', icon: 'none' })
    return
  }
  if (!password.value) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await userStore.login(account.value.trim(), password.value)
    const user = await userStore.fetchUserInfo()
    routeByRole(user?.role)
  } catch (error: any) {
    uni.showToast({ title: error?.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// ========== 邮箱验证码登录 ==========
async function sendCode() {
  if (!validEmail(email.value)) {
    uni.showToast({ title: '请输入正确的邮箱地址', icon: 'none' })
    return
  }

  sendingCode.value = true
  try {
    const res: any = await userStore.sendEmailCode(email.value)
    const delivery = res?.delivery || 'smtp'
    const devCode = res?.devCode

    if ((delivery === 'fallback' || delivery === 'dev') && devCode) {
      uni.showModal({
        title: '开发环境验证码',
        content: `当前邮件通道不可用，临时验证码：${devCode}`,
        showCancel: false
      })
    } else {
      uni.showToast({ title: '验证码已发送', icon: 'success' })
    }
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (error: any) {
    uni.showToast({ title: error?.message || '验证码发送失败', icon: 'none' })
  } finally {
    sendingCode.value = false
  }
}

async function emailLogin() {
  if (loading.value) return
  if (!ensureAgreement()) return

  if (!validEmail(email.value)) {
    uni.showToast({ title: '请输入正确的邮箱地址', icon: 'none' })
    return
  }
  if (!emailCode.value || emailCode.value.length < 4) {
    uni.showToast({ title: '请输入验证码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await userStore.loginWithEmail(email.value, emailCode.value)
    const user = await userStore.fetchUserInfo()
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      routeByRole(user?.role)
    }, 400)
  } catch (error: any) {
    uni.showToast({ title: error?.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// ========== 导航 ==========
function goRegister() {
  uni.navigateTo({ url: '/pages/user/register' })
}

function goIntro() {
  uni.navigateTo({ url: '/pages/brand/intro' })
}

function viewAgreement(type: 'user' | 'privacy') {
  const title = type === 'user' ? '用户协议' : '隐私政策'
  uni.showModal({ title, content: `${title}完善中，敬请期待`, showCancel: false })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #fff9f0 0%, #f8f9fb 56%);
  padding-bottom: calc(56rpx + env(safe-area-inset-bottom));
}

.hero {
  height: 340rpx;
  background: linear-gradient(135deg, #ffb347 0%, #ff8800 100%);
  border-bottom-left-radius: 44rpx;
  border-bottom-right-radius: 44rpx;
  position: relative;
  overflow: hidden;
}

.hero-bubble {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
}

.bubble-1 {
  width: 220rpx;
  height: 220rpx;
  right: -64rpx;
  top: -82rpx;
}

.bubble-2 {
  width: 136rpx;
  height: 136rpx;
  left: -36rpx;
  top: 140rpx;
}

.bubble-3 {
  width: 92rpx;
  height: 92rpx;
  right: 140rpx;
  top: 94rpx;
}

.brand {
  position: relative;
  z-index: 2;
  text-align: center;
  padding-top: calc(env(safe-area-inset-top) + 16rpx);
}

.logo-fallback {
  width: 120rpx;
  height: 120rpx;
  margin: 0 auto;
  border-radius: 26rpx;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ff8800;
  font-size: 54rpx;
  font-weight: 700;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.1);
}

.title {
  display: block;
  margin-top: 16rpx;
  font-size: 40rpx;
  font-weight: 700;
  color: #ffffff;
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.card {
  margin: -22rpx 24rpx 0;
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 14rpx 36rpx rgba(255, 136, 0, 0.12);
  padding: 30rpx 26rpx;
}

.intro-section {
  margin: 18rpx 24rpx 0;
  padding-bottom: 24rpx;
}

.intro-card {
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 10rpx 28rpx rgba(31, 41, 55, 0.08);
  padding: 24rpx;
}

.intro-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #1f2937;
}

.intro-item {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #6b7280;
  line-height: 1.7;
}

.intro-link {
  margin-top: 16rpx;
  height: 68rpx;
  border-radius: 999rpx;
  background: #fff7eb;
  color: #ff8800;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mode-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10rpx;
  margin-bottom: 20rpx;
  background: #fff6e8;
  border-radius: 16rpx;
  padding: 8rpx;
}

.mode-tab {
  height: 64rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #9f8a6e;
}

.mode-tab.active {
  background: #fff;
  color: #ff8800;
  font-weight: 700;
  box-shadow: 0 8rpx 16rpx rgba(255, 136, 0, 0.12);
}

.card-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
  text-align: center;
}

.card-subtitle {
  display: block;
  margin-top: 10rpx;
  text-align: center;
  font-size: 24rpx;
  color: #9f8a6e;
}

.wechat-btn {
  margin-top: 28rpx;
  height: 88rpx;
  border-radius: 999rpx;
  background: #f2fdf5;
  border: 1rpx solid #bee7cb;
  color: #19a34a;
  font-size: 30rpx;
  font-weight: 700;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.wechat-btn::after {
  border: none;
}

.input-box {
  margin-top: 14rpx;
  display: flex;
  align-items: center;
  border-radius: 16rpx;
  background: #f7f8fa;
  padding: 0 20rpx;
}

.input-field {
  flex: 1;
  height: 86rpx;
  font-size: 27rpx;
  color: #333;
}

.toggle-pwd {
  font-size: 24rpx;
  color: #ff8800;
}

.account-btn {
  margin-top: 20rpx;
  height: 88rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #ffb347, #ff8800);
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.account-btn::after {
  border: none;
}

.register-entry {
  margin-top: 18rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8rpx;
}

.register-tip {
  font-size: 22rpx;
  color: #9f8a6e;
}

.register-link {
  font-size: 22rpx;
  color: #ff8800;
}

.agreement {
  margin-top: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6rpx;
}

.checkbox {
  width: 30rpx;
  height: 30rpx;
  border-radius: 8rpx;
  border: 1rpx solid #d9c7ad;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20rpx;
  background: #fff;
}

.checkbox.checked {
  background: #ff8800;
  border-color: #ff8800;
}

.agreement-text {
  font-size: 22rpx;
  color: #9f8a6e;
}

.agreement-link {
  font-size: 22rpx;
  color: #ff8800;
}

.code-box-wrap {
  display: flex;
  align-items: center;
}

.code-box-wrap .code-btn {
  margin-left: 12rpx;
  background: transparent;
  color: #ff8800;
  font-size: 24rpx;
  white-space: nowrap;
  padding: 0 16rpx;
  line-height: 1;
}

.code-box-wrap .code-btn::after {
  border: none;
}

.code-box-wrap .code-btn[disabled] {
  color: #ccc;
}

.h5-wechat-tip {
  margin-top: 28rpx;
  padding: 32rpx 20rpx;
  background: #f7f8fa;
  border-radius: 16rpx;
  text-align: center;
}

.h5-wechat-tip .tip-text {
  display: block;
  font-size: 26rpx;
  color: #999;
}

.h5-wechat-tip .tip-sub {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #bbb;
}
</style>
