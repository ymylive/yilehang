<template>
  <div class="analytics-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>学员增长趋势</span>
          </template>
          <div ref="studentChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>课程热度排行</span>
          </template>
          <div ref="courseChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>训练数据统计</span>
          </template>
          <div ref="trainingChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>教练工作量</span>
          </template>
          <div ref="coachChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const studentChartRef = ref<HTMLElement>()
const courseChartRef = ref<HTMLElement>()
const trainingChartRef = ref<HTMLElement>()
const coachChartRef = ref<HTMLElement>()

onMounted(() => {
  initStudentChart()
  initCourseChart()
  initTrainingChart()
  initCoachChart()
})

function initStudentChart() {
  if (!studentChartRef.value) return
  const chart = echarts.init(studentChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
    yAxis: { type: 'value' },
    series: [{
      name: '新增学员',
      type: 'bar',
      data: [15, 22, 18, 25, 20, 28],
      itemStyle: { color: '#4CAF50' }
    }]
  })
}

function initCourseChart() {
  if (!courseChartRef.value) return
  const chart = echarts.init(courseChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: ['篮球基础班', '体能训练课', '篮球提高班', '私教一对一', '足球入门班'] },
    series: [{
      name: '报名人数',
      type: 'bar',
      data: [120, 98, 85, 45, 38],
      itemStyle: { color: '#2196F3' }
    }]
  })
}

function initTrainingChart() {
  if (!trainingChartRef.value) return
  const chart = echarts.init(trainingChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['训练次数', '训练时长(小时)'] },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [
      { name: '训练次数', type: 'line', data: [120, 132, 101, 134, 90, 230, 210], itemStyle: { color: '#FF9800' } },
      { name: '训练时长(小时)', type: 'line', data: [20, 22, 18, 24, 15, 38, 35], itemStyle: { color: '#9C27B0' } }
    ]
  })
}

function initCoachChart() {
  if (!coachChartRef.value) return
  const chart = echarts.init(coachChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 45, name: '张教练', itemStyle: { color: '#4CAF50' } },
        { value: 35, name: '李教练', itemStyle: { color: '#2196F3' } },
        { value: 20, name: '王教练', itemStyle: { color: '#FF9800' } }
      ]
    }]
  })
}
</script>

<style scoped lang="scss">
.chart {
  height: 300px;
}
</style>
