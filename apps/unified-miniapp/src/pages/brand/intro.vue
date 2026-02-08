<template>
  <scroll-view class="intro-page" scroll-y>
    <view class="hero">
      <text class="chip">{{ currentCopy.chip }}</text>
      <text class="hero-title">{{ currentCopy.heroTitle }}</text>
      <text class="hero-subtitle">{{ currentCopy.heroSubtitle }}</text>
      <text class="hero-desc">{{ currentCopy.heroDesc }}</text>

      <view class="role-tabs">
        <view
          v-for="role in roleList"
          :key="role.key"
          :class="['role-tab', { active: activeRole === role.key }]"
          @click="activeRole = role.key"
        >
          {{ role.label }}
        </view>
      </view>
    </view>

    <view class="card">
      <text class="card-title">方案关键词</text>
      <view class="keyword-list">
        <view v-for="item in currentCopy.keywords" :key="item.label" class="keyword-item">
          <text class="keyword-label">{{ item.label }}</text>
          <text class="keyword-value">{{ item.value }}</text>
        </view>
      </view>
    </view>

    <view class="card">
      <text class="card-title">三步开始</text>
      <view class="step-list">
        <text v-for="(step, index) in currentCopy.steps" :key="step" class="step-item">{{ index + 1 }}. {{ step }}</text>
      </view>
    </view>

    <view class="card">
      <text class="card-title">你将获得</text>
      <view class="benefit-list">
        <view v-for="item in currentCopy.benefits" :key="item.title" class="benefit-item">
          <text class="benefit-title">{{ item.title }}</text>
          <text class="benefit-desc">{{ item.desc }}</text>
        </view>
      </view>
    </view>

    <view class="actions">
      <button class="btn ghost" @click="goLogin">立即登录</button>
      <button class="btn primary" @click="goRegister">{{ currentCopy.primaryAction }}</button>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

type RoleKey = 'parent' | 'coach' | 'merchant'

const roleList: Array<{ key: RoleKey; label: string }> = [
  { key: 'parent', label: '我是家长' },
  { key: 'coach', label: '我是教练' },
  { key: 'merchant', label: '我是商家' }
]

const introCopy: Record<RoleKey, any> = {
  parent: {
    chip: '家长成长入口',
    heroTitle: '不是“看娃托管”',
    heroSubtitle: '而是放学两小时的成长操作系统',
    heroDesc: '训练 + 辅导联动，家长看见真实进步，中考体育更稳、日常学习更高效。',
    keywords: [
      { label: '训练反馈', value: '每次训练可追踪，可复盘' },
      { label: '成长确定性', value: '目标明确、进步可见、投入有回报' },
      { label: '家校协同', value: '教练与家长信息同步，减少沟通成本' }
    ],
    steps: ['注册家长账号并完善孩子信息', '预约体验课并选择时段', '查看课后反馈与成长档案'],
    benefits: [
      { title: '成长结果可视化', desc: '课表、反馈、消费记录一站式查看。' },
      { title: '过程更省心', desc: '标准化流程减少反复沟通，陪伴更从容。' }
    ],
    primaryAction: '家长去注册'
  },
  coach: {
    chip: '教练入驻入口',
    heroTitle: '做“专业沉淀”',
    heroSubtitle: '而不只是碎片化带课',
    heroDesc: '通过标准化流程、可视化反馈和排课能力，持续提升续课率与个人口碑。',
    keywords: [
      { label: '排课提效', value: '减少无效沟通与事务消耗' },
      { label: '反馈留痕', value: '训练过程可视化，家长更信任' },
      { label: '职业资产', value: '专业服务沉淀为长期口碑' }
    ],
    steps: ['注册教练账号并完成认证', '提交擅长方向与可授课时段', '审核通过后开通教练工作台'],
    benefits: [
      { title: '高效工作台', desc: '排课、学员管理、评价反馈一体化。' },
      { title: '专业能力可放大', desc: '把时间聚焦在训练质量与成果交付。' }
    ],
    primaryAction: '教练去入驻'
  },
  merchant: {
    chip: '商家合作入口',
    heroTitle: '接入“能量支票”',
    heroSubtitle: '获取可追踪的社区精准引流',
    heroDesc: '打通到店兑换和复购追踪，建立“到店-转化-复购”的稳定增长闭环。',
    keywords: [
      { label: '稳定客流', value: '对接社区运动家庭的持续消费需求' },
      { label: '兑换闭环', value: '核销规则清晰，路径可追踪' },
      { label: '复购增长', value: '提升到店二次转化与长期复购' }
    ],
    steps: ['提交门店与合作信息', '配置兑换商品与核销规则', '审核通过后上线合作'],
    benefits: [
      { title: '精准社区流量', desc: '触达有明确消费场景的本地家庭。' },
      { title: '效果可衡量', desc: '兑换与复购路径清晰，便于运营优化。' }
    ],
    primaryAction: '商家申请合作'
  }
}

