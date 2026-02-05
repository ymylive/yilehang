<template>
  <view class="page">
    <view class="logo-area">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
      <text class="title">易乐航</text>
      <text class="subtitle">ITS智慧体教云平台</text>
    </view>

    <view class="form-area">
      <view class="tabs">
        <text :class="['tab', { active: loginMode === 'password' }]" @click="loginMode = 'password'">密码登录</text>
        <text :class="['tab', { active: loginMode === 'code' }]" @click="loginMode = 'code'">验证码登录</text>
      </view>

      <view class="input-group">
        <text class="label">{{ loginMode === 'password' ? '手机号' : '邮箱' }}</text>
        <input
          class="input"
          :type="loginMode === 'password' ? 'number' : 'text'"
          v-model="phone"
          :placeholder="loginMode === 'password' ? '请输入手机号' : '请输入邮箱'"
          :maxlength="loginMode === 'password' ? 11 : 50"
        />
      </view>

      <view v-if="loginMode === 'password'" class="input-group">
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

      <view v-else class="input-group code-group">
        <input
          class="input code-input"
          v-model="code"
          placeholder="请输入验证码"
          maxlength="6"
        />
        <button class="btn-send-code" @click="sendCode" :disabled="codeSending || codeCountdown > 0">
          {{ codeCountdown > 0 ? `${codeCountdown}s` : '发送验证码' }}
        </button>
      </view>

      <button class="btn-login" @click="handleLogin" :loading="loading">
        {{ loginMode === 'password' ? '登录' : '验证码登录' }}
      </button>

      <view class="links">
        <text class="link" @click="goRegister">注册账号</text>
        <text v-if="loginMode === 'password'" class="link" @click="forgotPassword">忘记密码</text>
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
    uni.showToast({ title: '请输入邮箱', icon: 'none' })
    return
  }

  codeSending.value = true
  try {
    const response = await uni.request({
      url: `${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/auth/login/email/send`,
      method: 'POST',
      data: { phone: phone.value }
    })

    if (response[1]?.statusCode === 200) {
      uni.showToast({ title: '验证码已发送', icon: 'success' })
      codeCountdown.value = 60
      const timer = setInterval(() => {
        codeCountdown.value--
        if (codeCountdown.value <= 0) clearInterval(timer)
      }, 1000)
    } else {
      uni.showToast({ title: '发送失败', icon: 'none' })
    }
  } catch (error) {
    uni.showToast({ title: '发送失败', icon: 'none' })
  } finally {
    codeSending.value = false
  }
}

async function handleLogin() {
  if (!phone.value) {
    uni.showToast({ title: `请输入${loginMode.value === 'password' ? '手机号' : '邮箱'}`, icon: 'none' })
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
    uni.showToast({ title: '请先同意用户协议', icon: 'none' })
    return
  }

  loading.value = true
  try {
    if (loginMode.value === 'password') {
      await userStore.login(phone.value, password.value)
    } else {
      await userStore.emailLogin(phone.value, code.value)
    }
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

async function wechatLogin() {
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议', icon: 'none' })
    return
  }

  // #ifdef MP-WEIXIN
  uni.login({
    provider: 'weixin',
    success: async (loginRes) => {
      try {
        loading.value = true
        await userStore.wechatLogin(loginRes.code)
        uni.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/index/index' })
        }, 1500)
      } catch (error: any) {
        uni.showToast({ title: error.message || '微信登录失败', icon: 'none' })
      } finally {
        loading.value = false
      }
    },
    fail: () => {
      uni.showToast({ title: '获取微信授权失败', icon: 'none' })
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

.tabs {
  display: flex;
  gap: 30rpx;
  margin-bottom: 40rpx;
  border-bottom: 2rpx solid #e0e0e0;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 28rpx;
  color: #999;
  border-bottom: 4rpx solid transparent;
  transition: all 0.3s;

  &.active {
    color: #4CAF50;
    border-bottom-color: #4CAF50;
  }
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

.code-group {
  display: flex;
  gap: 20rpx;
}

.code-input {
  flex: 1;
}

.btn-send-code {
  width: 200rpx;
  height: 100rpx;
  background: #f5f5f5;
  color: #4CAF50;
  font-size: 24rpx;
  border-radius: 16rpx;
  border: none;
  white-space: nowrap;

  &:disabled {
    color: #999;
  }
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
