<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './stores/user'

onLaunch(() => {
  console.log('App Launch')
  // 初始化用户状态
  const userStore = useUserStore()
  userStore.initFromStorage()
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style>
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.container {
  padding: 20rpx;
}

/* 主题色 */
:root {
  --primary-color: #4CAF50;
  --primary-light: #81C784;
  --primary-dark: #388E3C;
  --accent-color: #FF9800;
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-hint: #999999;
  --bg-color: #F5F5F5;
  --card-bg: #FFFFFF;
}
</style>
