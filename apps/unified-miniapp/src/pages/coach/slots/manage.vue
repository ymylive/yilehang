<template>
  <view class="slots-page">
    <!-- 说明 -->
    <view class="tips-card">
      <view class="tips-icon">
        <wd-icon name="tips" size="30rpx" color="#1976d2" />
      </view>
      <text class="tips-text">设置您每周的可约时段，学员将在这些时段内预约您的课程</text>
    </view>

    <!-- 时段列表 -->
    <view class="slots-list">
      <view v-for="day in weekDays" :key="day.value" class="day-section">
        <view class="day-header">
          <text class="day-name">{{ day.label }}</text>
          <view class="add-btn" @click="addSlot(day.value)">+ 添加时段</view>
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
              <text class="action-btn edit" @click="editSlot(slot)">编辑</text>
              <text class="action-btn delete" @click="deleteSlotConfirm(slot.id)">删除</text>
            </view>
          </view>
        </view>

        <view v-else class="no-slots">
          <text>暂未设置时段</text>
        </view>
      </view>
    </view>

    <!-- 添加/编辑弹窗 -->
    <view v-if="showPopup" class="popup-mask" @click="showPopup = false">
      <view class="popup-content" @click.stop>
        <view class="popup-title">{{ editingSlot ? '编辑时段' : '添加时段' }}</view>

        <view class="form-item">
          <text class="form-label">开始时间</text>
          <picker mode="time" :value="formData.startTime" @change="onStartTimeChange">
            <view class="picker-value">{{ formData.startTime }}</view>
          </picker>
        </view>

        <view class="form-item">
          <text class="form-label">结束时间</text>
          <picker mode="time" :value="formData.endTime" @change="onEndTimeChange">
            <view class="picker-value">{{ formData.endTime }}</view>
          </picker>
        </view>

        <view class="form-item">
          <text class="form-label">每节时长（分钟）</text>
          <input
            class="form-input"
            type="number"
            v-model="formData.duration"
            placeholder="60"
          />
        </view>

        <view class="form-item">
          <text class="form-label">最大学员数</text>
          <input
            class="form-input"
            type="number"
            v-model="formData.maxStudents"
            placeholder="1"
          />
        </view>

        <view class="popup-buttons">
          <button class="btn cancel" @click="showPopup = false">取消</button>
          <button class="btn confirm" @click="saveSlot" :loading="saving">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { coachSlotsApi } from '@/api/index'

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
const saving = ref(false)
const loading = ref(false)

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

function onStartTimeChange(e: any) {
  formData.value.startTime = e.detail.value
}

function onEndTimeChange(e: any) {
  formData.value.endTime = e.detail.value
}

async function loadSlots() {
  loading.value = true
  try {
    const data = await coachSlotsApi.getSlots()
    slots.value = data || []
  } catch (error: any) {
    console.error('获取时段失败:', error)
    uni.showToast({ title: error.message || '获取时段失败', icon: 'none' })
  } finally {
    loading.value = false
  }
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

async function saveSlot() {
  if (saving.value) return

  // 验证
  if (!formData.value.startTime || !formData.value.endTime) {
    uni.showToast({ title: '请选择时间', icon: 'none' })
    return
  }

  if (formData.value.startTime >= formData.value.endTime) {
    uni.showToast({ title: '结束时间必须大于开始时间', icon: 'none' })
    return
  }

  saving.value = true
  try {
    const slotData = {
      day_of_week: currentDay.value,
      start_time: formData.value.startTime + ':00',
      end_time: formData.value.endTime + ':00',
      slot_duration: parseInt(formData.value.duration) || 60,
      max_students: parseInt(formData.value.maxStudents) || 1
    }

    if (editingSlot.value) {
      await coachSlotsApi.updateSlot(editingSlot.value.id, slotData)
    } else {
      await coachSlotsApi.createSlot(slotData)
    }

    showPopup.value = false
    uni.showToast({ title: '保存成功', icon: 'success' })
    await loadSlots()
  } catch (error: any) {
    console.error('保存失败:', error)
    uni.showToast({ title: error.message || '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}

function deleteSlotConfirm(id: number) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个时段吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await coachSlotsApi.deleteSlot(id)
          uni.showToast({ title: '删除成功', icon: 'success' })
          await loadSlots()
        } catch (error: any) {
          uni.showToast({ title: error.message || '删除失败', icon: 'none' })
        }
      }
    }
  })
}

onMounted(() => {
  loadSlots()
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
    width: 56rpx;
    height: 56rpx;
    border-radius: 16rpx;
    background: #eaf4ff;
    display: flex;
    align-items: center;
    justify-content: center;
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

    .add-btn {
      font-size: 26rpx;
      color: #2196F3;
      padding: 8rpx 20rpx;
      border: 1rpx solid #2196F3;
      border-radius: 20rpx;
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
      gap: 20rpx;

      .action-btn {
        font-size: 26rpx;
        padding: 8rpx 16rpx;

        &.edit {
          color: #2196F3;
        }

        &.delete {
          color: #f44336;
        }
      }
    }
  }
}

.no-slots {
  text-align: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;
}

.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 999;
}

.popup-content {
  width: 100%;
  background-color: #fff;
  border-radius: 24rpx 24rpx 0 0;
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

    .picker-value {
      padding: 20rpx;
      background-color: #f5f5f5;
      border-radius: 12rpx;
      font-size: 30rpx;
      color: #333;
    }

    .form-input {
      padding: 20rpx;
      background-color: #f5f5f5;
      border-radius: 12rpx;
      font-size: 30rpx;
    }
  }

  .popup-buttons {
    display: flex;
    gap: 20rpx;
    margin-top: 40rpx;

    .btn {
      flex: 1;
      height: 88rpx;
      line-height: 88rpx;
      border-radius: 44rpx;
      font-size: 32rpx;

      &.cancel {
        background-color: #f5f5f5;
        color: #666;
      }

      &.confirm {
        background-color: #2196F3;
        color: #fff;
      }
    }
  }
}
</style>
