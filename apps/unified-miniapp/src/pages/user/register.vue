<template>
  <view class="page">
    <view class="top-decor">
      <view class="circle circle1"></view>
      <view class="circle circle2"></view>
      <view class="circle circle3"></view>
    </view>

    <view class="nav-back" @click="goLogin">
      <text class="back-icon">&larr;</text>
      <text class="back-text">返回登录</text>
    </view>

    <view class="header-area">
      <text class="page-title">创建账号</text>
      <text class="page-subtitle">加入韧翎成长计划，开启运动之旅</text>
    </view>

    <view class="form-card">
      <view class="input-group">
        <text class="input-label">邮箱</text>
        <view class="input-box">
          <input class="input-field" type="text" v-model="email" placeholder="请输入邮箱地址" />
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">验证码</text>
        <view class="input-box code-box-wrap">
          <input class="input-field" type="number" v-model="emailCode" placeholder="请输入验证码" maxlength="6" />
          <button class="code-btn" :disabled="countdown > 0 || sendingCode" @click="sendCode">
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">昵称（选填）</text>
        <view class="input-box">
          <input class="input-field" v-model="nickname" placeholder="给自己取个名字" maxlength="20" />
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">我的身份</text>
        <view class="role-picker">
          <view
            v-for="item in roleOptions"
            :key="item.value"
            :class="['role-item', { active: selectedRole === item.value }]"
            @click="selectedRole = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">手机号（选填）</text>
        <view class="input-box">
          <input class="input-field" type="number" v-model="phone" placeholder="可稍后在个人中心补充" maxlength="11" />
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">密码</text>
        <view class="input-box">
          <input class="input-field" :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="请输入6-20位密码" maxlength="20" />
          <text class="toggle-pwd" @click="showPassword = !showPassword">{{ showPassword ? '隐藏' : '显示' }}</text>
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">确认密码</text>
        <view class="input-box">
          <input class="input-field" :type="showConfirmPassword ? 'text' : 'password'" v-model="confirmPassword" placeholder="请再次输入密码" maxlength="20" />
          <text class="toggle-pwd" @click="showConfirmPassword = !showConfirmPassword">{{ showConfirmPassword ? '隐藏' : '显示' }}</text>
        </view>
      </view>

      <view class="agreement-area">
        <view class="checkbox-wrap" @click="agreed = !agreed">
          <view :class="['custom-checkbox', { checked: agreed }]">
            <text v-if="agreed">&check;</text>
          </view>
        </view>
        <text class="agreement-text">我已阅读并同意</text>
        <text class="agreement-link" @click="viewAgreement('user')">《用户协议》</text>
        <text class="agreement-text">和</text>
        <text class="agreement-link" @click="viewAgreement('privacy')">《隐私政策》</text>
      </view>

      <button class="submit-btn" @click="submitRegister" :loading="loading">
        <text class="btn-text">{{ loading ? '注册中...' : '注册并登录' }}</text>
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { routeByRole } from '@/utils/role-guard'

const userStore = useUserStore()

const email = ref('')
const emailCode = ref('')
const nickname = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
const loading = ref(false)
const agreed = ref(false)
let countdownTimer: ReturnType<typeof setInterval> | null = null
const selectedRole = ref<'parent' | 'student' | 'coach' | 'merchant'>('parent')
const roleOptions = [
  { label: '我是家长', value: 'parent' },
  { label: '我是学员', value: 'student' },
  { label: '我是教练', value: 'coach' },
  { label: '我是商户', value: 'merchant' }
]

const canSubmit = computed(() => {
  return !!email.value && !!emailCode.value && !!password.value && !!confirmPassword.value
})

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})

function validEmail(e: string) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(e)
}

function validPhone(p: string) {
  return /^1[3-9]\d{9}$/.test(p)
}

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
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0 && countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }, 1000)
  } catch (error: any) {
    uni.showToast({ title: error.message || '验证码发送失败', icon: 'none' })
  } finally {
    sendingCode.value = false
  }
}

