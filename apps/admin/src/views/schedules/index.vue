<template>
  <div class="schedules-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排课管理</span>
          <el-button type="primary" @click="handleAdd">新增排课</el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="time" label="时间" width="150" />
        <el-table-column prop="course_name" label="课程" />
        <el-table-column prop="coach_name" label="教练" width="100" />
        <el-table-column prop="venue_name" label="场地" width="120" />
        <el-table-column prop="enrolled" label="报名/容量" width="100">
          <template #default="{ row }">{{ row.enrolled_count }}/{{ row.capacity }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewAttendance(row)">考勤</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref<any[]>([])

onMounted(() => {
  loadData()
})

function loadData() {
  loading.value = true
  setTimeout(() => {
    tableData.value = [
      { date: '2024-02-05', time: '09:00-10:00', course_name: '篮球基础班', coach_name: '张教练', venue_name: '主馆A区', enrolled_count: 12, capacity: 15, status: 'scheduled' },
      { date: '2024-02-05', time: '10:30-12:00', course_name: '篮球提高班', coach_name: '张教练', venue_name: '主馆B区', enrolled_count: 10, capacity: 12, status: 'scheduled' },
      { date: '2024-02-05', time: '14:00-15:00', course_name: '体能训练课', coach_name: '李教练', venue_name: '室外场地', enrolled_count: 18, capacity: 20, status: 'scheduled' }
    ]
    loading.value = false
  }, 500)
}

function getStatusText(status: string) {
  const map: Record<string, string> = { scheduled: '待上课', ongoing: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

function getStatusType(status: string) {
  const map: Record<string, string> = { scheduled: 'info', ongoing: 'warning', completed: 'success', cancelled: 'danger' }
  return map[status] || ''
}

function handleAdd() {
  ElMessage.info('新增排课功能开发中')
}

function handleEdit(row: any) {
  ElMessage.info(`编辑排课: ${row.course_name}`)
}

function viewAttendance(row: any) {
  ElMessage.info(`查看 ${row.course_name} 的考勤`)
}

function handleCancel(row: any) {
  ElMessageBox.confirm(`确定取消 ${row.course_name} 的排课吗？`, '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('取消成功')
      loadData()
    })
}
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
