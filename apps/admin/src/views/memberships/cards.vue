<template>
  <div class="membership-cards-page">
    <!-- 操作栏 -->
    <el-card class="action-card">
      <el-button type="primary" @click="handleAdd">新增课时卡</el-button>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <el-table :data="cards" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="卡名" width="150" />
        <el-table-column prop="card_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.card_type === 'times' ? 'primary' : 'success'" size="small">
              {{ row.card_type === 'times' ? '次卡' : '时长卡' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="规格" width="120">
          <template #default="{ row }">
            {{ row.card_type === 'times' ? `${row.total_times}次` : `${row.duration_days}天` }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="售价" width="120">
          <template #default="{ row }">
            ¥{{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="original_price" label="原价" width="120">
          <template #default="{ row }">
            <span class="original-price">¥{{ row.original_price?.toFixed(2) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="course_type" label="适用课程" width="100">
          <template #default="{ row }">
            {{ getCourseTypeText(row.course_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="handleStatusChange(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课时卡' : '新增课时卡'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="卡名" prop="name">
          <el-input v-model="form.name" placeholder="请输入卡名" />
        </el-form-item>
        <el-form-item label="类型" prop="card_type">
          <el-radio-group v-model="form.card_type">
            <el-radio value="times">次卡</el-radio>
            <el-radio value="duration">时长卡</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.card_type === 'times'" label="总次数" prop="total_times">
          <el-input-number v-model="form.total_times" :min="1" :max="999" />
        </el-form-item>
        <el-form-item v-if="form.card_type === 'duration'" label="有效天数" prop="duration_days">
          <el-input-number v-model="form.duration_days" :min="1" :max="365" />
        </el-form-item>
        <el-form-item label="售价" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" :step="100" />
        </el-form-item>
        <el-form-item label="原价" prop="original_price">
          <el-input-number v-model="form.original_price" :min="0" :precision="2" :step="100" />
        </el-form-item>
        <el-form-item label="适用课程" prop="course_type">
          <el-select v-model="form.course_type">
            <el-option label="全部课程" value="all" />
            <el-option label="私教课" value="private" />
            <el-option label="小班课" value="group" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

interface MembershipCard {
  id: number
  name: string
  card_type: string
  total_times?: number
  duration_days?: number
  price: number
  original_price?: number
  course_type: string
  description?: string
  is_active: boolean
}

const loading = ref(false)
const cards = ref<MembershipCard[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: 0,
  name: '',
  card_type: 'times',
  total_times: 10,
  duration_days: 30,
  price: 0,
  original_price: 0,
  course_type: 'all',
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入卡名', trigger: 'blur' }],
  card_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
  course_type: [{ required: true, message: '请选择适用课程', trigger: 'change' }]
}

function getCourseTypeText(type: string): string {
  const map: Record<string, string> = {
    all: '全部',
    private: '私教课',
    group: '小班课'
  }
  return map[type] || type
}

async function fetchCards() {
  loading.value = true
  try {
    // TODO: 调用API获取课时卡列表
    await new Promise(resolve => setTimeout(resolve, 500))

    cards.value = [
      { id: 1, name: '体验卡', card_type: 'times', total_times: 2, price: 99, original_price: 200, course_type: 'all', is_active: true },
      { id: 2, name: '10次卡', card_type: 'times', total_times: 10, price: 1800, original_price: 2000, course_type: 'all', is_active: true },
      { id: 3, name: '20次卡', card_type: 'times', total_times: 20, price: 3200, original_price: 4000, course_type: 'all', is_active: true },
      { id: 4, name: '月卡', card_type: 'duration', duration_days: 30, price: 2500, original_price: 3000, course_type: 'all', is_active: true },
      { id: 5, name: '季卡', card_type: 'duration', duration_days: 90, price: 6000, original_price: 9000, course_type: 'all', is_active: true }
    ]
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.id = 0
  form.name = ''
  form.card_type = 'times'
  form.total_times = 10
  form.duration_days = 30
  form.price = 0
  form.original_price = 0
  form.course_type = 'all'
  form.description = ''
}

function handleAdd() {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row: MembershipCard) {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

async function handleDelete(row: MembershipCard) {
  try {
    await ElMessageBox.confirm('确定要删除此课时卡吗？', '删除确认', { type: 'warning' })
    // TODO: 调用API删除
    cards.value = cards.value.filter(c => c.id !== row.id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

async function handleStatusChange(row: MembershipCard) {
  // TODO: 调用API更新状态
  ElMessage.success(`已${row.is_active ? '启用' : '停用'}`)
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    // TODO: 调用API保存
    if (isEdit.value) {
      const index = cards.value.findIndex(c => c.id === form.id)
      if (index !== -1) {
        cards.value[index] = { ...form, is_active: cards.value[index].is_active }
      }
    } else {
      cards.value.push({
        ...form,
        id: Date.now(),
        is_active: true
      })
    }
    dialogVisible.value = false
    ElMessage.success(isEdit.value ? '编辑成功' : '新增成功')
  } catch {
    // 验证失败
  }
}

onMounted(() => {
  fetchCards()
})
</script>

<style scoped lang="scss">
.membership-cards-page {
  .action-card {
    margin-bottom: 20px;
  }

  .original-price {
    text-decoration: line-through;
    color: #999;
  }
}
</style>
