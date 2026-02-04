<template>
  <view class="page">
    <view class="header">
      <text class="title">注册账号</text>
      <text class="subtitle">欢迎加入易乐航</text>
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
        <text class="label">验证码</text>
        <view class="input-with-btn">
          <input
            class="input"
            type="number"
            v-model="smsCode"
            placeholder="请输入验证码"
            maxlength="6"
          />
          <button
            class="btn-code"
            :disabled="countdown > 0"
            @click="sendCode"
          >
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </view>
      </view>

      <view class="input-group">
        <text class="label">密码</text>
        <input
          class="input"
          :type="showPassword ? 'text' : 'password'"
          v-model="password"
          placeholder="请设置6-20位密码"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="label">确认密码</text>
        <input
          class="input"
          :type="showPassword ? 'text' : 'password'"
          v-model="confirmPassword"
          placeholder="请再次输入密码"
          maxlength="20"
        />
      </view>

      <view class="input-group">
        <text class="label">昵称 (选填)</text>
        <input
          class="input"
          v-model="nickname"
          placeholder="请输入昵称"
          maxlength="20"
        />
      </view>

      <button class="btn-register" @click="handleRegister" :loading="loading">
        注册
      </button>

      <view class="links">
        <text class="link" @click="goLogin">已有账号？去登录</text>
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
const smsCode = ref('')
const password = ref('')
const confirmPassword = ref('')
const nickname = ref('')
const showPassword = ref(false)
const loading = ref(false)
const agreed = ref(false)
const countdown = ref(0)

let timer: number | null = null

function validatePhone(phone: string): boolean {
  return /^1[3-9]\d{9}$/.test(phone)
}

async function sendCode() {
  if (!phone.value) {
    uni.showToast({ title: '请输入手机号', icon: 'none' })
    return
  }
  if (!validatePhone(phone.value)) {
    uni.showToast({ title: '手机号格式不正确', icon: 'none' })
    return
  }

  try {
    await userStore.sendSmsCode(phone.value)
    uni.showToast({ title: '验证码已发送', icon: 'success' })

    // 开始倒计时
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
  if (!phone.value) {
    uni.showToast({ title: '请输入手机号', icon: 'none' })
    return
  }
  if (!validatePhone(phone.value)) {
    uni.showToast({ title: '手机号格式不正确', icon: 'none' })
    return
  }
  if (!smsCode.value) {
    uni.showToast({ title: '请输入验证码', icon: 'none' })
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
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议', icon: 'none' })
    return
  }

  loading.value = true
  try {
    // 先验证验证码
    // 然后注册
    await userStore.register(phone.value, password.value, 'parent', nickname.value || undefined)
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1500)
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
.page {
  min-height: 100vh;
  background: #fff;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 40rpx 0;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.subtitle {
  font-size: 28rpx;
  color: #999;
  margin-top: 10rpx;
}

.form-area {
  flex: 1;
  margin-top: 40rpx;
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

.input-with-btn {
  display: flex;
  gap: 20rpx;
}

.input-with-btn .input {
  flex: 1;
}

.btn-code {
  width: 220rpx;
  height: 100rpx;
  background: #4CAF50;
  color: #fff;
  font-size: 26rpx;
  border-radius: 16rpx;
  border: none;
  line-height: 100rpx;
}

.btn-code[disabled] {
  background: #ccc;
}

.btn-register {
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
  text-align: center;
  margin-top: 30rpx;
}

.links .link {
  font-size: 28rpx;
  color: #4CAF50;
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
