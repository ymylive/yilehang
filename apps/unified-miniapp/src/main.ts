import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

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

// 导入 useUserStore 用于指令
import { useUserStore } from './stores/user'
