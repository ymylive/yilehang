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
            <div class="stat-value">{{ stats.totalStudents }}</div>
            <div class="stat-label">学员总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon coaches">
            <el-icon><Avatar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCoaches }}</div>
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
            <div class="stat-value">{{ stats.todayCourses }}</div>
            <div class="stat-label">今日课程</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon revenue">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.monthRevenue }}</div>
            <div class="stat-label">本月营收</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>营收趋势</span>
          </template>
          <div ref="revenueChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>课程分布</span>
          </template>
          <div ref="courseChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近数据 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近报名</span>
          </template>
          <el-table :data="recentEnrollments" stripe>
            <el-table-column prop="studentName" label="学员" />
            <el-table-column prop="courseName" label="课程" />
            <el-table-column prop="time" label="时间" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日课程</span>
          </template>
          <el-table :data="todaySchedules" stripe>
            <el-table-column prop="time" label="时间" width="100" />
            <el-table-column prop="courseName" label="课程" />
            <el-table-column prop="coachName" label="教练" />
            <el-table-column prop="enrolled" label="人数" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const revenueChartRef = ref<HTMLElement>()
const courseChartRef = ref<HTMLElement>()

// 统计数据
const stats = ref({
  totalStudents: 256,
  totalCoaches: 12,
  todayCourses: 8,
  monthRevenue: '52,800'
})

// 最近报名
const recentEnrollments = ref([
  { studentName: '小明', courseName: '篮球基础班', time: '10分钟前' },
  { studentName: '小红', courseName: '体能训练课', time: '30分钟前' },
  { studentName: '小刚', courseName: '篮球提高班', time: '1小时前' }
])

// 今日课程
const todaySchedules = ref([
  { time: '09:00', courseName: '篮球基础班', coachName: '张教练', enrolled: '12/15' },
  { time: '10:30', courseName: '体能训练课', coachName: '李教练', enrolled: '18/20' },
  { time: '14:00', courseName: '篮球提高班', coachName: '张教练', enrolled: '10/12' }
])

onMounted(() => {
  initRevenueChart()
  initCourseChart()
})

function initRevenueChart() {
  if (!revenueChartRef.value) return

  const chart = echarts.init(revenueChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: { type: 'value' },
    series: [{
      name: '营收',
      type: 'line',
      smooth: true,
      data: [42000, 45000, 48000, 51000, 49000, 52800],
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

function initCourseChart() {
  if (!courseChartRef.value) return

  const chart = echarts.init(courseChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 45, name: '篮球', itemStyle: { color: '#4CAF50' } },
        { value: 25, name: '体能', itemStyle: { color: '#2196F3' } },
        { value: 15, name: '足球', itemStyle: { color: '#FF9800' } },
        { value: 15, name: '其他', itemStyle: { color: '#9C27B0' } }
      ]
    }]
  })
}
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

  .chart-row {
    margin-bottom: 20px;
  }

  .chart {
    height: 300px;
  }
}
</style>
