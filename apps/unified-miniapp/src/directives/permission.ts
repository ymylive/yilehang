/**
 * v-permission 权限控制指令
 * 根据用户权限控制元素显示/隐藏
 *
 * 用法:
 *   v-permission="'booking:create'"           - 单个权限
 *   v-permission="['booking:create', 'booking:cancel']"  - 多个权限（满足任一即可）
 *   v-permission:all="['booking:create', 'booking:cancel']" - 多个权限（需全部满足）
 *   v-permission:role="'coach'"               - 角色检查
 *   v-permission:role="['coach', 'admin']"    - 多角色检查（满足任一即可）
 */
import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'

export interface PermissionDirectiveBinding {
  value: string | string[]
  arg?: 'all' | 'role'
  modifiers?: Record<string, boolean>
}

function checkPermission(binding: DirectiveBinding<string | string[]>): boolean {
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  const { value, arg } = binding

  if (!value) return true

  // 角色检查模式
  if (arg === 'role') {
    const userRole = userStore.user?.role
    if (!userRole) return false

    const requiredRoles = Array.isArray(value) ? value : [value]
    return requiredRoles.includes(userRole)
  }

  // 权限检查模式
  const requiredPermissions = Array.isArray(value) ? value : [value]

  if (requiredPermissions.length === 0) return true

  // all 修饰符：需要全部权限
  if (arg === 'all') {
    return requiredPermissions.every(p => permissionStore.hasPermission(p))
  }

  // 默认：满足任一权限即可
  return requiredPermissions.some(p => permissionStore.hasPermission(p))
}

function updateElement(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
  const hasPermission = checkPermission(binding)

  if (!hasPermission) {
    // 隐藏元素
    el.style.display = 'none'
    // 添加标记，方便调试
    el.setAttribute('data-permission-hidden', 'true')
  } else {
    // 恢复显示
    el.style.display = ''
    el.removeAttribute('data-permission-hidden')
  }
}

export const vPermission: Directive<HTMLElement, string | string[]> = {
  mounted(el, binding) {
    updateElement(el, binding)
  },
  updated(el, binding) {
    updateElement(el, binding)
  },
}

/**
 * 函数式权限检查（用于 v-if 场景）
 */
export function hasPermission(permission: string | string[], mode: 'any' | 'all' = 'any'): boolean {
  const permissionStore = usePermissionStore()
  const permissions = Array.isArray(permission) ? permission : [permission]

  if (permissions.length === 0) return true

  if (mode === 'all') {
    return permissions.every(p => permissionStore.hasPermission(p))
  }

  return permissions.some(p => permissionStore.hasPermission(p))
}

/**
 * 函数式角色检查（用于 v-if 场景）
 */
export function hasRole(role: string | string[]): boolean {
  const userStore = useUserStore()
  const userRole = userStore.user?.role

  if (!userRole) return false

  const roles = Array.isArray(role) ? role : [role]
  return roles.includes(userRole)
}

export default vPermission
