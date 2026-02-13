<template>
  <view class="page page-enter anim-page-enter">
    <view class="hero anim-fade-up">
      <view class="hero-bubble bubble-1"></view>
      <view class="hero-bubble bubble-2"></view>
      <view class="hero-bubble bubble-3"></view>
      <view class="brand">
        <image class="logo-fallback" :src="brandLogoSrc" mode="aspectFit" @error="handleLogoError" />
        <text class="title">韧翎成长计划</text>
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
        <button class="wechat-btn" :loading="loading" @tap="wechatLogin">
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
          <wd-icon v-if="agreed" name="check" size="18rpx" color="#ffffff" />
        </view>
        <text class="agreement-text">我已阅读并同意</text>
        <text class="agreement-link" @click="viewAgreement('user')">《用户协议》</text>
        <text class="agreement-text">和</text>
        <text class="agreement-link" @click="viewAgreement('privacy')">《隐私政策》</text>
      </view>
    </view>

    <!-- 角色选择弹窗 -->
    <view v-if="showRoleSelector" class="role-modal" @click="showRoleSelector = false">
      <view class="role-content" @click.stop>
        <text class="role-title">选择您的角色</text>
        <text class="role-subtitle">首次登录，请选择您的身份</text>
        <view class="role-grid">
          <view class="role-item" @click="selectRole('parent')">
            <view class="role-icon">
              <wd-icon name="usergroup" size="34rpx" color="#2563eb" />
            </view>
            <text class="role-name">家长</text>
            <text class="role-desc">管理孩子学习</text>
          </view>
          <view class="role-item" @click="selectRole('student')">
            <view class="role-icon">
              <wd-icon name="books" size="34rpx" color="#2563eb" />
            </view>
            <text class="role-name">学员</text>
            <text class="role-desc">参与训练课程</text>
          </view>
          <view class="role-item" @click="selectRole('coach')">
            <view class="role-icon">
              <wd-icon name="dashboard" size="34rpx" color="#2563eb" />
            </view>
            <text class="role-name">教练</text>
            <text class="role-desc">教学与管理</text>
          </view>
          <view class="role-item" @click="selectRole('merchant')">
            <view class="role-icon">
              <wd-icon name="shop" size="34rpx" color="#2563eb" />
            </view>
            <text class="role-name">商家</text>
            <text class="role-desc">商品与核销</text>
          </view>
        </view>
      </view>
    </view>

    <view class="intro-section anim-fade-up anim-delay-2">
      <view class="intro-card">
        <text class="intro-title">为什么选择韧翎成长计划</text>
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
import { onUnmounted, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { routeByRole } from '@/utils/role-guard'
import { BRAND_LOGO_INLINE_DATA_URI, BRAND_LOGO_PROJECT_PATH } from '@/utils/brand-logo'
import { safeNavigate } from '@/utils/safe-nav'
import { trackError, trackEvent } from '@/utils/telemetry'

const userStore = useUserStore()
const permissionStore = usePermissionStore()
const loading = ref(false)
const agreed = ref(false)
const loginMode = ref<'wechat' | 'account' | 'email'>('wechat')
const brandLogoSrc = ref(BRAND_LOGO_PROJECT_PATH)

function handleLogoError() {
  if (brandLogoSrc.value !== BRAND_LOGO_INLINE_DATA_URI) {
    brandLogoSrc.value = BRAND_LOGO_INLINE_DATA_URI
  }
}

// 账号登录
const account = ref('')
const password = ref('')
const showPassword = ref(false)

// 邮箱验证码登录
const email = ref('')
const emailCode = ref('')
const sendingCode = ref(false)
const countdown = ref(0)
let countdownTimer: ReturnType<typeof setInterval> | null = null

// 角色选择
const showRoleSelector = ref(false)
const pendingRegister = ref<{ email?: string; wechatOpenid?: string; nickname?: string } | null>(null)

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

function clearCountdownTimer() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

onUnmounted(() => {
  clearCountdownTimer()
})

// ========== 微信登录 ==========
function isWechatCodeExpired(error: any) {
  const msg = String(error?.message || error?.detail || error?.errMsg || '')
  return msg.includes('40029') || msg.includes('invalid code') || msg.includes('登录凭证已过期')
}

function parseWechatRoleRequired(error: any) {
  const detail = error?.detail
  const code = detail?.code || (typeof detail === 'string' ? detail : '')
  const msg = String(error?.message || detail?.message || detail || '')
  const required =
    error?.statusCode === 409 &&
    (
      code === 'WECHAT_ROLE_REQUIRED' ||
      msg.includes('WECHAT_ROLE_REQUIRED') ||
      msg.includes('role selection') ||
      msg.includes('首次')
    )

  const wechatOpenid = String(
    detail?.wechat_openid || detail?.openid || detail?.wechatOpenid || error?.wechat_openid || ''
  ).trim()

  return {
    required,
    wechatOpenid,
    nickname: detail?.nickname || '微信用户'
  }
}

async function wechatLogin() {
  if (loading.value) return
  if (!ensureAgreement()) return
  trackEvent('auth.wechat.attempt', { mode: 'wechat' })

  // #ifdef MP-WEIXIN
  loading.value = true
  try {
    const loginRes: any = await new Promise((resolve, reject) => {
      uni.login({ timeout: 10000, success: resolve, fail: reject })
    })

    if (!loginRes?.code) {
      throw new Error('未获取到微信登录凭证')
    }

    const deviceId = getOrCreateDeviceId()
    try {
      await userStore.wechatLogin(loginRes.code, deviceId)
    } catch (error: any) {
      if (!isWechatCodeExpired(error)) throw error

      const retryRes: any = await new Promise((resolve, reject) => {
        uni.login({ timeout: 10000, success: resolve, fail: reject })
      })
      if (!retryRes?.code) throw new Error('微信登录凭证已失效，请重试')
      await userStore.wechatLogin(retryRes.code, deviceId)
    }

    const user = await userStore.fetchUserInfo()
    await permissionStore.init()
    trackEvent('auth.wechat.success', { role: user?.role || '' })
    routeByRole(user?.role)
  } catch (error: any) {
    const parsed = parseWechatRoleRequired(error)
    if (parsed.required) {
      const wechatOpenid = parsed.wechatOpenid
      if (!wechatOpenid) {
        trackError('auth.wechat.role_required_missing_openid', error)
        uni.showToast({ title: '微信登录信息不完整，请重试', icon: 'none' })
        return
      }
      pendingRegister.value = {
        wechatOpenid,
        nickname: parsed.nickname
      }
      showRoleSelector.value = true
      trackEvent('auth.wechat.role_required')
    } else {
      const msg = error?.errMsg || error?.message || '微信登录失败'
      trackError('auth.wechat.fail', error, { message: msg })
      uni.showToast({ title: msg, icon: 'none' })
    }
  } finally {
    loading.value = false
  }
  // #endif
}

// ========== 账号密码登录 ==========
async function accountLogin() {
  if (loading.value) return
  if (!ensureAgreement()) return
  trackEvent('auth.account.attempt', { mode: 'account' })

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
    await permissionStore.init()
    trackEvent('auth.account.success', { role: user?.role || '' })
    routeByRole(user?.role)
  } catch (error: any) {
    if (error?.message?.includes('USER_NOT_REGISTERED') || error?.message?.includes('404')) {
      pendingRegister.value = { email: account.value.trim() }
      showRoleSelector.value = true
      trackEvent('auth.account.role_required')
    } else {
      trackError('auth.account.fail', error)
      uni.showToast({ title: error?.message || '登录失败', icon: 'none' })
    }
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
  trackEvent('auth.email.code.attempt')
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

    clearCountdownTimer()
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        countdown.value = 0
        clearCountdownTimer()
      }
    }, 1000)
    trackEvent('auth.email.code.success')
  } catch (error: any) {
    trackError('auth.email.code.fail', error)
    uni.showToast({ title: error?.message || '验证码发送失败', icon: 'none' })
  } finally {
    sendingCode.value = false
  }
}

