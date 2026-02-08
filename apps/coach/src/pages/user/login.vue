<template>
  <view class="page">
    <view class="hero">
      <view class="hero-bubble bubble-1"></view>
      <view class="hero-bubble bubble-2"></view>
      <view class="hero-bubble bubble-3"></view>
      <view class="brand">
        <text class="title">Coach Studio</text>
        <text class="subtitle">Yilehang Coach Side</text>
      </view>
    </view>

    <view class="card">
      <view class="field">
        <text class="label">Account</text>
        <view class="input-wrap">
          <input
            v-model="account"
            class="input"
            type="text"
            maxlength="50"
            placeholder="Phone or Email"
            placeholder-class="placeholder"
          />
        </view>
      </view>

      <view class="field">
        <text class="label">Password</text>
        <view class="input-wrap">
          <input
            v-model="password"
            class="input"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Enter password"
            placeholder-class="placeholder"
          />
          <text class="suffix" @click="showPassword = !showPassword">
            {{ showPassword ? 'Hide' : 'Show' }}
          </text>
        </view>
      </view>

      <button class="submit" :loading="loading" :disabled="!canLogin" @click="handleLogin">
        {{ loading ? 'Signing in...' : 'Sign in as Coach' }}
      </button>

      <view class="tips">
        <text>Only coach accounts can login here.</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { authApi } from '@/api'

const account = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)

function validEmail(value: string) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)
}

function validPhone(value: string) {
  return /^1[3-9]\d{9}$/.test(value)
}

const canLogin = computed(() => {
  const v = account.value.trim()
  return (validPhone(v) || validEmail(v)) && password.value.length >= 6
})

async function handleLogin() {
  if (!canLogin.value || loading.value) return

  loading.value = true
  try {
    const res: any = await authApi.login({
      account: account.value.trim(),
      password: password.value
    })

    if (res.user && res.user.role !== 'coach') {
      uni.showToast({ title: 'Only coach accounts are allowed', icon: 'none' })
      return
    }

    uni.setStorageSync('token', res.access_token || res.token)
    uni.showToast({ title: 'Login success', icon: 'success' })

    setTimeout(() => {
      uni.switchTab({ url: '/pages/workbench/index' })
    }, 400)
  } catch (error: any) {
    uni.showToast({ title: error?.message || 'Login failed', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #fff9f0 0%, #ffffff 56%);
  padding-bottom: 56rpx;
}

.hero {
  height: 320rpx;
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
  top: 120rpx;
}

.bubble-3 {
  width: 92rpx;
  height: 92rpx;
  right: 140rpx;
  top: 84rpx;
}

.brand {
  position: relative;
  z-index: 2;
  text-align: center;
  padding-top: 96rpx;
}

.title {
  display: block;
  font-size: 42rpx;
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
  margin: -30rpx 24rpx 0;
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 14rpx 36rpx rgba(255, 136, 0, 0.12);
  padding: 26rpx;
}

.field {
  margin-bottom: 18rpx;
}

.label {
  display: block;
  font-size: 24rpx;
  color: #6f5b43;
  margin-bottom: 10rpx;
}

.input-wrap {
  display: flex;
  align-items: center;
  background: #fff7ed;
  border: 1rpx solid #ffe0b5;
  border-radius: 16rpx;
  padding: 0 18rpx;
}

.input {
  flex: 1;
  height: 88rpx;
  font-size: 28rpx;
  color: #2f2f2f;
  background: transparent;
}

.placeholder {
  color: #c8b08d;
}

.suffix {
  font-size: 24rpx;
  color: #ff8800;
  padding-left: 12rpx;
}

.submit {
  margin-top: 12rpx;
  height: 90rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #ffb347 0%, #ff8800 100%);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}

.submit::after {
  border: none;
}

.submit[disabled] {
  opacity: 0.6;
}

.tips {
  margin-top: 16rpx;
  text-align: center;
  color: #9a8a73;
  font-size: 24rpx;
}
</style>
