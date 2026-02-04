<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">新增用户</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="手机号">
          <el-input v-model="searchForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择" clearable>
            <el-option label="家长" value="parent" />
            <el-option label="教练" value="coach" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        class="pagination"
        @change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref<any[]>([])

const searchForm = reactive({
  phone: '',
  role: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

onMounted(() => {
  loadData()
})

function loadData() {
  loading.value = true
  // 模拟数据
  setTimeout(() => {
    tableData.value = [
      { id: 1, phone: '13800138001', nickname: '管理员', role: 'admin', status: 'active', created_at: '2024-01-01' },
      { id: 2, phone: '13800138002', nickname: '张教练', role: 'coach', status: 'active', created_at: '2024-01-05' },
      { id: 3, phone: '13800138003', nickname: '李家长', role: 'parent', status: 'active', created_at: '2024-01-10' }
    ]
    pagination.total = 3
    loading.value = false
  }, 500)
}

function getRoleText(role: string) {
  const map: Record<string, string> = { admin: '管理员', coach: '教练', parent: '家长' }
  return map[role] || role
}

function getRoleType(role: string) {
  const map: Record<string, string> = { admin: 'danger', coach: 'warning', parent: '' }
  return map[role] || ''
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchForm.phone = ''
  searchForm.role = ''
  handleSearch()
}

function handleAdd() {
  ElMessage.info('新增用户功能开发中')
}

function handleEdit(row: any) {
  ElMessage.info(`编辑用户: ${row.nickname}`)
}

function handleDelete(row: any) {
  ElMessageBox.confirm(`确定删除用户 ${row.nickname} 吗？`, '提示', {
    type: 'warning'
  }).then(() => {
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

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
