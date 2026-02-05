<template>
  <view class="page">
    <!-- Top decor -->
    <view class="top-decor">
      <view class="circle circle1"></view>
      <view class="circle circle2"></view>
      <view class="circle circle3"></view>
    </view>

    <!-- Back -->
    <view class="nav-back" @click="goLogin">
      <text class="back-icon">←</text>
      <text class="back-text">返回登录</text>
    </view>

    <!-- Header -->
    <view class="header-area">
      <text class="page-title">创建账号</text>
      <text class="page-subtitle">加入易乐航，开启运动之旅</text>
    </view>

    <!-- Form -->
    <view class="form-card">
      <view class="step-indicator">
        <view :class="['step', { active: true, done: step > 1 }]">
          <text class="step-num">1</text>
          <text class="step-label">基本信息</text>
        </view>
        <view class="step-line" :class="{ active: step > 1 }"></view>
        <view :class="['step', { active: step >= 2, done: step > 2 }]">
          <text class="step-num">2</text>
          <text class="step-label">短信验证</text>
        </view>
        <view class="step-line" :class="{ active: step > 2 }"></view>
        <view :class="['step', { active: step >= 3 }]">
          <text class="step-num">3</text>
          <text class="step-label">设置密码</text>
        </view>
      </view>

      <!-- Step 1 -->
      <view v-show="step === 1" class="step-content">
        <view class="input-group">
          <view class="input-label">
            <text class="label-icon">??</text>
            <text class="label-text">手机号</text>
          </view>
          <view class="input-box">
            <input
              class="input-field"
              type="number"
              v-model="phone"
              placeholder="请输入11位手机号"
              maxlength="11"
              placeholder-class="placeholder"
            />
            <text v-if="phone && validatePhone(phone)" class="input-check">?</text>
          </view>
        </view>

        <view class="input-group">
          <view class="input-label">
            <text class="label-icon">??</text>
            <text class="label-text">昵称</text>
            <text class="label-optional">(选填)</text>
          </view>
          <view class="input-box">
            <input
              class="input-field"
              v-model="nickname"
              placeholder="给自己取个名字吧"
              maxlength="20"
              placeholder-class="placeholder"
            />
          </view>
        </view>

        <button class="next-btn" @click="nextStep">
          <text class="btn-text">下一步</text>
          <text class="btn-arrow">→</text>
        </button>
      </view>

      <!-- Step 2 -->
      <view v-show="step === 2" class="step-content">
        <view class="verify-tip">
          <view class="tip-icon">??</view>
          <text class="tip-title">验证您的手机号</text>
          <text class="tip-desc">验证码将发送至 {{ maskPhone(phone) }}</text>
        </view>

        <view class="code-input-area">
          <view class="code-boxes">
            <view
              v-for="(_, index) in 6"
              :key="index"
              :class="['code-box', { filled: smsCode[index], active: smsCode.length === index }]"
            >
              <text class="code-digit">{{ smsCode[index] || '' }}</text>
            </view>
          </view>
          <input
            class="hidden-input"
            type="number"
            v-model="smsCode"
            maxlength="6"
            @input="onCodeInput"
          />
        </view>

        <view class="resend-area">
          <button
            class="resend-btn"
            :class="{ disabled: countdown > 0 }"
            @click="sendCode"
            :disabled="countdown > 0"
          >
            {{ countdown > 0 ? `${countdown}秒后重新发送` : '发送验证码' }}
          </button>
        </view>

        <view class="step-btns">
          <button class="prev-btn" @click="prevStep">
            <text>← 上一步</text>
          </button>
          <button class="next-btn" @click="nextStep">
            <text class="btn-text">下一步</text>
            <text class="btn-arrow">→</text>
          </button>
        </view>
      </view>

      <!-- Step 3 -->
      <view v-show="step === 3" class="step-content">
        <view class="input-group">
          <view class="input-label">
            <text class="label-icon">??</text>
            <text class="label-text">设置密码</text>
          </view>
          <view class="input-box">
            <input
              class="input-field"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="6-20位密码"
              maxlength="20"
              placeholder-class="placeholder"
            />
            <view class="toggle-pwd" @click="showPassword = !showPassword">
              {{ showPassword ? '??' : '??' }}
            </view>
          </view>
          <view class="pwd-strength" v-if="password">
            <view class="strength-bars">
              <view :class="['bar', { active: passwordStrength >= 1 }]" />
              <view :class="['bar', { active: passwordStrength >= 2 }]" />
              <view :class="['bar', { active: passwordStrength >= 3 }]" />
            </view>
            <text class="strength-text">{{ strengthText }}</text>
          </view>
        </view>

        <view class="input-group">
          <view class="input-label">
            <text class="label-icon">??</text>
            <text class="label-text">确认密码</text>
          </view>
          <view class="input-box">
            <input
              class="input-field"
              :type="showPassword ? 'text' : 'password'"
              v-model="confirmPassword"
              placeholder="再次输入密码"
              maxlength="20"
              placeholder-class="placeholder"
            />
            <text v-if="confirmPassword && password === confirmPassword" class="input-check">?</text>
          </view>
        </view>

        <view class="step-btns">
          <button class="prev-btn" @click="prevStep">
            <text>← 上一步</text>
          </button>
          <button class="submit-btn" @click="handleRegister" :loading="loading">
            <text class="btn-text">{{ loading ? '注册中...' : '完成注册' }}</text>
            <text class="btn-icon">??</text>
          </button>
        </view>
      </view>
    </view>

    <!-- Agreement -->
    <view class="agreement-area">
      <view class="checkbox-wrap" @click="agreed = !agreed">
        <view :class="['custom-checkbox', { checked: agreed }]">
          <text v-if="agreed">?</text>
        </view>
      </view>
      <text class="agreement-text">注册即表示同意</text>
      <text class="agreement-link" @click="viewAgreement('user')">《用户协议》</text>
      <text class="agreement-text">和</text>
      <text class="agreement-link" @click="viewAgreement('privacy')">《隐私政策》</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const step = ref(1)
