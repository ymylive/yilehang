<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './stores/user'
import { enforceRoleRoute } from './utils/role-guard'
import { trackEvent } from './utils/telemetry'

onLaunch(() => {
  const userStore = useUserStore()
  userStore.initFromStorage()
  trackEvent('app.launch')
})

onShow(() => {
  const userStore = useUserStore()
  userStore.initFromStorage()
  trackEvent('app.show', { loggedIn: Boolean(userStore.token) })
  if (userStore.token && !userStore.user?.role) {
    uni.reLaunch({ url: '/pages/user/login' })
    return
  }
  setTimeout(() => {
    enforceRoleRoute(userStore.user?.role)
  }, 0)
})

onHide(() => {
  trackEvent('app.hide')
})
</script>

<style lang="scss">
@import './uni.scss';

.container {
  padding: 20rpx;
}

:root {
  --primary-color: #2563eb;
  --primary-light: #3b82f6;
  --primary-dark: #1d4ed8;
  --accent-color: #f97316;
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --text-hint: #94a3b8;
  --bg-color: #f8fafc;
  --card-bg: #ffffff;
  --border-soft: rgba(222, 231, 244, 0.92);
  --surface-shadow: 0 12rpx 28rpx rgba(30, 41, 59, 0.08);
  --surface-shadow-strong: 0 18rpx 36rpx rgba(30, 41, 59, 0.12);
  --motion-fast: 180ms;
  --motion-medium: 240ms;
  --tabbar-height: 112rpx;
  --tabbar-safe-height: calc(var(--tabbar-height) + env(safe-area-inset-bottom));
  --tabbar-content-offset: calc(var(--tabbar-safe-height) + 24rpx);
}

page {
  background: radial-gradient(120% 120% at 50% -20%, #ffffff 0%, #f5f9ff 48%, #eef4fb 100%);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

view,
text,
button,
input,
textarea,
scroll-view,
image {
  box-sizing: border-box;
}

button {
  transition: transform var(--motion-fast) ease, box-shadow var(--motion-fast) ease, opacity var(--motion-fast) ease;
}

button::after {
  border: none;
}

button:active {
  transform: translateY(1rpx) scale(0.99);
}

input,
textarea {
  color: var(--text-primary);
}

.pro-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(252, 254, 255, 0.92));
  border: 1rpx solid var(--border-soft);
  border-radius: 24rpx;
  box-shadow: var(--surface-shadow);
}

.pro-glass {
  background: rgba(255, 255, 255, 0.72);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12rpx);
}

.page-enter,
.anim-page-enter {
  animation: pageEnter var(--motion-medium) ease-out both;
}

.anim-fade-up {
  opacity: 0;
  transform: translateY(14rpx);
  animation: fadeUp var(--motion-medium) ease-out forwards;
}

.anim-delay-1 {
  animation-delay: 70ms;
}

.anim-delay-2 {
  animation-delay: 140ms;
}

.anim-delay-3 {
  animation-delay: 210ms;
}

@keyframes pageEnter {
  from {
    opacity: 0;
    transform: translateY(16rpx) scale(0.995);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(14rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  page,
  view,
  text,
  button,
  input,
  textarea,
  scroll-view,
  image {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
