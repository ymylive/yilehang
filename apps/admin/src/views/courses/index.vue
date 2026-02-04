<template>
  <div class="courses-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" @click="handleAdd">新增课程</el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="code" label="课程编号" width="120" />
        <el-table-column prop="name" label="课程名称" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="duration" label="时长" width="100">
          <template #default="{ row }">{{ row.duration }}分钟</template>
        </el-table-column>
        <el-table-column prop="max_students" label="容量" width="80" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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
      { code: 'BB001', name: '篮球基础班', type: 'group', category: '篮球', duration: 60, max_students: 15, price: 150, status: 'active' },
      { code: 'BB002', name: '篮球提高班', type: 'group', category: '篮球', duration: 90, max_students: 12, price: 200, status: 'active' },
      { code: 'PE001', name: '体能训练课', type: 'group', category: '体能', duration: 60, max_students: 20, price: 100, status: 'active' },
      { code: 'PT001', name: '私教一对一', type: 'private', category: '篮球', duration: 60, max_students: 1, price: 300, status: 'active' }
    ]
    loading.value = false
  }, 500)
}

function getTypeText(type: string) {
  const map: Record<string, string> = { group: '团课', private: '私教', trial: '体验' }
  return map[type] || type
}

function handleAdd() {
  ElMessage.info('新增课程功能开发中')
}

function handleEdit(row: any) {
  ElMessage.info(`编辑课程: ${row.name}`)
}

function handleDelete(row: any) {
  ElMessageBox.confirm(`确定删除课程 ${row.name} 吗？`, '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success('删除成功')
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
