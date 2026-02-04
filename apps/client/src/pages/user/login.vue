<template>
  <view class="page">
    <view class="logo-area">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
      <text class="title">易乐航</text>
      <text class="subtitle">ITS智慧体教云平台</text>
    </view>

    <view class="form-area">
      <view class="input-group">
        <text class="label">手机号</text>
        <input
          class="input"
          type="number"
          v-model="phone"
          placeholder="请输入手机号"
          maxlength="11"
        />
      </view>

      <view class="input-group">
        <text class="label">密码</text>
        <input
          class="input"
          :type="showPassword ? 'text' : 'password'"
          v-model="password"
          placeholder="请输入密码"
        />
        <text class="toggle" @click="showPassword = !showPassword">
          {{ showPassword ? '隐藏' : '显示' }}
        </text>
      </view>

      <button class="btn-login" @click="handleLogin" :loading="loading">
        登录
      </button>

      <view class="links">
        <text class="link" @click="goRegister">注册账号</text>
        <text class="link" @click="forgotPassword">忘记密码</text>
      </view>
    </view>

    <view class="other-login">
      <view class="divider">
        <text>其他登录方式</text>
      </view>
      <view class="login-icons">
        <view class="login-icon wechat" @click="wechatLogin">
          <text>微信</text>
        </view>
      </view>
    </view>

    <view class="agreement">
      <checkbox :checked="agreed" @click="agreed = !agreed" />
      <text>我已阅读并同意</text>
      <text class="link" @click="viewAgreement('user')">《用户协议》</text>
      <text>和</text>
      <text class="link" @click="viewAgreement('privacy')">《隐私政策》</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const agreed = ref(false)

async function handleLogin() {
  if (!phone.value) {
    uni.showToast({ title: '请输入手机号', icon: 'none' })
    return
  }
  if (!password.value) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await userStore.login(phone.value, password.value)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1500)
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
  uni.showToast({ title: '请联系客服重置密码', icon: 'none' })
}

function wechatLogin() {
  // #ifdef MP-WEIXIN
  uni.login({
    provider: 'weixin',
    success: async (res) => {
      try {
        // await userStore.wechatLogin(res.code)
        uni.showToast({ title: '微信登录功能开发中', icon: 'none' })
      } catch (error) {
        uni.showToast({ title: '微信登录失败', icon: 'none' })
      }
    }
  })
  // #endif

  // #ifndef MP-WEIXIN
  uni.showToast({ title: '请在微信小程序中使用', icon: 'none' })
  // #endif
}

function viewAgreement(type: string) {
  uni.navigateTo({ url: `/pages/user/agreement?type=${type}` })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #fff;
  padding: 60rpx 40rpx;
  display: flex;
  flex-direction: column;
}

.logo-area {
  text-align: center;
  padding: 60rpx 0;
}

.logo {
  width: 160rpx;
  height: 160rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #4CAF50;
  display: block;
  margin-top: 20rpx;
}

.subtitle {
  font-size: 26rpx;
  color: #999;
  margin-top: 10rpx;
}

.form-area {
  flex: 1;
}

.input-group {
  margin-bottom: 30rpx;
}

.input-group .label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  display: block;
}

.input-group .input {
  width: 100%;
  height: 100rpx;
  background: #f5f5f5;
  border-radius: 16rpx;
  padding: 0 30rpx;
  font-size: 30rpx;
  box-sizing: border-box;
}

.input-group .toggle {
  position: absolute;
  right: 30rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 26rpx;
  color: #4CAF50;
}

.input-group {
  position: relative;
}

.btn-login {
  width: 100%;
  height: 100rpx;
  background: #4CAF50;
  color: #fff;
  font-size: 32rpx;
  border-radius: 50rpx;
  margin-top: 40rpx;
  border: none;
}

.links {
  display: flex;
  justify-content: space-between;
  margin-top: 30rpx;
}

.links .link {
  font-size: 26rpx;
  color: #4CAF50;
}

.other-login {
  margin-top: 60rpx;
}

.divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1rpx;
  background: #e0e0e0;
}

.divider text {
  padding: 0 30rpx;
  font-size: 26rpx;
  color: #999;
}

.login-icons {
  display: flex;
  justify-content: center;
  gap: 60rpx;
}

.login-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  color: #fff;
}

.login-icon.wechat {
  background: #07C160;
}

.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  font-size: 24rpx;
  color: #999;
  margin-top: 40rpx;
}

.agreement .link {
  color: #4CAF50;
}

checkbox {
  transform: scale(0.7);
}
</style>
