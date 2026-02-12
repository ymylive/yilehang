<template>
  <view class="page">
    <!-- 头像区域 -->
    <view class="avatar-section" @click="chooseAvatar">
      <image class="avatar" :src="avatar || '/static/default-avatar.png'" mode="aspectFill" />
      <view class="avatar-edit">
        <text class="edit-text">点击更换头像</text>
      </view>
    </view>

    <!-- 微信头像同步 -->
    <view class="sync-wechat" v-if="isWechat" @click="syncWechatAvatar">
      <view class="sync-icon">
        <wd-icon name="camera" size="30rpx" color="#07C160" />
      </view>
      <text class="sync-text">同步微信头像</text>
    </view>

    <!-- 表单区域 -->
    <view class="form-section">
      <view class="form-item">
        <text class="label">昵称</text>
        <input
          class="input"
          type="text"
          v-model="nickname"
          placeholder="请输入昵称"
          maxlength="20"
        />
      </view>
      <view class="form-item">
        <text class="label">手机号</text>
        <input
          class="input"
          type="text"
          v-model="phone"
          placeholder="请输入手机号"
          maxlength="11"
        />
      </view>
      <view class="form-item">
        <text class="label">邮箱</text>
        <text class="value readonly">{{ email || '未绑定' }}</text>
      </view>
      <view class="form-item">
        <text class="label">角色</text>
        <text class="value readonly">{{ roleText }}</text>
      </view>
    </view>

    <!-- 保存按钮 -->
    <view class="save-section">
      <button class="save-btn" :loading="saving" @tap="saveProfile">
        保存修改
      </button>
    </view>
    <DynamicTabBar />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { authApi, uploadApi } from '@/api'
import DynamicTabBar from '@/components/DynamicTabBar.vue'

const userStore = useUserStore()

const avatar = ref('')
const nickname = ref('')
const phone = ref('')
const email = ref('')
const role = ref('')
const saving = ref(false)

const isWechat = computed(() => {
  return typeof wx !== 'undefined' && typeof (globalThis as any).__wxConfig !== 'undefined'
})

const roleText = computed(() => {
  const map: Record<string, string> = {
    parent: '家长',
    student: '学员',
    coach: '教练',
    admin: '管理员'
  }
  return map[role.value] || role.value
})

onMounted(async () => {
  await loadUserInfo()
})

async function loadUserInfo() {
  try {
    const user = await authApi.getUserInfo()
    avatar.value = user.avatar || ''
    nickname.value = user.nickname || ''
    phone.value = user.phone || ''
    email.value = user.email || ''
    role.value = user.role || ''
  } catch (error) {
    console.error('加载用户信息失败', error)
  }
}

function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0]
      await uploadAvatar(tempFilePath)
    }
  })
}

async function uploadAvatar(filePath: string) {
  uni.showLoading({ title: '上传中...' })
  try {
    const result = await uploadApi.avatar(filePath) as any
    avatar.value = result.url
    uni.showToast({ title: '头像更新成功', icon: 'success' })
  } catch (error) {
    console.error('上传头像失败', error)
    uni.showToast({ title: '上传失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function syncWechatAvatar() {
  // 微信小程序获取头像
  if (!isWechat.value) {
    uni.showToast({ title: '请在微信小程序中使用', icon: 'none' })
    return
  }

  uni.showLoading({ title: '同步中...' })
  try {
    const result = await uploadApi.syncWechatAvatar() as any
    avatar.value = result.url
    uni.showToast({ title: '同步成功', icon: 'success' })
  } catch (error: any) {
    console.error('同步微信头像失败', error)
    uni.showToast({ title: error.message || '同步失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function saveProfile() {
  if (!nickname.value.trim()) {
    uni.showToast({ title: '请输入昵称', icon: 'none' })
    return
  }

  saving.value = true
  try {
    await authApi.updateUserInfo({
      nickname: nickname.value.trim(),
      phone: phone.value.trim() || undefined,
      avatar: avatar.value || undefined
    })

    // 更新本地存储
    userStore.setUser({
      ...userStore.user,
      nickname: nickname.value.trim(),
      phone: phone.value.trim(),
      avatar: avatar.value
    })

    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    console.error('保存失败', error)
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: calc(300rpx + env(safe-area-inset-bottom));
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
  background: linear-gradient(135deg, #FF8800, #FFB347);
}

.avatar {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.5);
}

.avatar-edit {
  margin-top: 16rpx;
}

.edit-text {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
}

.sync-wechat {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  background: #fff;
  margin: 20rpx;
  border-radius: 12rpx;
  gap: 12rpx;
  transition: transform 200ms ease, box-shadow 200ms ease;
  cursor: pointer;
}

.sync-wechat:active {
  transform: translateY(2rpx);
  box-shadow: 0 8rpx 16rpx rgba(7, 193, 96, 0.16);
}

.sync-icon {
  width: 58rpx;
  height: 58rpx;
  border-radius: 16rpx;
  background: #ecfdf3;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sync-text {
  font-size: 28rpx;
  color: #07C160;
}

.form-section {
  margin: 20rpx;
  background: #fff;
  border-radius: 12rpx;
  overflow: hidden;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.form-item:last-child {
  border-bottom: none;
}

.label {
  width: 160rpx;
  font-size: 28rpx;
  color: #333;
  flex-shrink: 0;
}

.input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.value {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.value.readonly {
  color: #999;
}

.save-section {
  position: fixed;
  bottom: calc(120rpx + env(safe-area-inset-bottom));
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background: rgba(255, 255, 255, 0.95);
  border-top: 1rpx solid rgba(235, 235, 235, 0.9);
  box-shadow: 0 -6rpx 20rpx rgba(0, 0, 0, 0.06);
  z-index: 1100;
}

.save-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #fff;
  font-size: 32rpx;
  border-radius: 44rpx;
  border: none;
}

.save-btn[loading] {
  opacity: 0.7;
}
</style>