const phone = ref('')
const smsCode = ref('')
const password = ref('')
const confirmPassword = ref('')
const nickname = ref('')
const showPassword = ref(false)
const loading = ref(false)
const agreed = ref(true)
const countdown = ref(0)

let timer: number | null = null

function validatePhone(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value)
}

function maskPhone(value: string): string {
  if (!value) return ''
  return value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const passwordStrength = computed(() => {
  if (!password.value) return 0
  let strength = 0
  if (password.value.length >= 6) strength++
  if (/[A-Z]/.test(password.value) && /[a-z]/.test(password.value)) strength++
  if (/\d/.test(password.value) && /[^a-zA-Z0-9]/.test(password.value)) strength++
  return strength
})

const strengthText = computed(() => {
  const texts = ['', '弱', '中', '强']
  return texts[passwordStrength.value]
})

function onCodeInput() {
  if (smsCode.value.length === 6) {
    // Auto step if needed
  }
}

function nextStep() {
  if (step.value === 1) {
    if (!phone.value) {
      uni.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }
    if (!validatePhone(phone.value)) {
      uni.showToast({ title: '手机号格式不正确', icon: 'none' })
      return
    }
    step.value = 2
    if (countdown.value === 0) {
      sendCode()
    }
  } else if (step.value === 2) {
    if (!smsCode.value || smsCode.value.length !== 6) {
      uni.showToast({ title: '请输入6位验证码', icon: 'none' })
      return
    }
    step.value = 3
  }
}

function prevStep() {
  if (step.value > 1) {
    step.value--
  }
}

async function sendCode() {
  if (countdown.value > 0) return

  try {
    await userStore.sendSmsCode(phone.value)
    uni.showToast({ title: '验证码已发送', icon: 'success' })

    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0 && timer) {
        clearInterval(timer)
        timer = null
      }
    }, 1000) as unknown as number
  } catch (error: any) {
    uni.showToast({ title: error.message || '发送失败', icon: 'none' })
  }
}

