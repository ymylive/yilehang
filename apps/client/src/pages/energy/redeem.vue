<template>
  <view class="page">
    <!-- 顶部能量余额 -->
    <view class="balance-bar">
      <text class="balance-label">我的能量</text>
      <view class="balance-info">
        <text class="balance-value">{{ balance }}</text>
        <text class="balance-icon">⚡</text>
      </view>
    </view>

    <!-- 商家分类 -->
    <scroll-view class="category-scroll" scroll-x>
      <view class="category-list">
        <view
          :class="['category-item', { active: currentCategory === '' }]"
          @click="currentCategory = ''"
        >全部</view>
        <view
          v-for="cat in categories"
          :key="cat.value"
          :class="['category-item', { active: currentCategory === cat.value }]"
          @click="currentCategory = cat.value"
        >{{ cat.label }}</view>
      </view>
    </scroll-view>

    <!-- 商品列表 -->
    <view class="items-section">
      <view class="items-grid" v-if="items.length">
        <view
          class="item-card"
          v-for="item in filteredItems"
          :key="item.id"
          @click="showItemDetail(item)"
        >
          <view class="item-image">
            <image v-if="item.image" :src="item.image" mode="aspectFill" />
            <view v-else class="item-placeholder">🎁</view>
          </view>
          <view class="item-info">
            <text class="item-name">{{ item.name }}</text>
            <text class="item-merchant">{{ item.merchant_name }}</text>
            <view class="item-footer">
              <view class="item-cost">
                <text class="cost-value">{{ item.energy_cost }}</text>
                <text class="cost-icon">⚡</text>
              </view>
              <text class="item-original" v-if="item.original_price">
                ¥{{ item.original_price }}
              </text>
            </view>
          </view>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-icon">🎁</text>
        <text class="empty-text">暂无可兑换商品</text>
      </view>
    </view>

    <!-- 商品详情弹窗 -->
    <view class="detail-modal" v-if="selectedItem" @click="selectedItem = null">
      <view class="detail-card" @click.stop>
        <view class="detail-image">
          <image v-if="selectedItem.image" :src="selectedItem.image" mode="aspectFill" />
          <view v-else class="detail-placeholder">🎁</view>
        </view>
        <view class="detail-content">
          <text class="detail-name">{{ selectedItem.name }}</text>
          <text class="detail-merchant">{{ selectedItem.merchant_name }}</text>
          <text class="detail-desc">{{ selectedItem.description || '暂无描述' }}</text>

          <view class="detail-meta">
            <view class="meta-item" v-if="selectedItem.valid_days">
              <text class="meta-label">有效期</text>
              <text class="meta-value">兑换后{{ selectedItem.valid_days }}天内有效</text>
            </view>
            <view class="meta-item" v-if="selectedItem.usage_rules">
              <text class="meta-label">使用规则</text>
              <text class="meta-value">{{ selectedItem.usage_rules }}</text>
            </view>
          </view>

          <view class="detail-footer">
            <view class="detail-cost">
              <text class="cost-value">{{ selectedItem.energy_cost }}</text>
              <text class="cost-icon">⚡</text>
            </view>
            <button
              class="redeem-btn"
              :disabled="balance < selectedItem.energy_cost"
              @click="confirmRedeem"
            >
              {{ balance < selectedItem.energy_cost ? '能量不足' : '立即兑换' }}
            </button>
          </view>
        </view>
      </view>
    </view>

    <!-- 我的兑换订单入口 -->
    <view class="orders-fab" @click="goToOrders">
      <text class="fab-icon">📋</text>
      <text class="fab-text">我的兑换</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { energyApi, merchantApi } from '@/api'

const balance = ref(0)
const items = ref<any[]>([])
const currentCategory = ref('')
const selectedItem = ref<any>(null)

const categories = [
  { label: '餐饮', value: '餐饮' },
  { label: '运动', value: '运动' },
  { label: '教育', value: '教育' },
  { label: '娱乐', value: '娱乐' }
]

const filteredItems = computed(() => {
  if (!currentCategory.value) return items.value
  return items.value.filter(item => item.merchant_category === currentCategory.value)
})

onMounted(async () => {
  await Promise.all([loadBalance(), loadItems()])
})

watch(currentCategory, () => {
  loadItems()
})

async function loadBalance() {
  try {
    const res = await energyApi.getSummary()
    balance.value = res.balance
  } catch (error) {
    console.error('加载余额失败', error)
  }
}

