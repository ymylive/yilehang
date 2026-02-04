<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('教练端 App Launch')
})

onShow(() => {
  console.log('教练端 App Show')
})

onHide(() => {
  console.log('教练端 App Hide')
})
</script>

<style>
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 全局样式 */
view, text {
  box-sizing: border-box;
}

/* 主题色 */
:root {
  --primary-color: #2196F3;
  --primary-light: #64B5F6;
  --primary-dark: #1976D2;
  --success-color: #4CAF50;
  --warning-color: #FF9800;
  --error-color: #F44336;
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-hint: #999999;
  --bg-color: #F5F5F5;
  --card-bg: #FFFFFF;
}
</style>
