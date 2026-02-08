<template>
  <view class="page page-enter">
    <view class="hero anim-fade-up">
      <view class="hero-bubble bubble-1"></view>
      <view class="hero-bubble bubble-2"></view>
      <view class="brand">
        <view class="logo-wrap">
          <text class="logo-icon">🏪</text>
        </view>
        <text class="title">易乐航商家端</text>
        <text class="subtitle">门店核销与数据经营</text>
      </view>
    </view>

    <view class="card anim-fade-up anim-delay-1">
      <view class="field">
        <text class="label">账号</text>
        <view class="input-wrap">
          <input
            v-model="account"
            class="input"
            type="text"
            maxlength="50"
            placeholder="请输入手机号或邮箱"
            placeholder-class="placeholder"
          />
        </view>
      </view>

      <view class="field">
        <text class="label">密码</text>
        <view class="input-wrap">
          <input
            v-model="password"
            class="input"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            placeholder-class="placeholder"
          />
          <text class="suffix" @click="showPassword = !showPassword">
            {{ showPassword ? '隐藏' : '显示' }}
          </text>
        </view>
      </view>

      <button class="submit tap-active" :loading="loading" :disabled="!canLogin" @click="handleLogin">
        {{ loading ? '登录中...' : '登录商家端' }}
      </button>

      <view class="tips">
        <text>仅商家账号可登录，如忘记密码请联系管理员。</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useMerchantStore } from '@/stores/merchant'

const merchantStore = useMerchantStore()

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
    await merchantStore.login(account.value.trim(), password.value)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 400)
  } catch (error: any) {
    console.error('商家登录失败', error)
    uni.showToast({ title: error?.message || '登录失败', icon: 'none' })
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
  height: 360rpx;
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
  top: 148rpx;
}

.brand {
  position: relative;
  z-index: 2;
  text-align: center;
  padding-top: 72rpx;
}

.logo-wrap {
  width: 106rpx;
  height: 106rpx;
  border-radius: 24rpx;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 28rpx rgba(0, 0, 0, 0.1);
}

.logo-icon {
  font-size: 54rpx;
}

.title {
  display: block;
  margin-top: 14rpx;
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
  margin: -40rpx 24rpx 0;
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
  font-size: 23rpx;
  line-height: 1.5;
}
</style>

