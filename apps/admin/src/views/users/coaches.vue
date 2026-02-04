<template>
  <div class="coaches-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教练管理</span>
          <el-button type="primary" @click="handleAdd">新增教练</el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="coach_no" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="specialty" label="专长" />
        <el-table-column prop="student_count" label="学员数" width="100" />
        <el-table-column prop="hourly_rate" label="课时费" width="100">
          <template #default="{ row }">¥{{ row.hourly_rate }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="viewSchedule(row)">排课</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref<any[]>([])

onMounted(() => {
  loadData()
})

function loadData() {
  loading.value = true
  setTimeout(() => {
    tableData.value = [
      { coach_no: 'C00000001', name: '张教练', phone: '13800138002', specialty: '篮球、体能', student_count: 25, hourly_rate: 200, status: 'active' },
      { coach_no: 'C00000002', name: '李教练', phone: '13800138004', specialty: '足球', student_count: 18, hourly_rate: 180, status: 'active' }
    ]
    loading.value = false
  }, 500)
}

function handleAdd() {
  ElMessage.info('新增教练功能开发中')
}

function handleEdit(row: any) {
  ElMessage.info(`编辑教练: ${row.name}`)
}

function viewSchedule(row: any) {
  ElMessage.info(`查看 ${row.name} 的排课`)
}
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
