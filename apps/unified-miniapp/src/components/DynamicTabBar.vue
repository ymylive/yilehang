<template>
  <view class="custom-tabbar" v-if="visible">
    <view
      v-for="(item, idx) in tabItems"
      :key="item.pagePath"
      class="tabbar-item"
      :class="{ active: currentIndex === idx }"
      @tap="switchTab(item, idx)"
    >
      <view class="tabbar-icon-wrap">
        <wd-icon
          class="tabbar-icon"
          :name="currentIndex === idx ? (item.activeIcon || item.icon) : item.icon"
          size="40rpx"
        />
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
  icon: string
  activeIcon?: string
  badge?: number
  dot?: boolean
}

const userStore = useUserStore()
const permissionStore = usePermissionStore()
const currentIndex = ref(0)

const TAB_ICONS: Record<string, { icon: string; activeIcon?: string }> = {
  'pages/index/index': { icon: 'home', activeIcon: 'home1' },
  'pages/booking/index': { icon: 'calendar' },
  'pages/growth/index': { icon: 'chart-bar' },
  'pages/schedule/index': { icon: 'view-list' },
  'pages/training/index': { icon: 'app' },
  'pages/user/index': { icon: 'user', activeIcon: 'user-circle' },
  'pages/coach/workbench/index': { icon: 'dashboard' },
  'pages/coach/schedule/index': { icon: 'calendar' },
  'pages/coach/students/index': { icon: 'usergroup' },
  'pages/admin/dashboard/index': { icon: 'dashboard' },
  'pages/admin/users/index': { icon: 'usergroup' },
  'pages/admin/analytics/index': { icon: 'chart' },
  'pages/chat/index': { icon: 'chat', activeIcon: 'chat1' },
  'pages/energy/index': { icon: 'star' },
}

function normalizePath(path: string) {
  return path.startsWith('/') ? path.slice(1) : path
}

// 从后端菜单或本地配置获取 tabBar
const tabItems = computed<TabItem[]>(() => {
  const role = (userStore.user?.role || 'parent') as UserRole

  // 优先使用后端菜单配置
  const backendMenus = permissionStore.getVisibleMenus()
  const tabBarMenus = backendMenus.filter(m => m.type === 'tabbar')

  if (tabBarMenus.length > 0) {
    return tabBarMenus.map(menu => {
      const pagePath = normalizePath(menu.path)
      const iconConfig = TAB_ICONS[pagePath] || { icon: 'app' }
      return {
        pagePath,
        text: menu.name,
        icon: menu.icon || iconConfig.icon,
        activeIcon: iconConfig.activeIcon || menu.icon || iconConfig.icon,
        badge: 0,
        dot: false,
      }
    })
  }

  // 回退到本地配置
  const config = ROLE_PAGE_MAP[role]
  if (!config) return []

  return config.tabBar.map(item => {
    const iconConfig = TAB_ICONS[item.pagePath] || { icon: 'app' }
    return {
      ...item,
      icon: iconConfig.icon,
      activeIcon: iconConfig.activeIcon || iconConfig.icon,
      badge: 0,
      dot: false,
    }
  })
})

const visible = computed(() => {
  if (!userStore.isLoggedIn || tabItems.value.length === 0) return false

  // Always show TabBar for allowed pages within the role's scope
  const pages = getCurrentPages()
  const current = pages[pages.length - 1] as any
  const route = current?.route || ''

  const role = (userStore.user?.role || 'parent') as UserRole
  const config = ROLE_PAGE_MAP[role]

  // Show TabBar if current page is within allowed prefixes
  return config?.allowedPrefixes.some(prefix => route.startsWith(prefix)) || false
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
  justify-content: space-around;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--tabbar-safe-height, calc(112rpx + env(safe-area-inset-bottom)));
  padding: 12rpx 16rpx calc(12rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.92);
  border-top: 1rpx solid rgba(208, 217, 233, 0.7);
  backdrop-filter: blur(14rpx);
  box-shadow: 0 -8rpx 24rpx rgba(33, 56, 92, 0.08);
  z-index: 1200;
}

.tabbar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  flex: 1;
  height: 100%;
  padding-top: 6rpx;
  transition: transform 0.2s ease;

  .tabbar-icon-wrap {
    position: relative;
    width: 64rpx;
    height: 64rpx;
    border-radius: 20rpx;
    background: rgba(243, 246, 252, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;

    .tabbar-icon {
      color: #6b768a;
      transition: color 0.2s ease;
    }
 
    .badge {
      position: absolute;
      top: -10rpx;
      right: -10rpx;
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
      top: -6rpx;
      right: -6rpx;
      width: 16rpx;
      height: 16rpx;
      background: #ff4d4f;
      border-radius: 50%;
    }
  }

  .tabbar-label {
    font-size: 21rpx;
    color: #6b768a;
    margin-top: 6rpx;
    transition: color 0.2s ease;
  }

  &.active {
    transform: translateY(-2rpx);

    .tabbar-icon-wrap {
      background: linear-gradient(135deg, #ffb347, #ff8800);
      box-shadow: 0 8rpx 16rpx rgba(255, 136, 0, 0.26);
    }

    .tabbar-icon {
      color: #fff;
    }

    .tabbar-label {
      color: #ff8800;
      font-weight: 600;
    }
  }
}
</style>
