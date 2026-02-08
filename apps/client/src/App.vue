<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './stores/user'

function enforceRoleRoute(role?: string) {
  if (!role) return

  const pages = getCurrentPages()
  const current = pages[pages.length - 1] as any
  const route = current?.route || ''
  if (!route || route.startsWith('pages/user/')) return

  if (role === 'coach') {
    const allowed = route.startsWith('pages/coach/') || route.startsWith('pages/chat/')
    if (!allowed) {
      uni.redirectTo({ url: '/pages/coach/workbench/index' })
    }
    return
  }

  if (role === 'merchant') {
    const allowed = route.startsWith('pages/merchant/')
    if (!allowed) {
      uni.redirectTo({ url: '/pages/merchant/index' })
    }
    return
  }

  if (role === 'student') {
    const disallowed = route.startsWith('pages/coach/') || route.startsWith('pages/merchant/')
    if (disallowed) {
      uni.switchTab({ url: '/pages/schedule/index' })
    }
  }
}

onLaunch(() => {
  // #ifdef DEV
  console.log('App Launch')
  // #endif
  const userStore = useUserStore()
  userStore.initFromStorage()
})

onShow(() => {
  // #ifdef DEV
  console.log('App Show')
  // #endif
  const userStore = useUserStore()
  userStore.initFromStorage()
  setTimeout(() => {
    enforceRoleRoute(userStore.user?.role)
  }, 0)
})

onHide(() => {
  // #ifdef DEV
  console.log('App Hide')
  // #endif
})
</script>

<style lang="scss">
@import './styles/index.scss';

.container {
  padding: 20rpx;
}

:root {
  --primary-color: #FF8800;
  --primary-light: #FFB347;
  --primary-dark: #F57C00;
  --accent-color: #4FA4F3;
  --text-primary: #2D2D2D;
  --text-secondary: #666666;
  --text-hint: #999999;
  --bg-color: #FFFBF5;
  --card-bg: #FFFFFF;
}
</style>
