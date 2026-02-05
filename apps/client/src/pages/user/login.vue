<template>
  <view class="page">
    <!-- 椤堕儴瑁呴グ鑳屾櫙 -->
    <view class="top-bg">
      <view class="deco-circle c1"></view>
      <view class="deco-circle c2"></view>
      <view class="deco-circle c3"></view>
    </view>

    <!-- 鍝佺墝鍖哄煙 -->
    <view class="brand-area">
      <view class="logo-box">
        <image class="logo-img" src="/static/logo.png" mode="aspectFit" />
      </view>
      <text class="app-name">鏄撲箰鑸?/text>
      <text class="app-slogan">璁╄繍鍔ㄦ洿蹇箰</text>
    </view>

    <!-- 鐧诲綍鍗＄墖 -->
    <view class="login-card">
      <!-- 鐧诲綍鏂瑰紡鍒囨崲 -->
      <view class="tab-bar">
        <view
          :class="['tab-item', { active: loginMode === 'password' }]"
          @click="loginMode = 'password'"
        >
          <text class="tab-text">瀵嗙爜鐧诲綍</text>
        </view>
        <view
          :class="['tab-item', { active: loginMode === 'code' }]"
          @click="loginMode = 'code'"
        >
          <text class="tab-text">楠岃瘉鐮佺櫥褰?/text>
        </view>
        <view class="tab-indicator" :style="{ left: loginMode === 'password' ? '0' : '50%' }"></view>
      </view>

      <!-- 琛ㄥ崟鍖哄煙 -->
      <view class="form-area">
        <view class="input-group">
          <text class="input-label">鎵嬫満鍙?/text>
          <view class="input-wrapper">
            <input
              class="input-field"
              type="number"
              v-model="phone"
              placeholder="璇疯緭鍏ユ墜鏈哄彿"
              :maxlength="11"
              placeholder-class="placeholder"
            />
          </view>
        </view>

        <view v-if="loginMode === 'password'" class="input-group">
          <text class="input-label">瀵嗙爜</text>
          <view class="input-wrapper">
            <input
              class="input-field"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="璇疯緭鍏ュ瘑鐮?
              placeholder-class="placeholder"
            />
            <view class="input-suffix" @click="showPassword = !showPassword">
              <text>{{ showPassword ? '闅愯棌' : '鏄剧ず' }}</text>
            </view>
          </view>
        </view>

        <view v-else class="input-group">
          <text class="input-label">楠岃瘉鐮?/text>
          <view class="input-wrapper code-wrapper">
            <input
              class="input-field"
              v-model="code"
              placeholder="璇疯緭鍏ラ獙璇佺爜"
              maxlength="6"
              placeholder-class="placeholder"
            />
            <button
              class="code-btn"
              :class="{ disabled: codeSending || codeCountdown > 0 }"
              @click="sendCode"
              :disabled="codeSending || codeCountdown > 0"
            >
              {{ codeCountdown > 0 ? `${codeCountdown}s` : '鑾峰彇楠岃瘉鐮? }}
            </button>
          </view>
        </view>

        <!-- 鐧诲綍鎸夐挳 -->
        <button class="login-btn" @click="handleLogin" :loading="loading">
          {{ loading ? '鐧诲綍涓?..' : '鐧?褰? }}
        </button>

        <!-- 蹇嵎閾炬帴 -->
        <view class="quick-links">
          <text class="link-text" @click="goRegister">鏂扮敤鎴锋敞鍐?/text>
          <text v-if="loginMode === 'password'" class="link-text" @click="forgotPassword">蹇樿瀵嗙爜锛?/text>
        </view>
      </view>
    </view>

    <!-- 鍏朵粬鐧诲綍鏂瑰紡 -->
    <view class="other-login">
      <view class="divider">
        <view class="line"></view>
        <text class="divider-text">鍏朵粬鐧诲綍鏂瑰紡</text>
        <view class="line"></view>
      </view>
      <view class="social-login">
        <view class="social-btn wechat" @click="wechatLogin">
          <text class="social-icon">寰俊</text>
        </view>
      </view>
    </view>

    <!-- 鐢ㄦ埛鍗忚 -->
    <view class="agreement">
      <view class="checkbox-area" @click="agreed = !agreed">
        <view :class="['checkbox', { checked: agreed }]">
          <text v-if="agreed" class="check-icon">鉁?/text>
        </view>
      </view>
      <text class="agree-text">鎴戝凡闃呰骞跺悓鎰?/text>
      <text class="agree-link" @click="viewAgreement('user')">銆婄敤鎴峰崗璁€?/text>
      <text class="agree-text">鍜?/text>
      <text class="agree-link" @click="viewAgreement('privacy')">銆婇殣绉佹斂绛栥€?/text>
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
    uni.showToast({ title: '璇疯緭鍏ユ墜鏈哄彿', icon: 'none' })
    return
  }

  // 楠岃瘉鎵嬫満鍙锋牸寮?  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(phone.value)) {
    uni.showToast({ title: '璇疯緭鍏ユ纭殑鎵嬫満鍙?, icon: 'none' })
    return
  }

  codeSending.value = true
  try {
    await userStore.sendSmsCode(phone.value)
    uni.showToast({ title: '楠岃瘉鐮佸凡鍙戦€?, icon: 'success' })
    codeCountdown.value = 60
    const timer = setInterval(() => {
      codeCountdown.value--
      if (codeCountdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (error) {
    uni.showToast({ title: '鍙戦€佸け璐?, icon: 'none' })
  } finally {
    codeSending.value = false
  }
}

async function handleLogin() {
  if (!phone.value) {
    uni.showToast({ title: '璇疯緭鍏ユ墜鏈哄彿', icon: 'none' })
    return
  }

  if (loginMode.value === 'password' && !password.value) {
    uni.showToast({ title: '璇疯緭鍏ュ瘑鐮?, icon: 'none' })
    return
  }

  if (loginMode.value === 'code' && !code.value) {
    uni.showToast({ title: '璇疯緭鍏ラ獙璇佺爜', icon: 'none' })
    return
  }

  if (!agreed.value) {
    uni.showToast({ title: '璇峰厛鍚屾剰鐢ㄦ埛鍗忚', icon: 'none' })
    return
  }

  loading.value = true
  try {
    if (loginMode.value === 'password') {
      await userStore.login(phone.value, password.value)
    } else {
      await userStore.loginWithSms(phone.value, code.value)
    }
    uni.showToast({ title: '鐧诲綍鎴愬姛', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '鐧诲綍澶辫触', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goRegister() {
  uni.navigateTo({ url: '/pages/user/register' })
}

function forgotPassword() {
  uni.showToast({ title: '璇疯仈绯诲鏈嶉噸缃瘑鐮?, icon: 'none' })
}

async function wechatLogin() {
  if (!agreed.value) {
    uni.showToast({ title: '璇峰厛鍚屾剰鐢ㄦ埛鍗忚', icon: 'none' })
    return
  }

  // #ifdef MP-WEIXIN
  uni.login({
    provider: 'weixin',
    success: async (loginRes) => {
      try {
        loading.value = true
        await userStore.wechatLogin(loginRes.code)
        uni.showToast({ title: '鐧诲綍鎴愬姛', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/index/index' })
        }, 1500)
      } catch (error: any) {
        uni.showToast({ title: error.message || '寰俊鐧诲綍澶辫触', icon: 'none' })
      } finally {
        loading.value = false
      }
    },
    fail: () => {
      uni.showToast({ title: '鑾峰彇寰俊鎺堟潈澶辫触', icon: 'none' })
    }
  })
  // #endif

  // #ifndef MP-WEIXIN
  uni.showToast({ title: '璇峰湪寰俊灏忕▼搴忎腑浣跨敤', icon: 'none' })
  // #endif
}

function viewAgreement(type: string) {
  uni.navigateTo({ url: `/pages/user/agreement?type=${type}` })
}
</script>

<style scoped>
/* 璁捐鍙橀噺 */
page {
  --c-primary: #FF8800;
  --c-secondary: #FFB347;
  --c-accent: #4FA4F3;
  --c-bg-body: #FFFBF5;
  --c-bg-card: #FFFFFF;
  --c-bg-input: #F5F5F5;
  --c-text-main: #2D2D2D;
  --c-text-sub: #666666;
  --c-text-light: #999999;
  --radius-sm: 24rpx;
  --radius-md: 40rpx;
  --radius-lg: 60rpx;
}

.page {
  min-height: 100vh;
  background: var(--c-bg-body);
  position: relative;
  overflow: hidden;
}

/* 椤堕儴瑁呴グ鑳屾櫙 */
.top-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 500rpx;
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
  border-radius: 0 0 80rpx 80rpx;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.c1 {
  width: 300rpx;
  height: 300rpx;
  top: -100rpx;
  right: -80rpx;
}

.c2 {
  width: 200rpx;
  height: 200rpx;
  top: 150rpx;
  left: -60rpx;
}

.c3 {
  width: 120rpx;
  height: 120rpx;
  top: 80rpx;
  right: 150rpx;
  background: rgba(255, 255, 255, 0.15);
}

/* 鍝佺墝鍖哄煙 */
.brand-area {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
  padding-bottom: 60rpx;
}

.logo-box {
  width: 160rpx;
  height: 160rpx;
  background: #FFFFFF;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20rpx 60rpx rgba(255, 136, 0, 0.3);
}

.logo-img {
  width: 100rpx;
  height: 100rpx;
}

.app-name {
  font-size: 52rpx;
  font-weight: 800;
  color: #FFFFFF;
  margin-top: 30rpx;
  letter-spacing: 4rpx;
}

.app-slogan {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 10rpx;
}

/* 鐧诲綍鍗＄墖 */
.login-card {
  position: relative;
  z-index: 10;
  margin: 0 40rpx;
  background: #FFFFFF;
  border-radius: var(--radius-md);
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* Tab鍒囨崲 */
.tab-bar {
  display: flex;
  position: relative;
  background: #F8F8F8;
}

.tab-item {
  flex: 1;
  height: 100rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-text {
  font-size: 30rpx;
  color: var(--c-text-sub);
  font-weight: 500;
  transition: all 0.3s;
}

.tab-item.active .tab-text {
  color: var(--c-primary);
  font-weight: 600;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  width: 50%;
  height: 6rpx;
  background: linear-gradient(90deg, #FFB347, #FF8800);
  border-radius: 3rpx;
  transition: left 0.3s ease;
}

/* 琛ㄥ崟鍖哄煙 */
.form-area {
  padding: 50rpx 40rpx;
}

.input-group {
  margin-bottom: 36rpx;
}

.input-label {
  display: block;
  font-size: 28rpx;
  color: var(--c-text-sub);
  font-weight: 600;
  margin-bottom: 16rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--c-bg-input);
  border-radius: var(--radius-sm);
  padding: 0 30rpx;
  height: 110rpx;
  border: 3rpx solid transparent;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  background: #FFFFFF;
  border-color: var(--c-secondary);
  box-shadow: 0 0 0 8rpx rgba(255, 179, 71, 0.15);
}

.input-field {
  flex: 1;
  height: 100%;
  font-size: 32rpx;
  color: var(--c-text-main);
}

.placeholder {
  color: var(--c-text-light);
}

.input-suffix {
  font-size: 26rpx;
  color: var(--c-primary);
  padding: 10rpx;
}

/* 楠岃瘉鐮佽緭鍏?*/
.code-wrapper {
  padding-right: 16rpx;
}

.code-btn {
  min-width: 180rpx;
  height: 76rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  color: #FFFFFF;
  font-size: 26rpx;
  font-weight: 600;
  border-radius: 38rpx;
  border: none;
  padding: 0 24rpx;
}

.code-btn.disabled {
  background: #E0E0E0;
  color: #999;
}

/* 鐧诲綍鎸夐挳 */
.login-btn {
  width: 100%;
  height: 110rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  color: #FFFFFF;
  font-size: 34rpx;
  font-weight: 700;
  border-radius: var(--radius-lg);
  border: none;
  margin-top: 20rpx;
  box-shadow: 0 16rpx 40rpx rgba(255, 136, 0, 0.35);
  letter-spacing: 8rpx;
}

.login-btn:active {
  transform: scale(0.98);
  box-shadow: 0 8rpx 20rpx rgba(255, 136, 0, 0.25);
}

/* 蹇嵎閾炬帴 */
.quick-links {
  display: flex;
  justify-content: space-between;
  margin-top: 30rpx;
}

.link-text {
  font-size: 28rpx;
  color: var(--c-primary);
}

/* 鍏朵粬鐧诲綍鏂瑰紡 */
.other-login {
  padding: 50rpx 40rpx 30rpx;
}

.divider {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.line {
  flex: 1;
  height: 2rpx;
  background: #E8E8E8;
}

.divider-text {
  padding: 0 30rpx;
  font-size: 26rpx;
  color: var(--c-text-light);
}

.social-login {
  display: flex;
  justify-content: center;
}

.social-btn {
  width: 200rpx;
  height: 90rpx;
  border-radius: 45rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.social-btn.wechat {
  background: #333333;
}

.social-icon {
  font-size: 28rpx;
  color: #FFFFFF;
  font-weight: 500;
}

/* 鐢ㄦ埛鍗忚 */
.agreement {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  padding: 30rpx 40rpx 60rpx;
}

.checkbox-area {
  padding: 10rpx;
}

.checkbox {
  width: 40rpx;
  height: 40rpx;
  border: 3rpx solid #DDD;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.checkbox.checked {
  background: linear-gradient(135deg, #FFB347, #FF8800);
  border-color: var(--c-primary);
}

.check-icon {
  color: #FFFFFF;
  font-size: 24rpx;
  font-weight: bold;
}

.agree-text {
  font-size: 26rpx;
  color: var(--c-text-light);
}

.agree-link {
  font-size: 26rpx;
  color: var(--c-primary);
}
</style>
