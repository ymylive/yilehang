<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  // #ifdef DEV
  console.log('教练端 App Launch')
  // #endif
})

onShow(() => {
  // #ifdef DEV
  console.log('教练端 App Show')
  // #endif
})

onHide(() => {
  // #ifdef DEV
  console.log('教练端 App Hide')
  // #endif
})
</script>

<style lang="scss">
@import './styles/index.scss';

page {
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}
</style>
