<template>
  <view class="user-detail">
    <view class="profile-card">
      <view class="avatar">{{ user.name?.charAt(0) || '?' }}</view>
      <text class="name">{{ user.name }}</text>
      <text class="role">{{ user.role }}</text>
    </view>
    <view class="info-section">
      <view class="info-item">
        <text class="label">手机号</text>
        <text class="value">{{ user.phone }}</text>
      </view>
      <view class="info-item">
        <text class="label">注册时间</text>
        <text class="value">{{ user.createdAt }}</text>
      </view>
      <view class="info-item">
        <text class="label">状态</text>
        <text class="value">{{ user.status }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

const user = ref({
  name: '张三',
  role: '家长',
  phone: '138****0000',
  createdAt: '2024-01-15',
  status: '正常'
})

onLoad((options) => {
  console.log('User ID:', options?.id)
})
</script>

<style lang="scss" scoped>
.user-detail {
  min-height: 100vh;
  background: #f5f5f5;
}

.profile-card {
  background: linear-gradient(135deg, #ff8800, #ffaa33);
  padding: 60rpx 30rpx;
  text-align: center;
  color: #fff;

  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    background: rgba(255,255,255,0.3);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 48rpx;
    margin-bottom: 20rpx;
  }

  .name {
    display: block;
    font-size: 36rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
  }

  .role {
    font-size: 26rpx;
    opacity: 0.9;
  }
}

.info-section {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 10rpx 30rpx;

  .info-item {
    display: flex;
    justify-content: space-between;
    padding: 24rpx 0;
    border-bottom: 1rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .label {
      color: #666;
      font-size: 28rpx;
    }

    .value {
      color: #333;
      font-size: 28rpx;
    }
  }
}
</style>
