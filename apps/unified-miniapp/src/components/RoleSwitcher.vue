<template>
  <view class="role-switcher" v-if="showSwitcher">
    <view class="switcher-trigger" @click="togglePanel">
      <view class="current-role">
        <text class="role-label">{{ roleName }}</text>
      </view>
      <text class="arrow" :class="{ 'arrow-up': showPanel }">&#9660;</text>
    </view>

    <view class="switcher-mask" v-if="showPanel" @click="showPanel = false" />

    <view class="switcher-panel" v-if="showPanel">
      <view
        v-for="role in availableRoles"
        :key="role.value"
        class="role-item"
        :class="{ active: currentRole === role.value }"
        @click="switchRole(role.value)"
      >
        <text class="role-name">{{ role.label }}</text>
        <text class="check-icon" v-if="currentRole === role.value">&#10003;</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { getRoleHomePage, type UserRole } from '@/utils/role-guard'

const userStore = useUserStore()
const permissionStore = usePermissionStore()
const showPanel = ref(false)
const switching = ref(false)

const ROLE_LABELS: Record<string, string> = {
  admin: '管理员',
  coach: '教练',
  parent: '家长',
  student: '学员'
}

const currentRole = computed(() => permissionStore.activeRole || userStore.user?.role || '')
const roleName = computed(() => ROLE_LABELS[currentRole.value] || '未知')

const availableRoles = computed(() => {
  // If permission store has roles from backend, use those; otherwise show all
  if (permissionStore.roleCodes.length > 0) {
    return permissionStore.roleCodes
      .filter(code => ROLE_LABELS[code])
      .map(code => ({ value: code, label: ROLE_LABELS[code] }))
  }
  return Object.entries(ROLE_LABELS).map(([value, label]) => ({ value, label }))
})

const showSwitcher = computed(() => !!userStore.isLoggedIn)

function togglePanel() {
  showPanel.value = !showPanel.value
}

async function switchRole(role: string) {
  if (role === currentRole.value) {
    showPanel.value = false
    return
  }

  uni.showModal({
    title: '切换角色',
    content: `确定切换到${ROLE_LABELS[role]}角色？`,
    success: async (res) => {
      if (res.confirm) {
        switching.value = true
        try {
          await permissionStore.switchRole(role)
          // Sync role to user store
          userStore.setUser({ ...userStore.user, role })
          const homePage = getRoleHomePage(role as UserRole)
          uni.reLaunch({ url: homePage })
        } catch (error: any) {
          console.error('Switch role failed:', error)
          uni.showToast({ title: error.message || '切换角色失败', icon: 'none' })
        } finally {
          switching.value = false
          showPanel.value = false
        }
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.role-switcher {
  position: relative;
  display: inline-flex;
}

.switcher-trigger {
  display: flex;
  align-items: center;
  padding: 8rpx 20rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);

  .current-role {
    .role-label {
      font-size: 26rpx;
      color: #333;
      font-weight: 500;
    }
  }

  .arrow {
    font-size: 18rpx;
    color: #999;
    margin-left: 8rpx;
    transition: transform 0.2s;
    &.arrow-up { transform: rotate(180deg); }
  }
}

.switcher-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.switcher-panel {
  position: absolute;
  top: calc(100% + 8rpx);
  left: 0;
  min-width: 200rpx;
  background: #fff;
  border-radius: 12rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.12);
  overflow: hidden;
  z-index: 1000;

  .role-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24rpx 32rpx;
    border-bottom: 1rpx solid #f5f5f5;

    &:last-child { border-bottom: none; }
    &.active { background: #fff8f0; }

    .role-name {
      font-size: 28rpx;
      color: #333;
    }

    .check-icon {
      font-size: 28rpx;
      color: #ff8800;
      font-weight: bold;
    }
  }
}
</style>
