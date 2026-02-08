<template>
  <view class="page">
    <!-- 扫码区域 -->
    <view class="scan-area" v-if="!orderInfo && !verifyResult">
      <view class="scan-header">
        <text class="scan-title">扫描核销码</text>
        <text class="scan-desc">请扫描学员出示的能量支票核销码</text>
      </view>

      <!-- 扫码按钮 -->
      <view class="scan-box" @click="startScan">
        <view class="scan-frame">
          <view class="corner tl"></view>
          <view class="corner tr"></view>
          <view class="corner bl"></view>
          <view class="corner br"></view>
        </view>
        <view class="scan-hint">
          <text class="hint-icon">📷</text>
          <text class="hint-text">点击扫码</text>
        </view>
      </view>

      <!-- 手动输入 -->
      <view class="manual-section">
        <view class="divider">
          <view class="divider-line"></view>
          <text class="divider-text">或手动输入核销码</text>
          <view class="divider-line"></view>
        </view>
        <view class="input-row">
          <input
            class="code-input"
            v-model="manualCode"
            placeholder="请输入核销码"
            @confirm="queryByCode"
          />
          <view class="query-btn" @click="queryByCode">
            <text>查询</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 订单详情 -->
    <view class="order-detail" v-if="orderInfo && !verifyResult">
      <view class="detail-header">
        <text class="detail-title">订单信息</text>
        <view :class="['status-badge', orderInfo.status]">
          <text>{{ getStatusText(orderInfo.status) }}</text>
        </view>
      </view>

      <view class="detail-card">
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">商品名称</text>
            <text class="info-value">{{ orderInfo.item_name }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">能量消耗</text>
            <text class="info-value energy">{{ orderInfo.energy_cost }} ⚡</text>
          </view>
          <view class="info-item">
            <text class="info-label">核销码</text>
            <text class="info-value code">{{ orderInfo.verify_code }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">下单时间</text>
            <text class="info-value">{{ formatTime(orderInfo.created_at) }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">有效期至</text>
            <text class="info-value">{{ formatTime(orderInfo.expire_at) }}</text>
          </view>
        </view>
      </view>

      <!-- 操作按钮 -->
      <view class="action-section" v-if="orderInfo.status === 'pending'">
        <view class="cancel-btn" @click="cancelVerify">
          <text>取消</text>
        </view>
        <view class="confirm-btn" @click="confirmVerify">
          <text>确认核销</text>
        </view>
      </view>

      <view class="action-section" v-else>
        <view class="back-btn" @click="resetPage">
          <text>返回扫码</text>
        </view>
      </view>
    </view>

    <!-- 核销结果 -->
    <view class="result-section" v-if="verifyResult">
      <view :class="['result-card', verifyResult.success ? 'success' : 'fail']">
        <view class="result-icon">
          <text>{{ verifyResult.success ? '✅' : '❌' }}</text>
        </view>
        <text class="result-title">{{ verifyResult.success ? '核销成功' : '核销失败' }}</text>
        <text class="result-message">{{ verifyResult.message }}</text>

        <view class="result-info" v-if="verifyResult.success && orderInfo">
          <view class="result-item">
            <text class="result-label">商品</text>
            <text class="result-value">{{ orderInfo.item_name }}</text>
          </view>
          <view class="result-item">
            <text class="result-label">能量</text>
            <text class="result-value">{{ orderInfo.energy_cost }} ⚡</text>
          </view>
        </view>
      </view>

      <view class="result-actions">
        <view class="action-btn primary" @click="resetPage">
          <text>继续核销</text>
        </view>
        <view class="action-btn secondary" @click="goBack">
          <text>返回工作台</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { merchantApi } from '@/api'

const manualCode = ref('')
const orderInfo = ref<any>(null)
const verifyResult = ref<{ success: boolean; message: string } | null>(null)

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待核销',
    verified: '已核销',
    cancelled: '已取消',
    expired: '已过期'
  }
  return map[status] || status
}

function formatTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function startScan() {
  // #ifdef MP-WEIXIN
  uni.scanCode({
    onlyFromCamera: true,
    scanType: ['qrCode'],
    success: (res) => {
      handleScanResult(res.result)
    },
    fail: () => {
      uni.showToast({ title: '扫码取消', icon: 'none' })
    }
  })
  // #endif

  // #ifdef H5
  uni.showModal({
    title: '输入核销码',
    editable: true,
    placeholderText: '请输入核销码',
    success: (res) => {
      if (res.confirm && res.content) {
        handleScanResult(res.content)
      }
    }
  })
  // #endif
}

function handleScanResult(result: string) {
  manualCode.value = result
  queryByCode()
}

async function queryByCode() {
  const code = manualCode.value.trim()
  if (!code) {
    uni.showToast({ title: '请输入核销码', icon: 'none' })
    return
  }

  uni.showLoading({ title: '查询中...' })

  try {
    // 先尝试通过核销码查询
    const res = await merchantApi.verifyByCode(code)

    if (res.order) {
      orderInfo.value = res.order
    } else {
      uni.showToast({ title: res.message || '未找到订单', icon: 'none' })
    }
  } catch (error: any) {
    uni.showToast({ title: error.message || '查询失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

async function confirmVerify() {
  if (!orderInfo.value) return

  uni.showLoading({ title: '核销中...' })

  try {
    const res = await merchantApi.verifyOrder(orderInfo.value.id, orderInfo.value.verify_code)

    verifyResult.value = {
      success: res.success,
      message: res.message || '核销成功'
    }
  } catch (error: any) {
    verifyResult.value = {
      success: false,
      message: error.message || '核销失败'
    }
  } finally {
    uni.hideLoading()
  }
}

function cancelVerify() {
  orderInfo.value = null
  manualCode.value = ''
}

function resetPage() {
  orderInfo.value = null
  verifyResult.value = null
  manualCode.value = ''
}

function goBack() {
  uni.navigateBack()
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding: 30rpx;
}

.scan-area {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.scan-header {
  text-align: center;
  margin-bottom: 40rpx;
}

.scan-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.scan-desc {
  font-size: 28rpx;
  color: #999;
}

.scan-box {
  width: 500rpx;
  height: 500rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;
}

.scan-frame {
  width: 400rpx;
  height: 400rpx;
  position: relative;
  background: rgba(255, 136, 0, 0.05);
  border-radius: 24rpx;
}

.corner {
  position: absolute;
  width: 40rpx;
  height: 40rpx;
  border-color: #FF8800;
  border-style: solid;
}

.corner.tl { top: 0; left: 0; border-width: 6rpx 0 0 6rpx; border-radius: 12rpx 0 0 0; }
.corner.tr { top: 0; right: 0; border-width: 6rpx 6rpx 0 0; border-radius: 0 12rpx 0 0; }
.corner.bl { bottom: 0; left: 0; border-width: 0 0 6rpx 6rpx; border-radius: 0 0 0 12rpx; }
.corner.br { bottom: 0; right: 0; border-width: 0 6rpx 6rpx 0; border-radius: 0 0 12rpx 0; }

.scan-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 30rpx;
}

.hint-icon {
  font-size: 60rpx;
  margin-bottom: 12rpx;
}

.hint-text {
  font-size: 28rpx;
  color: #FF8800;
  font-weight: 600;
}

.manual-section {
  width: 100%;
  margin-top: 20rpx;
}

.divider {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.divider-line {
  flex: 1;
  height: 2rpx;
  background: #EEE;
}

.divider-text {
  padding: 0 20rpx;
  font-size: 26rpx;
  color: #999;
}

.input-row {
  display: flex;
  gap: 16rpx;
}

.code-input {
  flex: 1;
  height: 90rpx;
  background: #FFFFFF;
  border: 2rpx solid #EEE;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 32rpx;
}

.query-btn {
  width: 160rpx;
  height: 90rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 600;
}

.order-detail {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.detail-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.status-badge {
  padding: 8rpx 20rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.status-badge.pending { background: #FFF3E0; color: #FF8800; }
.status-badge.verified { background: #E8F5E9; color: #4CAF50; }
.status-badge.cancelled { background: #FFEBEE; color: #F44336; }
.status-badge.expired { background: #F5F5F5; color: #999; }

.detail-card {
  background: #FAFAFA;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 28rpx;
  color: #999;
}

.info-value {
  font-size: 28rpx;
  color: #333;
}

.info-value.energy {
  color: #FF8800;
  font-weight: 600;
}

.info-value.code {
  font-family: monospace;
  letter-spacing: 2rpx;
  color: #4FA4F3;
}

.action-section {
  display: flex;
  gap: 20rpx;
}

.cancel-btn, .back-btn {
  flex: 1;
  height: 90rpx;
  background: #F5F5F5;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  color: #666;
}

.confirm-btn {
  flex: 2;
  height: 90rpx;
  background: linear-gradient(135deg, #FF8800, #FFB347);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 600;
  color: #FFFFFF;
  box-shadow: 0 8rpx 20rpx rgba(255, 136, 0, 0.3);
}

.result-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 60rpx;
}

.result-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 50rpx 30rpx;
  text-align: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
  margin-bottom: 40rpx;
}

.result-card.success { border-top: 8rpx solid #4CAF50; }
.result-card.fail { border-top: 8rpx solid #F44336; }

.result-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.result-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.result-message {
  font-size: 28rpx;
  color: #999;
  display: block;
  margin-bottom: 30rpx;
}

.result-info {
  background: #FAFAFA;
  border-radius: 16rpx;
  padding: 20rpx;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
}

.result-item:not(:last-child) {
  border-bottom: 2rpx solid #EEE;
}

.result-label {
  font-size: 26rpx;
  color: #999;
}

.result-value {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.result-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.action-btn {
  height: 90rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 600;
}

.action-btn.primary {
  background: linear-gradient(135deg, #FF8800, #FFB347);
  color: #FFFFFF;
  box-shadow: 0 8rpx 20rpx rgba(255, 136, 0, 0.3);
}

.action-btn.secondary {
  background: #F5F5F5;
  color: #666;
}
</style>
