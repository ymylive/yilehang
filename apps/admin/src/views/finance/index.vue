<template>
  <div class="finance-page">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">¥52,800</div>
            <div class="stat-label">本月营收</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">¥328,500</div>
            <div class="stat-label">年度营收</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">156</div>
            <div class="stat-label">本月订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">¥12,500</div>
            <div class="stat-label">待收款</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <span>订单列表</span>
      </template>
      <el-table :data="tableData" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="student_name" label="学员" />
        <el-table-column prop="course_name" label="课程" />
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="pay_method" label="支付方式" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'paid' ? 'success' : 'warning'">
              {{ row.status === 'paid' ? '已支付' : '待支付' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  { order_no: 'ORD202402050001', student_name: '小明', course_name: '篮球基础班(20课时)', amount: 3000, pay_method: '微信支付', status: 'paid', created_at: '2024-02-05 10:30' },
  { order_no: 'ORD202402040002', student_name: '小红', course_name: '体能训练课(10课时)', amount: 1000, pay_method: '支付宝', status: 'paid', created_at: '2024-02-04 15:20' }
])
</script>

<style scoped lang="scss">
.stat-cards {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #4CAF50;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}
</style>
