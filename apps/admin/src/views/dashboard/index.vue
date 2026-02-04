<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon students">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.students?.total || 0 }}</div>
            <div class="stat-label">学员总数</div>
            <div class="stat-sub">本月新增 {{ overview.students?.new_this_month || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon coaches">
            <el-icon><Avatar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.coaches?.total || 0 }}</div>
            <div class="stat-label">教练总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon courses">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.bookings?.today || 0 }}</div>
            <div class="stat-label">今日预约</div>
            <div class="stat-sub">待确认 {{ overview.bookings?.pending || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon revenue">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ formatMoney(overview.revenue?.this_month) }}</div>
            <div class="stat-label">本月营收</div>
            <div class="stat-sub" :class="{ positive: overview.revenue?.growth_rate > 0 }">
              {{ overview.revenue?.growth_rate > 0 ? '+' : '' }}{{ overview.revenue?.growth_rate || 0 }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>营收趋势</span>
              <el-button text @click="loadRevenueStats">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div v-loading="loadingRevenue" ref="revenueChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>预约统计 (近7天)</span>
              <el-button text @click="loadBookingStats">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div v-loading="loadingBooking" ref="bookingChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近数据 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近预约</span>
              <el-button text @click="loadRecentBookings">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentBookings" stripe v-loading="loadingRecent">
            <el-table-column prop="student_name" label="学员" width="120" />
            <el-table-column prop="coach_name" label="教练" width="120" />
            <el-table-column prop="booking_date" label="日期" width="120" />
            <el-table-column label="时间" width="120">
              <template #default="{ row }">
                {{ row.start_time }} - {{ row.end_time }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { UserFilled, Avatar, Reading, Money, Refresh } from '@element-plus/icons-vue'
import api from '@/api'

const revenueChartRef = ref<HTMLElement>()
const bookingChartRef = ref<HTMLElement>()

// 加载状态
const loadingOverview = ref(false)
const loadingRevenue = ref(false)
const loadingBooking = ref(false)
const loadingRecent = ref(false)

// 数据
const overview = ref<any>({})
const recentBookings = ref<any[]>([])
const revenueStats = ref<any[]>([])
const bookingStats = ref<any[]>([])

let revenueChart: echarts.ECharts | null = null
let bookingChart: echarts.ECharts | null = null

function formatMoney(value: number | undefined): string {
  if (!value) return '0'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}-${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    pending: 'warning',
    confirmed: 'primary',
    completed: 'success',
    cancelled: 'info',
    no_show: 'danger'
  }
  return map[status] || 'info'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
    no_show: '未到'
  }
  return map[status] || status
}

async function loadOverview() {
  loadingOverview.value = true
  try {
    overview.value = await api.get('/dashboard/overview')
  } catch (error) {
    console.error('获取概览数据失败:', error)
  } finally {
    loadingOverview.value = false
  }
}

async function loadRecentBookings() {
  loadingRecent.value = true
  try {
    recentBookings.value = await api.get('/dashboard/recent-bookings', { params: { limit: 10 } })
  } catch (error) {
    console.error('获取最近预约失败:', error)
  } finally {
    loadingRecent.value = false
  }
}

async function loadRevenueStats() {
  loadingRevenue.value = true
  try {
    revenueStats.value = await api.get('/dashboard/revenue-stats', { params: { months: 6 } })
    await nextTick()
    initRevenueChart()
  } catch (error) {
    console.error('获取营收统计失败:', error)
  } finally {
    loadingRevenue.value = false
  }
}

async function loadBookingStats() {
  loadingBooking.value = true
  try {
    bookingStats.value = await api.get('/dashboard/booking-stats', { params: { days: 7 } })
    await nextTick()
    initBookingChart()
  } catch (error) {
    console.error('获取预约统计失败:', error)
  } finally {
    loadingBooking.value = false
  }
}

function initRevenueChart() {
  if (!revenueChartRef.value) return

  if (revenueChart) {
    revenueChart.dispose()
  }

  revenueChart = echarts.init(revenueChartRef.value)
  revenueChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: revenueStats.value.map(item => item.month)
    },
    yAxis: { type: 'value' },
    series: [{
      name: '营收',
      type: 'line',
      smooth: true,
      data: revenueStats.value.map(item => item.revenue),
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(76, 175, 80, 0.3)' },
          { offset: 1, color: 'rgba(76, 175, 80, 0.05)' }
        ])
      },
      lineStyle: { color: '#4CAF50' },
      itemStyle: { color: '#4CAF50' }
    }]
  })
}

function initBookingChart() {
  if (!bookingChartRef.value) return

  if (bookingChart) {
    bookingChart.dispose()
  }

  bookingChart = echarts.init(bookingChartRef.value)
  bookingChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['预约数', '完成数'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: bookingStats.value.map(item => {
        const date = new Date(item.date)
        return `${date.getMonth() + 1}-${date.getDate()}`
      })
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '预约数',
        type: 'bar',
        data: bookingStats.value.map(item => item.total),
        itemStyle: { color: '#2196F3' }
      },
      {
        name: '完成数',
        type: 'bar',
        data: bookingStats.value.map(item => item.completed),
        itemStyle: { color: '#4CAF50' }
      }
    ]
  })
}

onMounted(() => {
  loadOverview()
  loadRecentBookings()
  loadRevenueStats()
  loadBookingStats()
})
</script>

<style scoped lang="scss">
.dashboard {
  .stat-cards {
    margin-bottom: 20px;
  }

  .stat-card {
    :deep(.el-card__body) {
      display: flex;
      align-items: center;
      gap: 16px;
    }
  }

  .stat-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: #fff;

    &.students { background: linear-gradient(135deg, #4CAF50, #81C784); }
    &.coaches { background: linear-gradient(135deg, #2196F3, #64B5F6); }
    &.courses { background: linear-gradient(135deg, #FF9800, #FFB74D); }
    &.revenue { background: linear-gradient(135deg, #9C27B0, #BA68C8); }
  }

  .stat-value {
    font-size: 28px;
    font-weight: bold;
    color: #333;
  }

  .stat-label {
    font-size: 14px;
    color: #999;
  }

  .stat-sub {
    font-size: 12px;
    color: #999;
    margin-top: 4px;

    &.positive {
      color: #4CAF50;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .chart-row {
    margin-bottom: 20px;
  }

  .chart {
    height: 300px;
  }
}
</style>
