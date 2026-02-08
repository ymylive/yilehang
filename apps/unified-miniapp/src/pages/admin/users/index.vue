<template>
  <view class="admin-users">
    <view class="search-bar">
      <input class="search-input" placeholder="搜索用户" v-model="keyword" />
    </view>
    <view class="user-list">
      <view class="user-item" v-for="user in users" :key="user.id" @click="viewDetail(user.id)">
        <view class="user-avatar">
          <text>{{ user.name.charAt(0) }}</text>
        </view>
        <view class="user-info">
          <text class="user-name">{{ user.name }}</text>
          <text class="user-role">{{ user.role }}</text>
        </view>
        <text class="arrow">›</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const keyword = ref('')
const users = ref([
  { id: 1, name: '张三', role: '家长' },
  { id: 2, name: '李四', role: '教练' },
  { id: 3, name: '王五', role: '学员' },
])

function viewDetail(id: number) {
  uni.navigateTo({ url: `/pages/admin/users/detail?id=${id}` })
}
</script>

<style lang="scss" scoped>
.admin-users {
  min-height: 100vh;
  background: #f5f5f5;
}

.search-bar {
  padding: 20rpx;
  background: #fff;

  .search-input {
    background: #f5f5f5;
    border-radius: 32rpx;
    padding: 16rpx 30rpx;
    font-size: 28rpx;
  }
}

.user-list {
  margin-top: 20rpx;
  background: #fff;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;

  .user-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: #ff8800;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 32rpx;
    margin-right: 20rpx;
  }

  .user-info {
    flex: 1;

    .user-name {
      display: block;
      font-size: 30rpx;
      color: #333;
    }

    .user-role {
      font-size: 24rpx;
      color: #999;
    }
  }

  .arrow {
    color: #ccc;
    font-size: 32rpx;
  }
}
</style>
