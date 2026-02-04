import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/index.vue'),
      meta: { title: '登录' }
    },
    {
      path: '/',
      component: () => import('@/layouts/default.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/index.vue'),
          meta: { title: '数据驾驶舱', icon: 'DataBoard' }
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('@/views/users/index.vue'),
          meta: { title: '用户管理', icon: 'User' }
        },
        {
          path: 'students',
          name: 'Students',
          component: () => import('@/views/users/students.vue'),
          meta: { title: '学员管理', icon: 'UserFilled' }
        },
        {
          path: 'coaches',
          name: 'Coaches',
          component: () => import('@/views/users/coaches.vue'),
          meta: { title: '教练管理', icon: 'Avatar' }
        },
        {
          path: 'courses',
          name: 'Courses',
          component: () => import('@/views/courses/index.vue'),
          meta: { title: '课程管理', icon: 'Reading' }
        },
        {
          path: 'schedules',
          name: 'Schedules',
          component: () => import('@/views/schedules/index.vue'),
          meta: { title: '排课管理', icon: 'Calendar' }
        },
        {
          path: 'finance',
          name: 'Finance',
          component: () => import('@/views/finance/index.vue'),
          meta: { title: '财务管理', icon: 'Money' }
        },
        {
          path: 'analytics',
          name: 'Analytics',
          component: () => import('@/views/analytics/index.vue'),
          meta: { title: '数据分析', icon: 'TrendCharts' }
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '易乐航'} - 管理后台`

  const token = localStorage.getItem('admin_token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