async function handleRegister() {
  if (!password.value) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
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
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await userStore.registerWithSms(phone.value, smsCode.value, password.value, 'parent', nickname.value || undefined)
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1200)
  } catch (error: any) {
    uni.showToast({ title: error.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goLogin() {
  uni.navigateBack()
}

function viewAgreement(type: string) {
  uni.navigateTo({ url: `/pages/user/agreement?type=${type}` })
}
</script>

<style scoped>
/* Design variables */
page {
  --c-primary: #FF8800;
  --c-secondary: #FFB347;
  --c-accent: #4FA4F3;
  --c-bg-body: #FFFBF5;
  --c-bg-card: #FFFFFF;
  --c-bg-input: #FFF8E1;
  --c-text-main: #2D2D2D;
  --c-text-sub: #666666;
  --c-text-light: #999999;
  --radius-sm: 20rpx;
  --radius-md: 40rpx;
  --radius-lg: 50rpx;
}

.page {
  min-height: 100vh;
  background: var(--c-bg-body);
  position: relative;
  padding-bottom: 40rpx;
}

.top-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 350rpx;
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
  border-radius: 0 0 60rpx 60rpx;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle1 {
  width: 300rpx;
  height: 300rpx;
  top: -150rpx;
  right: -50rpx;
}

.circle2 {
  width: 200rpx;
  height: 200rpx;
  top: 50rpx;
  left: -80rpx;
}

.circle3 {
  width: 150rpx;
  height: 150rpx;
  top: 100rpx;
  right: 100rpx;
  background: rgba(255, 255, 255, 0.15);
}

.nav-back {
  display: flex;
  align-items: center;
  padding: 40rpx;
  position: relative;
  z-index: 10;
}

.back-icon {
  font-size: 44rpx;
  color: #FFFFFF;
  margin-right: 12rpx;
}

.back-text {
  font-size: 30rpx;
  color: #FFFFFF;
  font-weight: 500;
}

.header-area {
  padding: 0 40rpx 40rpx;
  position: relative;
  z-index: 10;
}

.page-title {
  font-size: 52rpx;
  font-weight: 800;
  color: #FFFFFF;
  display: block;
}

.page-subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 12rpx;
}

.form-card {
  margin: 0 30rpx;
  background: #FFFFFF;
  border-radius: var(--radius-md);
  padding: 40rpx;
  box-shadow: 0 20rpx 60rpx rgba(255, 136, 0, 0.15);
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 50rpx;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-num {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F5F5F5;
  color: var(--c-text-light);
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.step.active .step-num {
  background: linear-gradient(135deg, #FFB347, #FF8800);
  color: #FFFFFF;
  box-shadow: 0 8rpx 20rpx rgba(255, 136, 0, 0.3);
}

.step.done .step-num {
  background: var(--c-secondary);
  color: #FFFFFF;
}

.step-label {
  font-size: 22rpx;
  color: var(--c-text-light);
  margin-top: 10rpx;
  white-space: nowrap;
}

.step.active .step-label {
  color: var(--c-primary);
  font-weight: 600;
}

.step-line {
  width: 80rpx;
  height: 4rpx;
  background: #F5F5F5;
  margin: 0 16rpx;
  margin-bottom: 30rpx;
  border-radius: 2rpx;
  transition: all 0.3s ease;
}

.step-line.active {
  background: linear-gradient(90deg, #FFB347, #FF8800);
}

.step-content {
  min-height: 400rpx;
}

.input-group {
  margin-bottom: 36rpx;
}

.input-label {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.label-icon {
  font-size: 36rpx;
  margin-right: 12rpx;
}

.label-text {
  font-size: 30rpx;
  color: var(--c-text-main);
  font-weight: 600;
}

.label-optional {
  font-size: 24rpx;
  color: var(--c-text-light);
  margin-left: 8rpx;
}

.input-box {
  display: flex;
  align-items: center;
  background: var(--c-bg-input);
  border-radius: var(--radius-sm);
  padding: 0 30rpx;
  height: 110rpx;
  border: 3rpx solid transparent;
  transition: all 0.3s ease;
}

.input-box:focus-within {
  border-color: var(--c-secondary);
  background: #FFFFFF;
  box-shadow: 0 0 0 8rpx rgba(255, 179, 71, 0.15);
}

.input-field {
  flex: 1;
  height: 100%;
  font-size: 34rpx;
  color: var(--c-text-main);
}

.placeholder {
  color: var(--c-text-light);
  font-size: 32rpx;
}

.input-check {
  font-size: 36rpx;
  color: var(--c-primary);
}

.toggle-pwd {
  font-size: 40rpx;
  padding: 10rpx;
}

.pwd-strength {
  display: flex;
  align-items: center;
  margin-top: 16rpx;
}

.strength-bars {
  display: flex;
  gap: 8rpx;
}

.bar {
  width: 60rpx;
  height: 8rpx;
  background: #F5F5F5;
  border-radius: 4rpx;
  transition: all 0.3s ease;
}

.bar.active:nth-child(1) { background: #FFD180; }
.bar.active:nth-child(2) { background: var(--c-secondary); }
.bar.active:nth-child(3) { background: var(--c-primary); }

.strength-text {
  font-size: 24rpx;
  color: var(--c-text-sub);
  margin-left: 16rpx;
}

.verify-tip {
  text-align: center;
  padding: 30rpx 0;
}

.tip-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.tip-title {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--c-text-main);
  display: block;
  margin-bottom: 12rpx;
}

.tip-desc {
  font-size: 28rpx;
  color: var(--c-text-sub);
}

.code-input-area {
  position: relative;
  margin: 40rpx 0;
}

.code-boxes {
  display: flex;
  justify-content: center;
  gap: 20rpx;
}

.code-box {
  width: 90rpx;
  height: 110rpx;
  background: var(--c-bg-input);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3rpx solid transparent;
  transition: all 0.2s ease;
}

.code-box.active {
  border-color: var(--c-primary);
  background: #FFFFFF;
  box-shadow: 0 0 0 6rpx rgba(255, 136, 0, 0.15);
}

.code-box.filled {
  background: #FFF3E0;
  border-color: var(--c-secondary);
}

.code-digit {
  font-size: 48rpx;
  font-weight: 700;
  color: var(--c-primary);
}

.hidden-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
}

.resend-area {
  text-align: center;
  margin: 30rpx 0;
}

.resend-btn {
  background: transparent;
  color: var(--c-primary);
  font-size: 30rpx;
  font-weight: 600;
  border: none;
}

.resend-btn.disabled {
  color: var(--c-text-light);
}

.step-btns {
  display: flex;
  gap: 24rpx;
  margin-top: 40rpx;
}

.prev-btn {
  flex: 1;
  height: 100rpx;
  background: #F5F5F5;
  color: var(--c-text-sub);
  font-size: 32rpx;
  border-radius: var(--radius-lg);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.next-btn, .submit-btn {
  flex: 2;
  height: 100rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  border-radius: var(--radius-lg);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 30rpx rgba(255, 136, 0, 0.35);
}

.next-btn:active, .submit-btn:active {
  transform: scale(0.98);
  box-shadow: 0 6rpx 15rpx rgba(255, 136, 0, 0.25);
}

.btn-text {
  font-size: 34rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.btn-arrow, .btn-icon {
  font-size: 36rpx;
  margin-left: 12rpx;
}

.agreement-area {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  padding: 40rpx;
}

.checkbox-wrap {
  padding: 10rpx;
}

.custom-checkbox {
  width: 44rpx;
  height: 44rpx;
  border: 3rpx solid var(--c-secondary);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  transition: all 0.2s ease;
}

.custom-checkbox.checked {
  background: linear-gradient(135deg, #FFB347, #FF8800);
  border-color: var(--c-primary);
}

.custom-checkbox text {
  color: #FFFFFF;
  font-size: 28rpx;
  font-weight: bold;
}

.agreement-text {
  font-size: 26rpx;
  color: var(--c-text-sub);
  margin: 0 4rpx;
}

.agreement-link {
  font-size: 26rpx;
  color: var(--c-primary);
  font-weight: 500;
}
</style>