async function loadItems() {
  try {
    const params: any = {}
    if (currentCategory.value) params.category = currentCategory.value

    const res = await merchantApi.getAllItems(params)
    items.value = res.items
  } catch (error) {
    console.error('加载商品失败', error)
  }
}

function showItemDetail(item: any) {
  selectedItem.value = item
}

async function confirmRedeem() {
  if (!selectedItem.value) return

  uni.showModal({
    title: '确认兑换',
    content: `确定使用 ${selectedItem.value.energy_cost} 能量兑换「${selectedItem.value.name}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        await doRedeem()
      }
    }
  })
}

async function doRedeem() {
  try {
    uni.showLoading({ title: '兑换中...' })
    const res = await merchantApi.redeemItem({ item_id: selectedItem.value.id })
    uni.hideLoading()

    uni.showModal({
      title: '兑换成功',
      content: `核销码：${res.verify_code}\n请在有效期内到店出示核销`,
      showCancel: false,
      success: () => {
        selectedItem.value = null
        loadBalance()
      }
    })
  } catch (error: any) {
    uni.hideLoading()
    uni.showToast({
      title: error.message || '兑换失败',
      icon: 'none'
    })
  }
}

function goToOrders() {
  uni.navigateTo({ url: '/pages/energy/orders' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding-bottom: 120rpx;
}

.balance-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
}

.balance-label {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.balance-info {
  display: flex;
  align-items: center;
}

.balance-value {
  font-size: 48rpx;
  font-weight: 800;
  color: #FFFFFF;
}

.balance-icon {
  font-size: 32rpx;
  margin-left: 8rpx;
}

.category-scroll {
  white-space: nowrap;
  background: #FFFFFF;
  padding: 20rpx 0;
}

.category-list {
  display: inline-flex;
  padding: 0 20rpx;
  gap: 20rpx;
}

.category-item {
  padding: 16rpx 32rpx;
  border-radius: 999rpx;
  font-size: 26rpx;
  color: #666;
  background: #F5F5F5;
}

.category-item.active {
  background: #FF8800;
  color: #FFFFFF;
}

.items-section {
  padding: 20rpx;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.item-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.item-image {
  width: 100%;
  height: 200rpx;
  background: #FFF3E0;
}

.item-image image {
  width: 100%;
  height: 100%;
}

.item-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60rpx;
}

.item-info {
  padding: 20rpx;
}

.item-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-merchant {
  font-size: 22rpx;
  color: #999;
  margin-top: 6rpx;
  display: block;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16rpx;
}

.item-cost {
  display: flex;
  align-items: center;
}

.cost-value {
  font-size: 32rpx;
  font-weight: 700;
  color: #FF8800;
}

.cost-icon {
  font-size: 24rpx;
  margin-left: 4rpx;
}

.item-original {
  font-size: 22rpx;
  color: #999;
  text-decoration: line-through;
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.detail-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 100;
}

.detail-card {
  width: 100%;
  max-height: 80vh;
  background: #FFFFFF;
  border-radius: 40rpx 40rpx 0 0;
  overflow: hidden;
}

.detail-image {
  width: 100%;
  height: 300rpx;
  background: #FFF3E0;
}

.detail-image image {
  width: 100%;
  height: 100%;
}

.detail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 100rpx;
}

.detail-content {
  padding: 30rpx;
}

.detail-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
  display: block;
}

.detail-merchant {
  font-size: 26rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
}

.detail-desc {
  font-size: 28rpx;
  color: #666;
  margin-top: 20rpx;
  line-height: 1.6;
  display: block;
}

.detail-meta {
  margin-top: 24rpx;
  padding: 20rpx;
  background: #FAFAFA;
  border-radius: 16rpx;
}

.meta-item {
  margin-bottom: 16rpx;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-label {
  font-size: 24rpx;
  color: #999;
  display: block;
}

.meta-value {
  font-size: 26rpx;
  color: #333;
  margin-top: 6rpx;
}

.detail-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30rpx;
  padding-top: 30rpx;
  border-top: 2rpx solid #F0F0F0;
}

.detail-cost .cost-value {
  font-size: 48rpx;
}

.detail-cost .cost-icon {
  font-size: 32rpx;
}

.redeem-btn {
  padding: 24rpx 60rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 600;
  border-radius: 999rpx;
  border: none;
}

.redeem-btn[disabled] {
  background: #CCC;
}

.orders-fab {
  position: fixed;
  right: 30rpx;
  bottom: 120rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
}

.fab-icon {
  font-size: 40rpx;
}

.fab-text {
  font-size: 20rpx;
  color: #666;
  margin-top: 6rpx;
}
</style>
