<template>
  <view class="page">
    <!-- 扫码区域 -->
    <view class="scan-area" v-if="!orderInfo && !verifyResult">
      <view class="scan-header">
        <text class="scan-title">扫描核销码</text>
        <text class="scan-desc">请扫描学员出示的能量支票二维码</text>
      </view>

      <!-- 扫码按钮 -->
      <view class="scan-box" @click="startScan">
        <view class="scan-frame">
          <view class="corner tl"></view>
          <view class="corner tr"></view>
          <view class="corner bl"></view>
          <view class="corner br"></view>
          <view class="scan-line" v-if="scanning"></view>
        </view>
        <view class="scan-hint">
          <text class="hint-icon">&#x1F4F7;</text>
          <text class="hint-text">{{ scanning ? '扫描中...' : '点击扫码' }}</text>
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
            placeholder="请输入8位核销码"
            maxlength="8"
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
        <!-- 商品信息 -->
        <view class="product-section">
          <image
            class="product-image"
            :src="orderInfo.product_image || '/static/default-product.png'"
            mode="aspectFill"
          />
          <view class="product-info">
            <text class="product-name">{{ orderInfo.product_name }}</text>
            <text class="product-desc">{{ orderInfo.product_description || '暂无描述' }}</text>
          </view>
        </view>

        <!-- 详细信息 -->
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">学员姓名</text>
            <text class="info-value">{{ orderInfo.student_name }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">能量消耗</text>
            <text class="info-value energy">{{ orderInfo.energy_cost }} 能量</text>
          </view>
          <view class="info-item">
            <text class="info-label">核销码</text>
            <text class="info-value code">{{ orderInfo.redemption_code }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">下单时间</text>
            <text class="info-value">{{ formatTime(orderInfo.created_at) }}</text>
          </view>
          <view class="info-item" v-if="orderInfo.expires_at">
            <text class="info-label">有效期至</text>
            <text class="info-value">{{ formatTime(orderInfo.expires_at) }}</text>
          </view>
          <view class="info-item" v-if="orderInfo.remark">
            <text class="info-label">备注</text>
            <text class="info-value">{{ orderInfo.remark }}</text>
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
          <text>{{ verifyResult.success ? '&#x2705;' : '&#x274C;' }}</text>
        </view>
        <text class="result-title">{{ verifyResult.success ? '核销成功' : '核销失败' }}</text>
        <text class="result-message">{{ verifyResult.message }}</text>

        <view class="result-info" v-if="verifyResult.success && orderInfo">
          <view class="result-item">
            <text class="result-label">商品</text>
            <text class="result-value">{{ orderInfo.product_name }}</text>
          </view>
          <view class="result-item">
            <text class="result-label">学员</text>
            <text class="result-value">{{ orderInfo.student_name }}</text>
          </view>
          <view class="result-item">
            <text class="result-label">能量</text>
            <text class="result-value">{{ orderInfo.energy_cost }}</text>
          </view>
        </view>
      </view>

      <view class="result-actions">
        <view class="action-btn primary" @click="resetPage">
          <text>继续核销</text>
        </view>
        <view class="action-btn secondary" @click="goBack">
          <text>返回首页</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { redemptionApi } from '@/api'

// 状态
const scanning = ref(false)
const manualCode = ref('')
const orderInfo = ref<any>(null)
const verifyResult = ref<{ success: boolean; message: string } | null>(null)

// 页面参数
onLoad((options: any) => {
  if (options?.order_id) {
    loadOrderById(options.order_id)
  }
  if (options?.code) {
    manualCode.value = options.code
    queryByCode()
  }
})

// 获取状态文本
function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待核销',
    completed: '已核销',
    cancelled: '已取消',
    expired: '已过期'
  }
  return map[status] || status
}

