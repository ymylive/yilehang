<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './stores/user'

onLaunch(() => {
  console.log('App Launch')
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
page {
  background-color: #FFFBF5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

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
