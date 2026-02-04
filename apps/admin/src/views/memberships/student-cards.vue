<template>
  <div class="student-cards-page">
    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="学员">
          <el-input v-model="filters.studentName" placeholder="学员姓名" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="有效" value="active" />
            <el-option label="已过期" value="expired" />
            <el-option label="已用完" value="exhausted" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="action-card">
      <el-button type="primary" @click="handleRecharge">手动充值</el-button>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <el-table :data="studentCards" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="student_name" label="学员" width="120" />
        <el-table-column prop="card_name" label="课时卡" width="120" />
        <el-table-column label="剩余/总计" width="120">
          <template #default="{ row }">
            <span :class="{ 'low-balance': row.remaining_times <= 3 }">
              {{ row.remaining_times }} / {{ row.total_times }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="expire_date" label="到期日期" width="120">
          <template #default="{ row }">
            <span :class="{ 'expiring-soon': isExpiringSoon(row.expire_date) }">
              {{ row.expire_date }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="purchase_date" label="购买时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewTransactions(row)">消费记录</el-button>
            <el-button size="small" type="primary" @click="handleAddTimes(row)">增加课时</el-button>
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

    <!-- 手动充值弹窗 -->
    <el-dialog v-model="rechargeVisible" title="手动充值" width="500px">
      <el-form ref="rechargeFormRef" :model="rechargeForm" :rules="rechargeRules" label-width="100px">
        <el-form-item label="学员" prop="student_id">
          <el-select v-model="rechargeForm.student_id" filterable placeholder="选择学员">
            <el-option v-for="s in students" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课时卡" prop="card_id">
          <el-select v-model="rechargeForm.card_id" placeholder="选择课时卡">
            <el-option v-for="c in availableCards" :key="c.id" :label="`${c.name} (¥${c.price})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="rechargeForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRechargeSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 增加课时弹窗 -->
    <el-dialog v-model="addTimesVisible" title="增加课时" width="400px">
      <el-form ref="addTimesFormRef" :model="addTimesForm" :rules="addTimesRules" label-width="100px">
        <el-form-item label="增加次数" prop="times">
          <el-input-number v-model="addTimesForm.times" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="原因" prop="reason">
          <el-select v-model="addTimesForm.reason">
            <el-option label="赠送" value="gift" />
            <el-option label="补偿" value="compensation" />
            <el-option label="续费" value="renewal" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="addTimesForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addTimesVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddTimesSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 消费记录弹窗 -->
    <el-dialog v-model="transactionsVisible" title="消费记录" width="700px">
      <el-table :data="transactions" stripe>
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'consume' ? 'danger' : 'success'" size="small">
              {{ getTransactionTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="times_change" label="课时变动" width="100">
          <template #default="{ row }">
            <span :class="row.times_change > 0 ? 'positive' : 'negative'">
              {{ row.times_change > 0 ? '+' : '' }}{{ row.times_change }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

interface StudentCard {
  id: number
  student_id: number
  student_name: string
  card_id: number
  card_name: string
  remaining_times: number
  total_times: number
  expire_date: string
  status: string
  purchase_date: string
}

interface Transaction {
  id: number
  created_at: string
  type: string
  times_change: number
  description: string
}

const loading = ref(false)
const studentCards = ref<StudentCard[]>([])
const students = ref<{ id: number; name: string }[]>([])
const availableCards = ref<{ id: number; name: string; price: number }[]>([])
const transactions = ref<Transaction[]>([])

const rechargeVisible = ref(false)
const addTimesVisible = ref(false)
const transactionsVisible = ref(false)
const currentCard = ref<StudentCard | null>(null)

const rechargeFormRef = ref<FormInstance>()
const addTimesFormRef = ref<FormInstance>()

const filters = reactive({
  studentName: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const rechargeForm = reactive({
  student_id: null as number | null,
  card_id: null as number | null,
  remark: ''
})

const rechargeRules: FormRules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  card_id: [{ required: true, message: '请选择课时卡', trigger: 'change' }]
}

const addTimesForm = reactive({
  times: 1,
  reason: 'gift',
  remark: ''
})

const addTimesRules: FormRules = {
  times: [{ required: true, message: '请输入次数', trigger: 'blur' }],
  reason: [{ required: true, message: '请选择原因', trigger: 'change' }]
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    active: '有效',
    expired: '已过期',
    exhausted: '已用完'
  }
  return map[status] || status
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    active: 'success',
    expired: 'info',
    exhausted: 'warning'
  }
  return map[status] || 'info'
}

function getTransactionTypeText(type: string): string {
  const map: Record<string, string> = {
    purchase: '购买',
    consume: '消费',
    refund: '退款',
    gift: '赠送'
  }
  return map[type] || type
}

function isExpiringSoon(dateStr: string): boolean {
  const expireDate = new Date(dateStr)
  const now = new Date()
  const diffDays = (expireDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  return diffDays <= 7 && diffDays > 0
}

async function fetchStudentCards() {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    studentCards.value = [
      { id: 1, student_id: 1, student_name: '小明', card_id: 2, card_name: '10次卡', remaining_times: 8, total_times: 10, expire_date: '2026-06-30', status: 'active', purchase_date: '2026-01-15 10:30' },
      { id: 2, student_id: 2, student_name: '小红', card_id: 2, card_name: '10次卡', remaining_times: 2, total_times: 10, expire_date: '2026-02-10', status: 'active', purchase_date: '2026-01-10 14:20' },
      { id: 3, student_id: 3, student_name: '小刚', card_id: 3, card_name: '20次卡', remaining_times: 15, total_times: 20, expire_date: '2026-08-15', status: 'active', purchase_date: '2026-01-20 09:00' },
      { id: 4, student_id: 4, student_name: '小美', card_id: 4, card_name: '月卡', remaining_times: 0, total_times: 0, expire_date: '2026-01-31', status: 'expired', purchase_date: '2025-12-31 16:00' }
    ]
    pagination.total = studentCards.value.length
  } finally {
    loading.value = false
  }
}

async function fetchStudents() {
  students.value = [
    { id: 1, name: '小明' },
    { id: 2, name: '小红' },
    { id: 3, name: '小刚' },
    { id: 4, name: '小美' },
    { id: 5, name: '小强' }
  ]
}

async function fetchAvailableCards() {
  availableCards.value = [
    { id: 1, name: '体验卡', price: 99 },
    { id: 2, name: '10次卡', price: 1800 },
    { id: 3, name: '20次卡', price: 3200 },
    { id: 4, name: '月卡', price: 2500 },
    { id: 5, name: '季卡', price: 6000 }
  ]
}

function handleSearch() {
  pagination.page = 1
  fetchStudentCards()
}

function handleReset() {
  filters.studentName = ''
  filters.status = ''
  handleSearch()
}

function handleSizeChange() {
  pagination.page = 1
  fetchStudentCards()
}

function handlePageChange() {
  fetchStudentCards()
}

function handleRecharge() {
  rechargeForm.student_id = null
  rechargeForm.card_id = null
  rechargeForm.remark = ''
  rechargeVisible.value = true
}

async function handleRechargeSubmit() {
  if (!rechargeFormRef.value) return

  try {
    await rechargeFormRef.value.validate()
    // TODO: 调用API充值
    rechargeVisible.value = false
    ElMessage.success('充值成功')
    fetchStudentCards()
  } catch {
    // 验证失败
  }
}

function handleAddTimes(row: StudentCard) {
  currentCard.value = row
  addTimesForm.times = 1
  addTimesForm.reason = 'gift'
  addTimesForm.remark = ''
  addTimesVisible.value = true
}

async function handleAddTimesSubmit() {
  if (!addTimesFormRef.value || !currentCard.value) return

  try {
    await addTimesFormRef.value.validate()
    // TODO: 调用API增加课时
    currentCard.value.remaining_times += addTimesForm.times
    addTimesVisible.value = false
    ElMessage.success('课时增加成功')
  } catch {
    // 验证失败
  }
}

function handleViewTransactions(row: StudentCard) {
  currentCard.value = row
  // TODO: 调用API获取消费记录
  transactions.value = [
    { id: 1, created_at: '2026-02-04 09:30', type: 'consume', times_change: -1, description: '私教课消费' },
    { id: 2, created_at: '2026-02-01 10:00', type: 'consume', times_change: -1, description: '私教课消费' },
    { id: 3, created_at: '2026-01-28 14:30', type: 'gift', times_change: 2, description: '活动赠送' },
    { id: 4, created_at: '2026-01-15 10:30', type: 'purchase', times_change: 10, description: '购买10次卡' }
  ]
  transactionsVisible.value = true
}

onMounted(() => {
  fetchStudentCards()
  fetchStudents()
  fetchAvailableCards()
})
</script>

<style scoped lang="scss">
.student-cards-page {
  .filter-card,
  .action-card {
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }

  .low-balance {
    color: #f56c6c;
    font-weight: bold;
  }

  .expiring-soon {
    color: #e6a23c;
  }

  .positive {
    color: #67c23a;
  }

  .negative {
    color: #f56c6c;
  }
}
</style>
