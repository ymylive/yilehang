<template>
  <view class="page">
    <!-- 用户信息卡片 -->
    <view class="profile-card">
      <view class="profile-bg">
        <view class="bg-shape s1"></view>
        <view class="bg-shape s2"></view>
      </view>
      <view class="profile-content">
        <image
          class="merchant-logo"
          :src="merchantStore.merchant?.logo || '/static/default-logo.png'"
          mode="aspectFill"
        />
        <view class="merchant-info">
          <text class="merchant-name">{{ merchantStore.merchant?.name || '商家名称' }}</text>
          <text class="merchant-id">商家ID: {{ merchantStore.merchant?.id || '-' }}</text>
        </view>
        <view class="status-badge">
          <text>营业中</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-group">
        <view class="menu-item" @click="goToProducts">
          <view class="menu-icon">
            <text>&#x1F381;</text>
          </view>
          <text class="menu-name">商品管理</text>
          <text class="menu-arrow">&#x203A;</text>
        </view>
        <view class="menu-item" @click="goToSettings">
          <view class="menu-icon">
            <text>&#x2699;</text>
          </view>
          <text class="menu-name">店铺设置</text>
          <text class="menu-arrow">&#x203A;</text>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-item" @click="goToHelp">
          <view class="menu-icon">
            <text>&#x2753;</text>
          </view>
          <text class="menu-name">帮助中心</text>
          <text class="menu-arrow">&#x203A;</text>
        </view>
        <view class="menu-item" @click="goToAbout">
          <view class="menu-icon">
            <text>&#x2139;</text>
          </view>
          <text class="menu-name">关于我们</text>
          <text class="menu-arrow">&#x203A;</text>
        </view>
        <view class="menu-item" @click="contactService">
          <view class="menu-icon">
            <text>&#x1F4DE;</text>
          </view>
          <text class="menu-name">联系客服</text>
          <text class="menu-arrow">&#x203A;</text>
        </view>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <view class="logout-btn" @click="handleLogout">
        <text>退出登录</text>
      </view>
    </view>

    <!-- 版本信息 -->
    <view class="version-info">
      <text>韧性成长中心商家端 v1.0.0</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { useMerchantStore } from '@/stores/merchant'

const merchantStore = useMerchantStore()

function goToProducts() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToSettings() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToHelp() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToAbout() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function contactService() {
  uni.makePhoneCall({
    phoneNumber: '400-888-1234',
    fail: () => {
      uni.showToast({ title: '拨打失败', icon: 'none' })
    }
  })
}

function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        merchantStore.logout()
        uni.reLaunch({ url: '/pages/user/login' })
      }
    }
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: 120rpx;
}

/* 用户信息卡片 */
.profile-card {
  position: relative;
  margin: 20rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  border-radius: 24rpx;
  padding: 40rpx 30rpx;
  overflow: hidden;
}

.profile-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.bg-shape.s1 {
  width: 200rpx;
  height: 200rpx;
  top: -60rpx;
  right: -40rpx;
}

.bg-shape.s2 {
  width: 150rpx;
  height: 150rpx;
  bottom: -40rpx;
  left: -30rpx;
}

.profile-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.merchant-logo {
  width: 100rpx;
  height: 100rpx;
  border-radius: 20rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.5);
  background: #FFFFFF;
}

.merchant-info {
  flex: 1;
}

.merchant-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #FFFFFF;
  display: block;
}

.merchant-id {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8rpx;
}

.status-badge {
  padding: 10rpx 20rpx;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 999rpx;
  font-size: 24rpx;
  color: #FFFFFF;
}

/* 功能菜单 */
.menu-section {
  padding: 0 20rpx;
}

.menu-group {
  background: #FFFFFF;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx 24rpx;
  border-bottom: 2rpx solid #F5F5F5;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  width: 60rpx;
  height: 60rpx;
  background: #FFF3E0;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  margin-right: 20rpx;
}

.menu-name {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.menu-arrow {
  font-size: 36rpx;
  color: #CCC;
}

/* 退出登录 */
.logout-section {
  padding: 40rpx 20rpx;
}

.logout-btn {
  height: 90rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  color: #F44336;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

/* 版本信息 */
.version-info {
  text-align: center;
  font-size: 24rpx;
  color: #999;
  padding: 20rpx;
}
</style>