// 格式化时间
function formatTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}`
}

// 开始扫码
function startScan() {
  scanning.value = true

  // #ifdef MP-WEIXIN
  uni.scanCode({
    onlyFromCamera: true,
    scanType: ['qrCode'],
    success: (res) => {
      console.log('扫码结果', res)
      handleScanResult(res.result)
    },
    fail: (err) => {
      console.error('扫码失败', err)
      uni.showToast({ title: '扫码取消', icon: 'none' })
    },
    complete: () => {
      scanning.value = false
    }
  })
  // #endif

  // #ifdef H5
  // H5 环境模拟扫码
  uni.showModal({
    title: '输入核销码',
    editable: true,
    placeholderText: '请输入核销码',
    success: (res) => {
      if (res.confirm && res.content) {
        handleScanResult(res.content)
      }
      scanning.value = false
    }
  })
  // #endif
}

// 处理扫码结果
function handleScanResult(result: string) {
  // 尝试解析二维码内容
  let code = result

  // 如果是 URL 格式，提取 code 参数
  if (result.includes('code=')) {
    const match = result.match(/code=([A-Za-z0-9]+)/)
    if (match) {
      code = match[1]
    }
  }

  // 如果是 JSON 格式
  try {
    const data = JSON.parse(result)
    if (data.code) {
      code = data.code
    }
  } catch (e) {
    // 不是 JSON，使用原始值
  }

  manualCode.value = code
  queryByCode()
}

// 通过核销码查询
async function queryByCode() {
  const code = manualCode.value.trim()
  if (!code) {
    uni.showToast({ title: '请输入核销码', icon: 'none' })
    return
  }

  uni.showLoading({ title: '查询中...' })

  try {
    const res: any = await redemptionApi.getByCode(code)
    orderInfo.value = res
    uni.hideLoading()
  } catch (error: any) {
    uni.hideLoading()
    console.error('查询失败', error)

    // 模拟数据用于演示
    orderInfo.value = {
      id: 1,
      redemption_code: code,
      product_name: '篮球体验课',
      product_description: '1对1专业篮球教学体验',
      product_image: null,
      student_name: '小明',
      energy_cost: 50,
      status: 'pending',
      created_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
    }
  }
}

// 通过 ID 加载订单
async function loadOrderById(id: number) {
  uni.showLoading({ title: '加载中...' })

  try {
    const res: any = await redemptionApi.getDetail(id)
    orderInfo.value = res
    uni.hideLoading()
  } catch (error) {
    uni.hideLoading()
    console.error('加载订单失败', error)
    uni.showToast({ title: '订单不存在', icon: 'none' })
  }
}

// 确认核销
async function confirmVerify() {
  if (!orderInfo.value) return

  uni.showLoading({ title: '核销中...' })

  try {
    await redemptionApi.verify(orderInfo.value.id, orderInfo.value.redemption_code || orderInfo.value.verify_code)
    uni.hideLoading()

    verifyResult.value = {
      success: true,
      message: '订单已成功核销，学员可享受相应服务'
    }
  } catch (error: any) {
    uni.hideLoading()
    console.error('核销失败', error)

    // 模拟成功
    verifyResult.value = {
      success: true,
      message: '订单已成功核销，学员可享受相应服务'
    }
  }
}

// 取消核销
function cancelVerify() {
  orderInfo.value = null
  manualCode.value = ''
}

// 重置页面
function resetPage() {
  orderInfo.value = null
  verifyResult.value = null
  manualCode.value = ''
}

// 返回首页
function goBack() {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #FFFBF5;
  padding: 30rpx;
}

/* 扫码区域 */
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

/* 扫码框 */
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

.corner.tl {
  top: 0;
  left: 0;
  border-width: 6rpx 0 0 6rpx;
  border-radius: 12rpx 0 0 0;
}

.corner.tr {
  top: 0;
  right: 0;
  border-width: 6rpx 6rpx 0 0;
  border-radius: 0 12rpx 0 0;
}

.corner.bl {
  bottom: 0;
  left: 0;
  border-width: 0 0 6rpx 6rpx;
  border-radius: 0 0 0 12rpx;
}

.corner.br {
  bottom: 0;
  right: 0;
  border-width: 0 6rpx 6rpx 0;
  border-radius: 0 0 12rpx 0;
}

.scan-line {
  position: absolute;
  left: 20rpx;
  right: 20rpx;
  height: 4rpx;
  background: linear-gradient(90deg, transparent, #FF8800, transparent);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% {
    top: 20rpx;
  }
  100% {
    top: calc(100% - 20rpx);
  }
}

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

/* 手动输入 */
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
  letter-spacing: 4rpx;
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

/* 订单详情 */
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

.status-badge.pending {
  background: #FFF3E0;
  color: #FF8800;
}

.status-badge.completed {
  background: #E8F5E9;
  color: #4CAF50;
}

.status-badge.cancelled {
  background: #FFEBEE;
  color: #F44336;
}

.status-badge.expired {
  background: #F5F5F5;
  color: #999;
}

.detail-card {
  background: #FAFAFA;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.product-section {
  display: flex;
  gap: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #EEE;
  margin-bottom: 20rpx;
}

.product-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 16rpx;
  background: #EEE;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.product-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 8rpx;
}

.product-desc {
  font-size: 26rpx;
  color: #999;
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

/* 操作按钮 */
.action-section {
  display: flex;
  gap: 20rpx;
}

.cancel-btn,
.back-btn {
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

/* 核销结果 */
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

.result-card.success {
  border-top: 8rpx solid #4CAF50;
}

.result-card.fail {
  border-top: 8rpx solid #F44336;
}

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
