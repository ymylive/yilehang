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
      </view>

      <template v-if="loginMode === 'wechat'">
        <text class="card-title">微信登录</text>
        <text class="card-subtitle">授权后自动同步微信昵称和头像</text>

        <!-- #ifdef MP-WEIXIN -->
        <button class="wechat-btn" :loading="loading" @click="wechatLogin">
          {{ loading ? '登录中...' : '微信一键登录' }}
        </button>
        <!-- #endif -->

        <!-- #ifndef MP-WEIXIN -->
        <button class="wechat-btn" :loading="loading" @click="wechatLogin">
          {{ loading ? '登录中...' : '微信一键登录' }}
        </button>
        <!-- #endif -->
      </template>

      <template v-else>
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

const userStore = useUserStore()
const loading = ref(false)
const agreed = ref(false)
const loginMode = ref<'wechat' | 'account'>('wechat')
const account = ref('')
const password = ref('')
const showPassword = ref(false)

function ensureAgreement() {
  if (!agreed.value) {
    uni.showToast({ title: '请先勾选用户协议', icon: 'none' })
    return false
  }
  return true
}

function getOrCreateDeviceId() {
  const key = 'device_id'
  const existing = uni.getStorageSync(key)
  if (existing) return String(existing)

  const generated = `dev-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
  uni.setStorageSync(key, generated)
  return generated
}

function routeByRole(role?: string) {
  if (role === 'student') {
    uni.switchTab({ url: '/pages/schedule/index' })
    return
  }

  if (role === 'coach') {
    uni.navigateTo({ url: '/pages/coach/workbench/index' })
    return
  }

  if (role === 'merchant') {
    uni.navigateTo({ url: '/pages/merchant/index' })
    return
  }

  uni.switchTab({ url: '/pages/index/index' })
}

async function doWechatOpenidLogin(withProfile = true) {
  const loginRes: any = await new Promise((resolve, reject) => {
    uni.login({ provider: 'weixin', success: resolve, fail: reject })
  })

  if (!loginRes?.code) {
    throw new Error('未获取到微信登录凭证')
  }

  let userInfo: Record<string, any> | undefined
  if (withProfile) {
    try {
      const profileRes: any = await new Promise((resolve, reject) => {
        uni.getUserProfile({
          desc: '用于完善用户资料',
          success: resolve,
          fail: reject
        })
      })
      userInfo = profileRes?.userInfo
    } catch (error: any) {
      throw new Error(error?.errMsg?.includes('deny') ? '请允许获取微信信息后再登录' : '获取微信信息失败，请重试')
    }
  }

  const deviceId = getOrCreateDeviceId()
  await userStore.wechatLogin(loginRes.code, userInfo, deviceId)
  const user = await userStore.fetchUserInfo()
  routeByRole(user?.role)
}

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

function goRegister() {
  uni.navigateTo({ url: '/pages/user/register' })
}

function goIntro() {
  uni.navigateTo({ url: '/pages/brand/intro' })
}

async function wechatLogin() {
  if (loading.value) return
  if (!ensureAgreement()) return

  // #ifndef MP-WEIXIN
  uni.showToast({ title: '请在微信小程序中使用微信登录', icon: 'none' })
  // #endif

  // #ifdef MP-WEIXIN
  loading.value = true
  try {
    await doWechatOpenidLogin(true)
  } catch (error: any) {
    uni.showToast({ title: error?.message || '微信登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
  // #endif
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
  grid-template-columns: 1fr 1fr;
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
</style>
