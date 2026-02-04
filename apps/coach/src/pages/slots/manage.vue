<template>
  <view class="slots-page">
    <!-- 说明 -->
    <view class="tips-card">
      <text class="tips-icon">💡</text>
      <text class="tips-text">设置您每周的可约时段，学员将在这些时段内预约您的课程</text>
    </view>

    <!-- 时段列表 -->
    <view class="slots-list">
      <view v-for="day in weekDays" :key="day.value" class="day-section">
        <view class="day-header">
          <text class="day-name">{{ day.label }}</text>
          <wd-button size="small" plain @click="addSlot(day.value)">+ 添加时段</wd-button>
        </view>

        <view v-if="getSlotsByDay(day.value).length > 0" class="slot-items">
          <view
            v-for="slot in getSlotsByDay(day.value)"
            :key="slot.id"
            class="slot-item"
          >
            <view class="slot-time">
              {{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}
            </view>
            <view class="slot-info">
              <text>{{ slot.slot_duration }}分钟/节</text>
              <text>最多{{ slot.max_students }}人</text>
            </view>
            <view class="slot-actions">
              <wd-button size="small" plain @click="editSlot(slot)">编辑</wd-button>
              <wd-button size="small" plain type="error" @click="deleteSlot(slot.id)">删除</wd-button>
            </view>
          </view>
        </view>

        <view v-else class="no-slots">
          <text>暂未设置时段</text>
        </view>
      </view>
    </view>

    <!-- 添加/编辑弹窗 -->
    <wd-popup v-model="showPopup" position="bottom" round>
      <view class="popup-content">
        <view class="popup-title">{{ editingSlot ? '编辑时段' : '添加时段' }}</view>

        <view class="form-item">
          <text class="form-label">开始时间</text>
          <wd-datetime-picker
            v-model="formData.startTime"
            type="time"
            label=""
          />
        </view>

        <view class="form-item">
          <text class="form-label">结束时间</text>
          <wd-datetime-picker
            v-model="formData.endTime"
            type="time"
            label=""
          />
        </view>

        <view class="form-item">
          <text class="form-label">每节时长（分钟）</text>
          <wd-input v-model="formData.duration" type="number" placeholder="60" />
        </view>

        <view class="form-item">
          <text class="form-label">最大学员数</text>
          <wd-input v-model="formData.maxStudents" type="number" placeholder="1" />
        </view>

        <view class="popup-buttons">
          <wd-button plain @click="showPopup = false">取消</wd-button>
          <wd-button type="primary" @click="saveSlot">保存</wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Slot {
  id: number
  day_of_week: number
  start_time: string
  end_time: string
  slot_duration: number
  max_students: number
  is_active: boolean
}

const weekDays = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 0 }
]

const slots = ref<Slot[]>([])
const showPopup = ref(false)
const editingSlot = ref<Slot | null>(null)
const currentDay = ref(0)

const formData = ref({
  startTime: '09:00',
  endTime: '10:00',
  duration: '60',
  maxStudents: '1'
})

function getSlotsByDay(day: number): Slot[] {
  return slots.value.filter(s => s.day_of_week === day)
}

function formatTime(timeStr: string): string {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}

function addSlot(day: number) {
  currentDay.value = day
  editingSlot.value = null
  formData.value = {
    startTime: '09:00',
    endTime: '10:00',
    duration: '60',
    maxStudents: '1'
  }
  showPopup.value = true
}

function editSlot(slot: Slot) {
  currentDay.value = slot.day_of_week
  editingSlot.value = slot
  formData.value = {
    startTime: slot.start_time.substring(0, 5),
    endTime: slot.end_time.substring(0, 5),
    duration: String(slot.slot_duration),
    maxStudents: String(slot.max_students)
  }
  showPopup.value = true
}

function saveSlot() {
  // TODO: 调用API保存
  const newSlot: Slot = {
    id: editingSlot.value?.id || Date.now(),
    day_of_week: currentDay.value,
    start_time: formData.value.startTime + ':00',
    end_time: formData.value.endTime + ':00',
    slot_duration: parseInt(formData.value.duration) || 60,
    max_students: parseInt(formData.value.maxStudents) || 1,
    is_active: true
  }

  if (editingSlot.value) {
    const index = slots.value.findIndex(s => s.id === editingSlot.value!.id)
    if (index > -1) {
      slots.value[index] = newSlot
    }
  } else {
    slots.value.push(newSlot)
  }

  showPopup.value = false
  uni.showToast({ title: '保存成功', icon: 'success' })
}

function deleteSlot(id: number) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个时段吗？',
    success: (res) => {
      if (res.confirm) {
        slots.value = slots.value.filter(s => s.id !== id)
        uni.showToast({ title: '删除成功', icon: 'success' })
      }
    }
  })
}

onMounted(() => {
  // 模拟数据
  slots.value = [
    { id: 1, day_of_week: 1, start_time: '09:00:00', end_time: '12:00:00', slot_duration: 60, max_students: 1, is_active: true },
    { id: 2, day_of_week: 1, start_time: '14:00:00', end_time: '18:00:00', slot_duration: 60, max_students: 1, is_active: true },
    { id: 3, day_of_week: 3, start_time: '09:00:00', end_time: '12:00:00', slot_duration: 60, max_students: 1, is_active: true },
    { id: 4, day_of_week: 5, start_time: '14:00:00', end_time: '18:00:00', slot_duration: 60, max_students: 1, is_active: true }
  ]
})
</script>

<style lang="scss" scoped>
.slots-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 40rpx;
}

.tips-card {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  background-color: #e3f2fd;
  margin: 20rpx;
  border-radius: 12rpx;

  .tips-icon {
    font-size: 32rpx;
    margin-right: 16rpx;
  }

  .tips-text {
    font-size: 26rpx;
    color: #1976d2;
    flex: 1;
  }
}

.slots-list {
  padding: 0 20rpx;
}

.day-section {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;

  .day-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;

    .day-name {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
    }
  }
}

.slot-items {
  .slot-item {
    display: flex;
    align-items: center;
    padding: 20rpx;
    background-color: #f9f9f9;
    border-radius: 12rpx;
    margin-bottom: 16rpx;

    &:last-child {
      margin-bottom: 0;
    }

    .slot-time {
      font-size: 30rpx;
      font-weight: 500;
      color: #333;
      width: 200rpx;
    }

    .slot-info {
      flex: 1;
      display: flex;
      gap: 20rpx;
      font-size: 24rpx;
      color: #999;
    }

    .slot-actions {
      display: flex;
      gap: 12rpx;
    }
  }
}

.no-slots {
  text-align: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;
}

.popup-content {
  padding: 40rpx;

  .popup-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
    text-align: center;
    margin-bottom: 40rpx;
  }

  .form-item {
    margin-bottom: 30rpx;

    .form-label {
      display: block;
      font-size: 28rpx;
      color: #666;
      margin-bottom: 12rpx;
    }
  }

  .popup-buttons {
    display: flex;
    gap: 20rpx;
    margin-top: 40rpx;

    :deep(.wd-button) {
      flex: 1;
    }
  }
}
</style>
