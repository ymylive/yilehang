<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
        <span class="logo-text" v-if="!isCollapsed">易乐航</span>
        <span class="logo-icon" v-else>乐</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#4CAF50"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>数据驾驶舱</span>
        </el-menu-item>
        <el-sub-menu index="users">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/users">全部用户</el-menu-item>
          <el-menu-item index="/students">学员管理</el-menu-item>
          <el-menu-item index="/coaches">教练管理</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/courses">
          <el-icon><Reading /></el-icon>
          <span>课程管理</span>
        </el-menu-item>
        <el-menu-item index="/schedules">
          <el-icon><Calendar /></el-icon>
          <span>排课管理</span>
        </el-menu-item>
        <el-menu-item index="/bookings">
          <el-icon><Tickets /></el-icon>
          <span>预约管理</span>
        </el-menu-item>
        <el-sub-menu index="memberships">
          <template #title>
            <el-icon><Postcard /></el-icon>
            <span>课时卡</span>
          </template>
          <el-menu-item index="/membership-cards">课时卡管理</el-menu-item>
          <el-menu-item index="/student-cards">学员课时卡</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/finance">
          <el-icon><Money /></el-icon>
          <span>财务管理</span>
        </el-menu-item>
        <el-menu-item index="/analytics">
          <el-icon><TrendCharts /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 主内容区 -->
    <div class="main">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRoute?.meta?.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" src="" />
              <span class="username">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

function logout() {
  localStorage.removeItem('admin_token')
  router.push('/login')
}
</script>

<style scoped lang="scss">
.layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  background: #001529;
  transition: width 0.3s;

  &.collapsed {
    width: 64px;
  }
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: #4CAF50;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 64px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.content {
  flex: 1;
  padding: 20px;
  background: #f0f2f5;
  overflow: auto;
}

:deep(.el-menu) {
  border-right: none;
}
</style>
