<template>
  <view class="custom-tabbar" v-if="visible">
    <view
      v-for="(item, idx) in tabItems"
      :key="item.pagePath"
      class="tabbar-item"
      :class="{ active: currentIndex === idx }"
      @click="switchTab(item, idx)"
    >
      <view class="tabbar-icon">
        <image
          v-if="item.iconPath"
          class="icon-image"
          :src="currentIndex === idx ? item.selectedIconPath : item.iconPath"
          mode="aspectFit"
        />
        <text v-else class="icon-text">{{ item.icon }}</text>
        <view v-if="item.badge && item.badge > 0" class="badge">
          {{ item.badge > 99 ? '99+' : item.badge }}
        </view>
        <view v-else-if="item.dot" class="dot"></view>
      </view>
      <text class="tabbar-label">{{ item.text }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { ROLE_PAGE_MAP, type UserRole } from '@/utils/role-guard'

interface TabItem {
  pagePath: string
  text: string
  icon?: string
  iconPath?: string
  selectedIconPath?: string
  badge?: number
  dot?: boolean
}

const userStore = useUserStore()
const permissionStore = usePermissionStore()
const currentIndex = ref(0)

// 角色对应的 tabBar 图标配置
const TAB_ICONS: Record<string, { icon: string; iconPath?: string; selectedIconPath?: string }> = {
  'pages/index/index': { icon: '🏠' },
  'pages/booking/index': { icon: '📅' },
  'pages/growth/index': { icon: '📈' },
  'pages/schedule/index': { icon: '📋' },
  'pages/training/index': { icon: '🏋️' },
  'pages/user/index': { icon: '👤' },
  'pages/coach/workbench/index': { icon: '🔧' },
  'pages/coach/schedule/index': { icon: '📋' },
  'pages/coach/students/index': { icon: '👥' },
  'pages/admin/dashboard/index': { icon: '📊' },
  'pages/admin/users/index': { icon: '👥' },
  'pages/admin/analytics/index': { icon: '📉' },
  'pages/chat/index': { icon: '💬' },
  'pages/energy/index': { icon: '⚡' },
}

// 从后端菜单或本地配置获取 tabBar
const tabItems = computed<TabItem[]>(() => {
  const role = (userStore.user?.role || 'parent') as UserRole

  // 优先使用后端菜单配置
  const backendMenus = permissionStore.getVisibleMenus()
  const tabBarMenus = backendMenus.filter(m => m.type === 'tabbar')

  if (tabBarMenus.length > 0) {
    return tabBarMenus.map(menu => ({
      pagePath: menu.path.startsWith('/') ? menu.path.slice(1) : menu.path,
      text: menu.name,
      icon: menu.icon || TAB_ICONS[menu.path]?.icon || '📄',
      iconPath: undefined,
      selectedIconPath: undefined,
      badge: 0,
      dot: false,
    }))
  }

  // 回退到本地配置
  const config = ROLE_PAGE_MAP[role]
  if (!config) return []

  return config.tabBar.map(item => {
    const iconConfig = TAB_ICONS[item.pagePath] || { icon: '📄' }
    return {
      ...item,
      ...iconConfig,
      badge: 0,
      dot: false,
    }
  })
})

const visible = computed(() => {
  return userStore.isLoggedIn && tabItems.value.length > 0
})

// 监听页面变化，更新当前选中的 tab
function updateCurrentIndex() {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1] as any
  const route = current?.route || ''

  const idx = tabItems.value.findIndex(item => item.pagePath === route)
  if (idx >= 0) {
    currentIndex.value = idx
  }
}

// 监听角色变化，重置 tab 索引
watch(() => userStore.user?.role, () => {
  currentIndex.value = 0
})

// 监听权限初始化完成
watch(() => permissionStore.initialized, (val) => {
  if (val) {
    updateCurrentIndex()
  }
})

function switchTab(item: TabItem, idx: number) {
  if (currentIndex.value === idx) return
  currentIndex.value = idx

  const url = '/' + item.pagePath

  // 判断是否是 tabBar 页面
  const isTabPage = tabItems.value.some(t => t.pagePath === item.pagePath)

  if (isTabPage) {
    // 使用 reLaunch 确保正确切换（因为自定义 tabBar 可能不在 pages.json 的 tabBar.list 中）
    uni.reLaunch({ url })
  } else {
    uni.navigateTo({ url })
  }
}

/**
 * 设置 tab 徽标
 */
function setBadge(pagePath: string, badge: number) {
  const item = tabItems.value.find(t => t.pagePath === pagePath)
  if (item) {
    item.badge = badge
  }
}

/**
 * 设置 tab 红点
 */
function setDot(pagePath: string, show: boolean) {
  const item = tabItems.value.find(t => t.pagePath === pagePath)
  if (item) {
    item.dot = show
  }
}

onMounted(() => {
  updateCurrentIndex()
})

defineExpose({ updateCurrentIndex, setBadge, setDot })
</script>

<style lang="scss" scoped>
.custom-tabbar {
  display: flex;
  align-items: center;
  justify-content: space-around;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx;
  background: #fff;
  border-top: 1rpx solid #eee;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 999;
}

.tabbar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  transition: color 0.2s;

  .tabbar-icon {
    position: relative;

    .icon-text {
      font-size: 40rpx;
    }

    .icon-image {
      width: 44rpx;
      height: 44rpx;
    }

    .badge {
      position: absolute;
      top: -8rpx;
      right: -16rpx;
      min-width: 32rpx;
      height: 32rpx;
      padding: 0 8rpx;
      background: #ff4d4f;
      border-radius: 16rpx;
      font-size: 20rpx;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .dot {
      position: absolute;
      top: -4rpx;
      right: -4rpx;
      width: 16rpx;
      height: 16rpx;
      background: #ff4d4f;
      border-radius: 50%;
    }
  }

  .tabbar-label {
    font-size: 22rpx;
    color: #999;
    margin-top: 4rpx;
  }

  &.active {
    .tabbar-label {
      color: #ff8800;
      font-weight: 500;
    }
  }
}
</style>
