/**
 * Permission store - 权限状态管理
 * 对接后端 /api/v1/roles, /api/v1/permissions, /api/v1/menus
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { roleApi } from '@/api'

export interface Role {
  id: number
  code: string
  name: string
  is_system: boolean
  is_active: boolean
  sort_order: number
}

export interface Permission {
  id: number
  code: string
  name: string
  type: string
  resource: string
  action: string
  description?: string
}

export interface Menu {
  id: number
  parent_id: number | null
  code: string
  name: string
  type: string
  path: string
  component?: string
  icon?: string
  sort_order: number
  is_visible: boolean
  is_active: boolean
  permission_code?: string
  children: Menu[]
}

export const usePermissionStore = defineStore('permission', () => {
  const roles = ref<Role[]>([])
  const permissions = ref<Permission[]>([])
  const menus = ref<Menu[]>([])
  const activeRole = ref<string>('')
  const loading = ref(false)
  const initialized = ref(false)

  // 权限代码集合（用于快速查找）
  const permissionCodes = computed(() => new Set(permissions.value.map(p => p.code)))

  // 角色代码列表
  const roleCodes = computed(() => roles.value.map(r => r.code))

  /**
   * 检查是否拥有指定权限
   */
  function hasPermission(code: string): boolean {
    // admin 拥有所有权限
    if (activeRole.value === 'admin' || roleCodes.value.includes('admin')) {
      return true
    }
    return permissionCodes.value.has(code)
  }

  /**
   * 检查是否拥有指定角色
   */
  function hasRole(code: string): boolean {
    return roleCodes.value.includes(code)
  }

  /**
   * 获取用户角色列表
   */
  async function fetchRoles() {
    try {
      const res: any = await roleApi.getRoles()
      roles.value = Array.isArray(res?.data) ? res.data : []
      // 设置激活角色（优先使用第一个角色）
      if (roles.value.length > 0 && !activeRole.value) {
        activeRole.value = roles.value[0].code
      }
      return roles.value
    } catch (error) {
      console.error('Fetch roles failed:', error)
      return []
    }
  }

  /**
   * 获取用户权限列表
   */
  async function fetchPermissions() {
    try {
      const res: any = await roleApi.getPermissions()
      permissions.value = Array.isArray(res?.data) ? res.data : []
      return permissions.value
    } catch (error) {
      console.error('Fetch permissions failed:', error)
      return []
    }
  }

  /**
   * 获取用户菜单列表
   */
  async function fetchMenus() {
    try {
      const res: any = await roleApi.getMenus()
      menus.value = Array.isArray(res?.data) ? res.data : []
      return menus.value
    } catch (error) {
      console.error('Fetch menus failed:', error)
      return []
    }
  }

  /**
   * 切换角色
   */
  async function switchRole(roleCode: string) {
    if (!roleCodes.value.includes(roleCode)) {
      throw new Error(`您没有 ${roleCode} 角色`)
    }

    try {
      const res: any = await roleApi.switchRole(roleCode)
      const { access_token, active_role } = res?.data || {}

      if (access_token) {
        uni.setStorageSync('token', access_token)
      }

      activeRole.value = active_role || roleCode

      // 重新获取权限和菜单
      await Promise.all([fetchPermissions(), fetchMenus()])

      return res?.data
    } catch (error) {
      console.error('Switch role failed:', error)
      throw error
    }
  }

  /**
   * 初始化权限数据（登录后调用）
   */
  async function init() {
    if (initialized.value) return

    loading.value = true
    try {
      await Promise.all([fetchRoles(), fetchPermissions(), fetchMenus()])
      initialized.value = true
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置状态（登出时调用）
   */
  function reset() {
    roles.value = []
    permissions.value = []
    menus.value = []
    activeRole.value = ''
    initialized.value = false
  }

  /**
   * 设置激活角色（从 user store 同步）
   */
  function setActiveRole(role: string) {
    activeRole.value = role
  }

  /**
   * 根据权限过滤菜单
   */
  function getVisibleMenus(): Menu[] {
    function filterMenus(items: Menu[]): Menu[] {
      return items
        .filter(menu => {
          if (!menu.is_visible || !menu.is_active) return false
          if (menu.permission_code && !hasPermission(menu.permission_code)) return false
          return true
        })
        .map(menu => ({
          ...menu,
          children: filterMenus(menu.children || []),
        }))
    }
    return filterMenus(menus.value)
  }

  return {
    roles,
    permissions,
    menus,
    activeRole,
    loading,
    initialized,
    permissionCodes,
    roleCodes,
    hasPermission,
    hasRole,
    fetchRoles,
    fetchPermissions,
    fetchMenus,
    switchRole,
    init,
    reset,
    setActiveRole,
    getVisibleMenus,
  }
})