async function submitRegister() {
  if (!canSubmit.value) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' })
    return
  }

  if (!validEmail(email.value)) {
    uni.showToast({ title: '请输入正确的邮箱地址', icon: 'none' })
    return
  }

  if (phone.value && !validPhone(phone.value)) {
    uni.showToast({ title: '手机号格式不正确', icon: 'none' })
    return
  }

  if (password.value.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' })
    return
  }

  if (password.value !== confirmPassword.value) {
    uni.showToast({ title: '两次输入密码不一致', icon: 'none' })
    return
  }

  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议与隐私政策', icon: 'none' })
    return
  }

  loading.value = true
  try {
    await userStore.registerWithEmail(
      email.value,
      emailCode.value,
      password.value,
      selectedRole.value,
      nickname.value || undefined,
      phone.value || undefined
    )
    const user = await userStore.fetchUserInfo()
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      routeByRole(user?.role)
    }, 400)
  } catch (error: any) {
    uni.showToast({ title: error.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goLogin() {
  uni.navigateBack()
}

function viewAgreement(type: 'user' | 'privacy') {
  uni.showToast({ title: type === 'user' ? '用户协议开发中' : '隐私政策开发中', icon: 'none' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #fff;
}

.top-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 320rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.circle1 { width: 240rpx; height: 240rpx; top: -80rpx; right: -30rpx; }
.circle2 { width: 140rpx; height: 140rpx; top: 120rpx; left: -40rpx; }
.circle3 { width: 90rpx; height: 90rpx; top: 80rpx; right: 160rpx; }

.nav-back {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: #fff;
  font-size: 26rpx;
  padding: 36rpx 28rpx 0;
}

.header-area {
  position: relative;
  z-index: 2;
  padding: 34rpx 30rpx 22rpx;
}

.page-title {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
  color: #fff;
}

.page-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.form-card {
  position: relative;
  z-index: 3;
  margin: 24rpx;
  margin-top: 26rpx;
  border-radius: 28rpx;
  background: #fff;
  padding: 28rpx;
  box-shadow: 0 16rpx 34rpx rgba(0, 0, 0, 0.12);
}

.input-group {
  margin-bottom: 20rpx;
}

.input-label {
  display: block;
  margin-bottom: 8rpx;
  font-size: 24rpx;
  color: #666;
}

.input-box {
  display: flex;
  align-items: center;
  border-radius: 16rpx;
  background: #f6f6f6;
  padding: 0 20rpx;
}

.input-field {
  flex: 1;
  height: 88rpx;
  font-size: 28rpx;
  color: #333;
}

.code-box-wrap .code-btn {
  margin-left: 12rpx;
  background: transparent;
  color: #FF8800;
  font-size: 24rpx;
}

.role-picker {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12rpx;
}

.role-item {
  height: 76rpx;
  border-radius: 14rpx;
  border: 1rpx solid #f1d7bc;
  background: #fff8ef;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9b6c2f;
  font-size: 24rpx;
  text-align: center;
}

.role-item.active {
  border-color: #ff8800;
  background: #fff0de;
  color: #ff8800;
  font-weight: 600;
}

.toggle-pwd {
  color: #FF8800;
  font-size: 24rpx;
}

.agreement-area {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 4rpx;
}

.checkbox-wrap {
  padding: 8rpx;
}

.custom-checkbox {
  width: 34rpx;
  height: 34rpx;
  border: 1rpx solid #ccc;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-checkbox.checked {
  background: #FF8800;
  border-color: #FF8800;
  color: #fff;
}

.agreement-text {
  font-size: 22rpx;
  color: #999;
  margin: 0 4rpx;
}

.agreement-link {
  font-size: 22rpx;
  color: #FF8800;
}

.submit-btn {
  margin-top: 24rpx;
  height: 92rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn::after {
  border: none;
}

.btn-text {
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
}
</style>
