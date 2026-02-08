<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('商家端 App Launch')
})

onShow(() => {
  console.log('商家端 App Show')
})

onHide(() => {
  console.log('商家端 App Hide')
})
</script>

<style lang="scss">
@import './styles/index.scss';

page {
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}
</style>
