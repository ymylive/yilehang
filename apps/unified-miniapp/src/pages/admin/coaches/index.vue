<template>
  <view class="admin-coaches">
    <view class="toolbar card">
      <input v-model="keyword" class="search-input" placeholder="搜索教练姓名/手机号/邮箱" @confirm="loadCoaches(true)" />
      <view class="toolbar-actions">
        <button class="btn ghost" @click="loadCoaches(true)">查询</button>
        <button class="btn primary" :loading="seeding" @click="seedMock">生成模拟教练</button>
      </view>
    </view>

    <view class="list" v-if="coaches.length">
      <view class="coach-card card" v-for="coach in coaches" :key="coach.id">
        <view class="head">
          <text class="name">{{ coach.name }}</text>
          <text class="meta">{{ coach.phone || '-' }}</text>
        </view>

        <view class="field">
          <text class="label">姓名</text>
          <input class="input" v-model="drafts[coach.id].name" />
        </view>
        <view class="field">
          <text class="label">专长（逗号分隔）</text>
          <input class="input" v-model="drafts[coach.id].specialtyText" />
        </view>
        <view class="inline-fields">
          <view class="field compact">
            <text class="label">课时费</text>
            <input class="input" type="digit" v-model="drafts[coach.id].hourlyRateText" />
          </view>
          <view class="field compact">
            <text class="label">教龄</text>
            <input class="input" type="number" v-model="drafts[coach.id].yearsText" />
          </view>
        </view>
        <view class="field">
          <text class="label">介绍</text>
          <textarea class="textarea" maxlength="200" v-model="drafts[coach.id].introduction" />
        </view>

        <button class="btn primary save" :loading="savingId === coach.id" @click="saveCoach(coach.id)">保存修改</button>
      </view>
    </view>

    <view class="empty card" v-else>
      <image :src="emptyIcon" class="empty-icon" mode="aspectFit" />
      <text>暂无教练数据</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { adminPanelApi } from '@/api'
import { getSemanticIcon } from '@/constants/semantic-icons'

interface CoachItem {
  id: number
  name: string
  phone?: string | null
  specialty: string[]
  introduction?: string | null
  hourly_rate?: number | null
  years_of_experience?: number | null
}

interface CoachDraft {
  name: string
  specialtyText: string
  introduction: string
  hourlyRateText: string
  yearsText: string
}

const keyword = ref('')
const coaches = ref<CoachItem[]>([])
const drafts = reactive<Record<number, CoachDraft>>({})
const savingId = ref(0)
const seeding = ref(false)
const emptyIcon = getSemanticIcon('admin-coaches-empty')

function setDraft(coach: CoachItem) {
  drafts[coach.id] = {
    name: coach.name || '',
    specialtyText: (coach.specialty || []).join(','),
    introduction: coach.introduction || '',
    hourlyRateText: coach.hourly_rate != null ? String(coach.hourly_rate) : '',
    yearsText: coach.years_of_experience != null ? String(coach.years_of_experience) : ''
  }
}

async function loadCoaches(resetPage = false) {
  try {
    const data: any = await adminPanelApi.listCoaches({
      keyword: keyword.value.trim() || undefined,
      page: resetPage ? 1 : 1,
      page_size: 50
    })
    coaches.value = (data?.items || []) as CoachItem[]
    coaches.value.forEach(setDraft)
  } catch (error: any) {
    uni.showToast({ title: error?.message || '加载教练失败', icon: 'none' })
  }
}

function parseSpecialty(text: string) {
  return text
    .split(',')
    .map(item => item.trim())
    .filter(Boolean)
}

async function saveCoach(coachId: number) {
  const draft = drafts[coachId]
  if (!draft) return
  if (!draft.name.trim()) {
    uni.showToast({ title: '姓名不能为空', icon: 'none' })
    return
  }

  savingId.value = coachId
  try {
    await adminPanelApi.updateCoach(coachId, {
      name: draft.name.trim(),
      specialty: parseSpecialty(draft.specialtyText),
      introduction: draft.introduction.trim() || undefined,
      hourly_rate: draft.hourlyRateText ? Number(draft.hourlyRateText) : undefined,
      years_of_experience: draft.yearsText ? Number(draft.yearsText) : undefined
    })
    uni.showToast({ title: '已保存', icon: 'success' })
    await loadCoaches()
  } catch (error: any) {
    uni.showToast({ title: error?.message || '保存失败', icon: 'none' })
  } finally {
    savingId.value = 0
  }
}

async function seedMock() {
  seeding.value = true
  try {
    const result: any = await adminPanelApi.seedMockCoaches(10)
    uni.showToast({ title: `新增${result?.created_count || 0}个`, icon: 'success' })
    await loadCoaches(true)
  } catch (error: any) {
    uni.showToast({ title: error?.message || '生成失败', icon: 'none' })
  } finally {
    seeding.value = false
  }
}

onShow(() => {
  loadCoaches(true)
})
</script>

<style scoped>
.admin-coaches {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 20rpx;
}

.card {
  border-radius: 18rpx;
  background: #fff;
  padding: 18rpx;
  box-shadow: 0 8rpx 18rpx rgba(31, 37, 51, 0.06);
}

.toolbar {
  margin-bottom: 14rpx;
}

.search-input {
  height: 72rpx;
  border-radius: 14rpx;
  background: #f4f6fb;
  padding: 0 18rpx;
  font-size: 24rpx;
}

.toolbar-actions {
  display: flex;
  gap: 10rpx;
  margin-top: 12rpx;
}

.btn {
  height: 68rpx;
  line-height: 68rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  border: none;
}

.btn::after {
  border: none;
}

.btn.primary {
  background: linear-gradient(135deg, #ffbd49, #ff9120);
  color: #fff;
  flex: 1;
}

.btn.ghost {
  background: #eef2f8;
  color: #516079;
  width: 160rpx;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.name {
  font-size: 29rpx;
  font-weight: 700;
  color: #1f2533;
}

.meta {
  font-size: 22rpx;
  color: #8993a8;
}

.field {
  margin-top: 10rpx;
}

.label {
  display: block;
  font-size: 22rpx;
  color: #667189;
  margin-bottom: 6rpx;
}

.input,
.textarea {
  width: 100%;
  border-radius: 12rpx;
  background: #f6f8fc;
  padding: 0 14rpx;
  font-size: 24rpx;
}

.input {
  height: 68rpx;
  line-height: 68rpx;
}

.textarea {
  min-height: 120rpx;
  padding-top: 12rpx;
  box-sizing: border-box;
}

.inline-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10rpx;
}

.save {
  margin-top: 14rpx;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: #90a0ba;
  padding: 28rpx;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 8rpx;
}
</style>
