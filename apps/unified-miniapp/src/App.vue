<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './stores/user'
import { enforceRoleRoute } from './utils/role-guard'

onLaunch(() => {
  const userStore = useUserStore()
  userStore.initFromStorage()
})

onShow(() => {
  const userStore = useUserStore()
  userStore.initFromStorage()
  setTimeout(() => {
    enforceRoleRoute(userStore.user?.role)
  }, 0)
})

onHide(() => {
  // noop
})
</script>

<style lang="scss">
@import './uni.scss';

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
