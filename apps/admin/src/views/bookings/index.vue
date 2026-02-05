<template>
  <div class="bookings-page">
    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="学员">
          <el-input v-model="filters.studentName" placeholder="学员姓名" clearable />
        </el-form-item>
        <el-form-item label="教练">
          <el-select v-model="filters.coachId" placeholder="选择教练" clearable>
            <el-option v-for="coach in coaches" :key="coach.id" :label="coach.name" :value="coach.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="预约状态" clearable>
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="未到" value="no_show" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预约列表</span>
          <el-button type="primary" @click="handleExport">导出</el-button>
        </div>
      </template>

      <el-table :data="bookings" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="student_name" label="学员" width="100" />
        <el-table-column prop="coach_name" label="教练" width="100" />
        <el-table-column label="预约时间" width="200">
          <template #default="{ row }">
            {{ formatDate(row.booking_date) }} {{ formatTime(row.start_time) }}-{{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="course_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.course_type === 'private' ? 'primary' : 'success'" size="small">
              {{ row.course_type === 'private' ? '私教课' : '小班课' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="success"
              @click="handleConfirm(row)"
            >确认</el-button>
            <el-button
              v-if="['pending', 'confirmed'].includes(row.status)"
              size="small"
              type="danger"
              @click="handleCancel(row)"
            >取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="预约详情" width="600px">
      <el-descriptions :column="2" border v-if="currentBooking">
        <el-descriptions-item label="预约ID">{{ currentBooking.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentBooking.status)">
            {{ getStatusText(currentBooking.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="学员">{{ currentBooking.student_name }}</el-descriptions-item>
        <el-descriptions-item label="教练">{{ currentBooking.coach_name }}</el-descriptions-item>
        <el-descriptions-item label="预约日期">{{ formatDate(currentBooking.booking_date) }}</el-descriptions-item>
        <el-descriptions-item label="时间段">
          {{ formatTime(currentBooking.start_time) }} - {{ formatTime(currentBooking.end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="课程类型">
          {{ currentBooking.course_type === 'private' ? '私教课' : '小班课' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(currentBooking.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="取消原因" :span="2" v-if="currentBooking.cancel_reason">
          {{ currentBooking.cancel_reason }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bookingApi, coachApi } from '@/api'

interface Booking {
  id: number
  student_id: number
  student_name: string
  coach_id: number
  coach_name: string
  booking_date: string
  start_time: string
  end_time: string
  course_type: string
  status: string
  cancel_reason?: string
  created_at: string
}

interface Coach {
  id: number
  name: string
}

const loading = ref(false)
const bookings = ref<Booking[]>([])
const coaches = ref<Coach[]>([])
const detailVisible = ref(false)
const currentBooking = ref<Booking | null>(null)

const filters = reactive({
  studentName: '',
  coachId: null as number | null,
  status: '',
  dateRange: null as [Date, Date] | null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function formatTime(timeStr: string): string {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${formatDate(dateStr)} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
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

async function fetchBookings() {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.coachId) params.coach_id = filters.coachId
    if (filters.status) params.status = filters.status
    if (filters.studentName) params.student_name = filters.studentName
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0].toISOString().split('T')[0]
      params.end_date = filters.dateRange[1].toISOString().split('T')[0]
    }

    const res: any = await bookingApi.list(params)
    bookings.value = res.items || res.data || res || []
    pagination.total = res.total || bookings.value.length
  } catch (error: any) {
    ElMessage.error(error.message || '获取预约列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchCoaches() {
  try {
    const res: any = await coachApi.list({ page_size: 100 })
    const coachList = res.items || res.data || res || []
    coaches.value = coachList.map((c: any) => ({
      id: c.id,
      name: c.name || c.user?.nickname || `教练${c.id}`
    }))
  } catch (error: any) {
    console.error('获取教练列表失败:', error)
  }
}

function handleSearch() {
  pagination.page = 1
  fetchBookings()
}

function handleReset() {
  filters.studentName = ''
  filters.coachId = null
  filters.status = ''
  filters.dateRange = null
  handleSearch()
}

function handleSizeChange() {
  pagination.page = 1
  fetchBookings()
}

function handlePageChange() {
  fetchBookings()
}

function handleView(row: Booking) {
  currentBooking.value = row
  detailVisible.value = true
}

async function handleConfirm(row: Booking) {
  try {
    await ElMessageBox.confirm('确定要确认此预约吗？', '确认预约')
    await bookingApi.confirm(row.id)
    row.status = 'confirmed'
    ElMessage.success('预约已确认')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '确认预约失败')
    }
  }
}

async function handleCancel(row: Booking) {
  try {
    const { value } = await ElMessageBox.prompt('请输入取消原因', '取消预约', {
      inputPattern: /.+/,
      inputErrorMessage: '请输入取消原因'
    })
    await bookingApi.cancel(row.id, value)
    row.status = 'cancelled'
    row.cancel_reason = value
    ElMessage.success('预约已取消')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消预约失败')
    }
  }
}

function handleExport() {
  ElMessage.info('导出功能开发中')
}

onMounted(() => {
  fetchBookings()
  fetchCoaches()
})
</script>

<style scoped lang="scss">
.bookings-page {
  .filter-card {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}
</style>