const activeRole = ref<RoleKey>('parent')
const currentCopy = computed(() => introCopy[activeRole.value])

onLoad((query) => {
  const role = query?.role
  if (role === 'parent' || role === 'coach' || role === 'merchant') {
    activeRole.value = role
  }
})

function goLogin() {
  uni.navigateTo({ url: '/pages/user/login' })
}

function goRegister() {
  uni.navigateTo({ url: '/pages/user/register' })
}
</script>

<style scoped>
.intro-page {
  min-height: 100vh;
  background: #f8f9fb;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));
}

.hero {
  background: linear-gradient(135deg, #ffb347 0%, #ff8800 100%);
  border-bottom-left-radius: 44rpx;
  border-bottom-right-radius: 44rpx;
  padding: calc(env(safe-area-inset-top) + 36rpx) 30rpx 40rpx;
}

.chip {
  display: inline-block;
  background: rgba(255, 255, 255, 0.24);
  color: #fff;
  font-size: 22rpx;
  border-radius: 999rpx;
  padding: 10rpx 20rpx;
}

.hero-title {
  display: block;
  margin-top: 22rpx;
  font-size: 44rpx;
  color: #fff;
  font-weight: 700;
}

.hero-subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 34rpx;
  color: #fff;
  font-weight: 600;
}

.hero-desc {
  display: block;
  margin-top: 18rpx;
  font-size: 25rpx;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.92);
}

.role-tabs {
  margin-top: 22rpx;
  background: rgba(255, 255, 255, 0.22);
  border-radius: 16rpx;
  padding: 8rpx;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8rpx;
}

.role-tab {
  height: 64rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff6e8;
  font-size: 24rpx;
}

.role-tab.active {
  background: #fff;
  color: #ff8800;
  font-weight: 700;
}

.card {
  margin: 22rpx 24rpx 0;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 12rpx 28rpx rgba(31, 41, 55, 0.08);
}

.card-title {
  display: block;
  font-size: 30rpx;
  color: #1f2937;
  font-weight: 700;
  margin-bottom: 16rpx;
}

.keyword-list,
.benefit-list,
.step-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.keyword-item {
  background: #fff7eb;
  border-radius: 14rpx;
  padding: 16rpx;
}

.keyword-label {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: #ff8800;
}

.keyword-value {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #7c5f3a;
}

.benefit-item {
  background: #f8fafc;
  border-radius: 14rpx;
  padding: 16rpx;
}

.benefit-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: #111827;
}

.benefit-desc {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: #6b7280;
}

.step-item {
  background: #f3f4f6;
  border-radius: 14rpx;
  padding: 16rpx;
  font-size: 24rpx;
  color: #374151;
}

.actions {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  gap: 20rpx;
  padding: 18rpx 24rpx calc(18rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 -8rpx 24rpx rgba(0, 0, 0, 0.06);
}

.btn {
  flex: 1;
  height: 84rpx;
  border-radius: 999rpx;
  font-size: 29rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.btn::after {
  border: none;
}

.btn.ghost {
  background: #fff;
  color: #ff8800;
  border: 1rpx solid #ffd7a4;
}

.btn.primary {
  background: linear-gradient(135deg, #ffb347, #ff8800);
  color: #fff;
}
</style>
