import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { useUserStore } from './stores/user'
import { trackError } from './utils/telemetry'


let lastRuntimeErrorAt = 0

function reportRuntimeError(error: unknown) {
  console.error('[runtime-error]', error)
  trackError('runtime.error', error)
  const now = Date.now()
  if (now - lastRuntimeErrorAt < 1500) return
  lastRuntimeErrorAt = now
  uni.showToast({ title: '页面异常，正在恢复', icon: 'none' })
}

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()

  app.use(pinia)

  // 注册全局权限指令
  app.directive('permission', {
    mounted(el, binding) {
      const { value } = binding
      const userStore = useUserStore()

      if (value && !checkPermission(value, userStore.user?.role)) {
        el.style.display = 'none'
      }
    },
    updated(el, binding) {
      const { value } = binding
      const userStore = useUserStore()

      if (value && !checkPermission(value, userStore.user?.role)) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  })

  app.config.errorHandler = (error) => {
    reportRuntimeError(error)
  }

  const uniAny = uni as any
  if (typeof uniAny.onUnhandledRejection === 'function') {
    uniAny.onUnhandledRejection((event: any) => {
      reportRuntimeError(event?.reason || event)
    })
  }

  return {
    app,
    pinia
  }
}

function checkPermission(permission: string | string[], role?: string): boolean {
  if (!role) return false

  const permissions = Array.isArray(permission) ? permission : [permission]
  return permissions.includes(role)
}