async function emailLogin() {
  if (loading.value) return
  if (!ensureAgreement()) return
  trackEvent('auth.email.attempt', { mode: 'email' })

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
    trackEvent('auth.email.success', { role: user?.role || '' })
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      routeByRole(user?.role)
    }, 400)
  } catch (error: any) {
    if (error?.message?.includes('USER_NOT_REGISTERED') || error?.message?.includes('404')) {
      pendingRegister.value = { email: email.value }
      showRoleSelector.value = true
      trackEvent('auth.email.role_required')
    } else {
      trackError('auth.email.fail', error)
      uni.showToast({ title: error?.message || '登录失败', icon: 'none' })
    }
  } finally {
    loading.value = false
  }
}

// ========== 角色选择 ==========
async function selectRole(role: string) {
  if (!pendingRegister.value) return

  showRoleSelector.value = false
  loading.value = true
  trackEvent('auth.register.role.attempt', { role })

  try {
    await userStore.registerWithRole(
      pendingRegister.value.email || '',
      pendingRegister.value.wechatOpenid || '',
      role,
      pendingRegister.value.nickname
    )
    const user = await userStore.fetchUserInfo()
    await permissionStore.init()
    trackEvent('auth.register.role.success', { role: user?.role || role })
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      routeByRole(user?.role)
    }, 400)
  } catch (error: any) {
    trackError('auth.register.role.fail', error, { role })
    uni.showToast({ title: error?.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
    pendingRegister.value = null
  }
}

// ========== 导航 ==========
function goRegister() {
  safeNavigate('/pages/user/register')
}

function goIntro() {
  safeNavigate('/pages/brand/intro')
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
  display: block;
  overflow: hidden;
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

.role-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.role-content {
  width: 600rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx 30rpx;
}

.role-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
  text-align: center;
}

.role-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #999;
  text-align: center;
}

.role-grid {
  margin-top: 30rpx;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.role-item {
  background: #f7f8fa;
  border-radius: 16rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  border: 1rpx solid rgba(226, 232, 240, 0.9);
  transition: transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease;
  cursor: pointer;
}

.role-item:active {
  transform: translateY(2rpx);
  border-color: rgba(147, 197, 253, 0.88);
  box-shadow: 0 8rpx 18rpx rgba(37, 99, 235, 0.14);
}

.role-icon {
  width: 68rpx;
  height: 68rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #eff6ff, #f3f8ff);
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #333;
}

.role-desc {
  font-size: 22rpx;
  color: #999;
}
</style>
