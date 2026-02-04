<template>
  <div class="students-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学员管理</span>
          <el-button type="primary" @click="handleAdd">新增学员</el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="school" label="学校" />
        <el-table-column prop="grade" label="年级" width="100" />
        <el-table-column prop="remaining_lessons" label="剩余课时" width="100" />
        <el-table-column prop="coach_name" label="负责教练" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '在读' : '休学' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewGrowth(row)">成长档案</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
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
      { student_no: 'S00000001', name: '小明', gender: '男', school: '阳光小学', grade: '三年级', remaining_lessons: 20, coach_name: '张教练', status: 'active' },
      { student_no: 'S00000002', name: '小红', gender: '女', school: '阳光小学', grade: '二年级', remaining_lessons: 15, coach_name: '张教练', status: 'active' }
    ]
    loading.value = false
  }, 500)
}

function handleAdd() {
  ElMessage.info('新增学员功能开发中')
}

function handleEdit(row: any) {
  ElMessage.info(`编辑学员: ${row.name}`)
}

function viewGrowth(row: any) {
  ElMessage.info(`查看 ${row.name} 的成长档案`)
}
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
