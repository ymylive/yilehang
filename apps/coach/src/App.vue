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
  font-family: "ZCOOL QingKe HuangYou", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

view, text {
  box-sizing: border-box;
}

:root {
  --primary-color: #FF8800;
  --primary-light: #FFB347;
  --primary-dark: #E56A00;
  --accent-color: #4FA4F3;
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
