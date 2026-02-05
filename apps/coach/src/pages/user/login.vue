<template>
  <view class="login-page">
    <view class="logo-section">
      <text class="logo-text">易乐航</text>
      <text class="sub-text">教练工作台</text>
    </view>

    <view class="form-section">
      <view class="form-item">
        <wd-input
          v-model="phone"
          placeholder="请输入手机号"
          type="number"
          :maxlength="11"
        />
      </view>
      <view class="form-item">
        <wd-input
          v-model="password"
          placeholder="请输入密码"
          type="password"
        />
      </view>

      <wd-button
        type="primary"
        block
        :loading="loading"
        :disabled="!canLogin"
        @click="handleLogin"
      >
        登录
      </wd-button>
    </view>

    <view class="footer">
      <text class="footer-text">仅限教练使用</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { authApi } from '@/api'

const phone = ref('')
const password = ref('')
const loading = ref(false)

const canLogin = computed(() => {
  return phone.value.length === 11 && password.value.length >= 6
})

async function handleLogin() {
  if (!canLogin.value || loading.value) return

  loading.value = true
  try {
    const res: any = await authApi.login({
      phone: phone.value,
      password: password.value
    })

    // 验证用户角色
    if (res.user && res.user.role !== 'coach') {
      uni.showToast({ title: '仅限教练登录', icon: 'none' })
      return
    }

    // 保存token
    uni.setStorageSync('token', res.access_token || res.token)
    uni.showToast({ title: '登录成功', icon: 'success' })

    setTimeout(() => {
      uni.switchTab({ url: '/pages/workbench/index' })
    }, 1500)
  } catch (error: any) {
    uni.showToast({ title: error.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

.logo-section {
  padding: 120rpx 0 80rpx;
  text-align: center;

  .logo-text {
    display: block;
    font-size: 60rpx;
    font-weight: 600;
    color: #2196F3;
  }

  .sub-text {
    display: block;
    font-size: 28rpx;
    color: #999;
    margin-top: 16rpx;
  }
}

.form-section {
  padding: 0 60rpx;

  .form-item {
    margin-bottom: 30rpx;
  }

  :deep(.wd-button) {
    margin-top: 40rpx;
  }
}

.footer {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 60rpx;

  .footer-text {
    font-size: 24rpx;
    color: #ccc;
  }
}
</style>
