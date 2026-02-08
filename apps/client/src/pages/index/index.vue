<template>
  <view class="page">
    <view v-if="!userStore.isLoggedIn" class="marketing">
      <view class="hero hero-fullscreen">
        <view class="hero-bg">
          <view class="hero-orb orb-1"></view>
          <view class="hero-orb orb-2"></view>
          <view class="hero-orb orb-3"></view>
          <view class="hero-orb orb-4"></view>
          <view class="hero-grid"></view>
        </view>
        <view class="hero-content hero-content-center">
          <view class="brand-logo">
            <view class="logo-icon">易</view>
            <view class="logo-text">
              <text class="logo-name">易乐航 ITS</text>
              <text class="logo-slogan">社区青少年韧性成长中心</text>
            </view>
          </view>
          <text class="hero-title hero-title-large">重新定义放学两小时</text>
          <text class="hero-subtitle hero-subtitle-center">不是"看娃托管" · 而是"大脑激活码"</text>
          <view class="hero-features">
            <view class="feature-item">
              <text class="feature-icon">⚡</text>
              <view class="feature-text">
                <text class="feature-title">运动激活</text>
                <text class="feature-desc">多巴胺提升专注</text>
              </view>
            </view>
            <view class="feature-item">
              <text class="feature-icon">📈</text>
              <view class="feature-text">
                <text class="feature-title">可见进步</text>
                <text class="feature-desc">成长肉眼可见</text>
              </view>
            </view>
            <view class="feature-item">
              <text class="feature-icon">🎁</text>
              <view class="feature-text">
                <text class="feature-title">能量激励</text>
                <text class="feature-desc">汗水兑换奖励</text>
              </view>
            </view>
          </view>
          <view class="hero-actions hero-actions-center">
            <button class="cta primary cta-large" @click="goToLogin">开启韧性成长之旅</button>
          </view>
          <view class="hero-stats">
            <view class="stat-item">
              <text class="stat-value">98%</text>
              <text class="stat-label">满意度</text>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-item">
              <text class="stat-value">12K+</text>
              <text class="stat-label">累计上课</text>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-item">
              <text class="stat-value">50+</text>
              <text class="stat-label">明星教练</text>
            </view>
          </view>
        </view>
        <view class="hero-bottom">
          <view class="hero-bottom-actions">
            <text class="hero-link" @click="openTrial">免费体验课</text>
            <text class="hero-divider">|</text>
            <text class="hero-link" @click="handleConsult">联系客服</text>
          </view>
          <view class="scroll-hint" @click="scrollToContent">
            <text class="scroll-text">了解更多</text>
            <text class="scroll-arrow">↓</text>
          </view>
        </view>
      </view>

      <view class="marketing-section">
        <view class="section-header marketing">
          <text class="section-title">环境与场馆</text>
          <text class="section-subtitle">安全、干净、明亮，孩子运动更专注</text>
        </view>
        <view class="card-row">
          <view
            v-for="(item, index) in envCards"
            :key="item.title"
            class="media-card"
            :style="{ animationDelay: `${index * 0.08}s` }"
          >
            <view class="media-photo" :class="item.tone"></view>
            <text class="media-title">{{ item.title }}</text>
            <text class="media-desc">{{ item.desc }}</text>
          </view>
        </view>
      </view>

      <view class="marketing-section">
        <view class="section-header marketing">
          <text class="section-title">精品课程</text>
          <text class="section-subtitle">次卡 / 月卡 / 私教 / 套餐，覆盖多场景</text>
        </view>
        <view class="course-grid">
          <view
            v-for="(item, index) in courseCards"
            :key="item.title"
            class="course-card"
            :style="{ animationDelay: `${index * 0.06}s` }"
          >
            <view class="course-icon">{{ item.icon }}</view>
            <view class="course-info">
              <text class="course-title">{{ item.title }}</text>
              <text class="course-desc">{{ item.desc }}</text>
            </view>
            <text class="course-tag">{{ item.tag }}</text>
          </view>
        </view>
      </view>

      <view class="marketing-section">
        <view class="section-header marketing">
          <text class="section-title">教练团队</text>
          <text class="section-subtitle">多项目认证，平均 5 年以上教学经验</text>
        </view>
        <view class="coach-row">
          <view
            v-for="(coach, index) in coachCards"
            :key="coach.name"
            class="coach-card"
            :style="{ animationDelay: `${index * 0.08}s` }"
          >
            <view class="coach-avatar" :class="coach.tone">{{ coach.initial }}</view>
            <view class="coach-info">
              <text class="coach-name">{{ coach.name }}</text>
              <text class="coach-desc">{{ coach.desc }}</text>
              <view class="coach-meta">
                <text>评分 {{ coach.rating }}</text>
                <text>{{ coach.years }} 年经验</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="marketing-section">
        <view class="section-header marketing">
          <text class="section-title">价格方案</text>
          <text class="section-subtitle">灵活计费，支持发票与续费提醒</text>
        </view>
        <view class="price-grid">
          <view
            v-for="(plan, index) in priceCards"
            :key="plan.title"
            class="price-card"
            :class="{ hot: plan.hot }"
            :style="{ animationDelay: `${index * 0.08}s` }"
          >
            <text class="price-title">{{ plan.title }}</text>
            <text class="price-value">{{ plan.price }}</text>
            <text class="price-desc">{{ plan.desc }}</text>
            <view class="price-tags">
              <text v-for="tag in plan.tags" :key="tag" class="price-tag">{{ tag }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="marketing-section">
        <view class="section-header marketing">
          <text class="section-title">学员口碑</text>
          <text class="section-subtitle">真实家长反馈，复购率持续上升</text>
        </view>
        <view class="review-grid">
          <view
            v-for="(review, index) in visibleReviewCards"
            :key="review.name"
            class="review-card"
            :style="{ animationDelay: `${index * 0.06}s` }"
          >
            <text class="review-text">{{ review.text }}</text>
            <view class="review-footer">
              <text class="review-name">{{ review.name }}</text>
              <text class="review-score">评分 {{ review.score }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="marketing-section strategy-section">
        <view class="section-header marketing">
          <text class="section-title">1-2-3-4 实战架构</text>
          <text class="section-subtitle">不是低端托管，而是社区青少年韧性成长中心</text>
        </view>

        <view class="position-card">
          <view class="position-badge">1 个核心定位</view>
          <text class="position-title">不只是“看娃”，更是“大脑激活码”</text>
          <text class="position-desc">通过“体育 + 辅导”管理效率，让孩子更爱动、更会学，家长看得见进步。</text>
        </view>

        <view class="strategy-grid two-col">
          <view class="strategy-card" v-for="item in costStrategies" :key="item.title">
            <text class="strategy-k">{{ item.no }}</text>
            <text class="strategy-title">{{ item.title }}</text>
            <text class="strategy-desc">{{ item.desc }}</text>
            <text class="strategy-win">{{ item.win }}</text>
          </view>
        </view>

        <view class="strategy-grid three-col">
          <view class="strategy-card" v-for="item in visibleProfitLoops" :key="item.title">
            <text class="strategy-k">{{ item.no }}</text>
            <text class="strategy-title">{{ item.title }}</text>
            <text class="strategy-desc">{{ item.desc }}</text>
          </view>
        </view>

        <view class="strategy-grid two-col">
          <view class="strategy-card" v-for="item in visibleEventPackaging" :key="item.title">
            <text class="strategy-k">{{ item.no }}</text>
            <text class="strategy-title">{{ item.title }}</text>
            <text class="strategy-desc">{{ item.desc }}</text>
          </view>
        </view>

        <view class="strategy-toggle-wrap">
          <text class="strategy-toggle" @click="toggleStrategyDetail">
            {{ showStrategyDetail ? '收起架构详情' : '展开完整架构' }}
          </text>
        </view>
      </view>

      <view class="marketing-section foot-cta">
        <view class="foot-card">
          <view class="foot-head">
            <text class="foot-kicker">免费体验课</text>
            <text class="foot-title">准备好开始了吗？</text>
          </view>
          <text class="foot-subtitle">一键预约，专属教练为孩子规划课程。</text>
          <view class="foot-actions">
            <button class="cta primary" @click="handleBooking">立即预约</button>
            <button class="cta ghost" @click="openTrial">先领体验课</button>
          </view>
        </view>
      </view>

      <view class="trial-modal" v-if="trialVisible">
        <view class="trial-card">
          <view class="trial-header">
            <text>免费体验课报名</text>
            <text class="trial-close" @click="trialVisible = false">×</text>
          </view>
          <view class="trial-form">
            <input class="trial-input" v-model="trialForm.name" placeholder="孩子姓名" />
            <input class="trial-input" v-model="trialForm.phone" placeholder="家长手机号" />
            <input class="trial-input" v-model="trialForm.age" placeholder="孩子年龄" />
          </view>
          <button class="cta primary trial-submit" @click="submitTrial">提交报名</button>
        </view>
      </view>
    </view>

    <view v-else-if="isParentOrStudent" class="dashboard">
      <!-- 顶部区域 -->
      <view class="header-section">
        <!-- 背景装饰 -->
        <view class="header-bg">
          <view class="bg-shape shape1"></view>
          <view class="bg-shape shape2"></view>
          <view class="bg-shape shape3"></view>
        </view>

        <!-- 用户信息栏 -->
        <view class="user-bar">
          <view class="user-info" @click="goToUser">
            <view class="avatar-wrap">
              <image class="avatar" :src="userStore.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
              <view class="avatar-badge">VIP</view>
            </view>
            <view class="user-text">
              <text class="greeting">{{ getGreeting() }}</text>
              <text class="user-name">{{ currentStudentName }}</text>
            </view>
          </view>
          <view class="header-actions">
            <view class="action-btn" @click="scanQRCode">
              <text class="action-icon">📷</text>
            </view>
          </view>
        </view>

        <!-- 课时卡片 -->
        <view class="lesson-card">
          <view class="lesson-info">
            <view class="lesson-icon">⏱</view>
            <view class="lesson-text">
              <text class="lesson-label">剩余课时</text>
              <text class="lesson-count">{{ userStore.currentStudent?.remaining_lessons || 0 }}</text>
            </view>
          </view>
          <view class="lesson-action" @click="goTo('/pages/membership/index')">
            <text>充值</text>
            <text class="arrow">→</text>
          </view>
        </view>
      </view>

      <!-- 功能入口 -->
      <view class="feature-section">
        <view class="feature-grid">
          <view class="feature-card" @click="goTo('/pages/growth/index')">
            <view class="feature-icon-wrap growth">
              <text class="feature-icon">📈</text>
            </view>
            <text class="feature-name">成长档案</text>
            <text class="feature-desc">查看运动数据</text>
          </view>

          <view class="feature-card" @click="goTo('/pages/training/index')">
            <view class="feature-icon-wrap training">
              <text class="feature-icon">🤖</text>
            </view>
            <text class="feature-name">AI陪练</text>
            <text class="feature-desc">智能运动指导</text>
          </view>

          <view class="feature-card" @click="goTo('/pages/moments/index')">
            <view class="feature-icon-wrap moments">
              <text class="feature-icon">✨</text>
            </view>
            <text class="feature-name">精彩瞬间</text>
            <text class="feature-desc">记录成长时刻</text>
          </view>

          <view class="feature-card" @click="goTo('/pages/booking/index')">
            <view class="feature-icon-wrap orders">
              <text class="feature-icon">🧾</text>
            </view>
            <text class="feature-name">我的订单</text>
            <text class="feature-desc">预约与消费</text>
          </view>
        </view>
      </view>

      <!-- 今日课程 -->
      <view class="section">
        <view class="section-header">
          <view class="section-title">
            <text class="title-icon">📅</text>
            <text class="title-text">今日课程</text>
          </view>
          <view class="section-more" @click="goTo('/pages/schedule/index')">
            <text>全部</text>
            <text class="more-arrow">→</text>
          </view>
        </view>

        <view class="course-list" v-if="todayCourses.length">
          <view class="course-item" v-for="course in todayCourses" :key="course.id">
            <view class="course-time-block">
              <text class="course-time">{{ formatTime(course.start_time) }}</text>
              <text class="course-duration">{{ course.duration }}分钟</text>
            </view>
            <view class="course-divider"></view>
            <view class="course-detail">
              <text class="course-name">{{ course.name }}</text>
              <view class="course-meta">
                <text class="coach-name">教练：{{ course.coach_name }}</text>
              </view>
            </view>
            <view :class="['course-status', course.status]">
              <text>{{ getStatusText(course.status) }}</text>
            </view>
          </view>
        </view>

        <view class="empty-state" v-else>
          <view class="empty-icon">📅</view>
          <text class="empty-text">今日暂无课程</text>
          <text class="empty-hint">去预约一节课吧</text>
        </view>
      </view>

      <!-- 本周统计 -->
      <view class="section stats-section">
        <view class="section-header">
          <view class="section-title">
            <text class="title-icon">🏃</text>
            <text class="title-text">本周运动</text>
          </view>
        </view>

        <view class="stats-grid">
          <view class="stat-card">
            <view class="stat-icon-wrap sessions">
              <text class="stat-icon">🎯</text>
            </view>
            <view class="stat-content">
              <text class="stat-value">{{ weekStats.sessions }}</text>
              <text class="stat-label">训练次数</text>
            </view>
          </view>

          <view class="stat-card">
            <view class="stat-icon-wrap duration">
              <text class="stat-icon">⏳</text>
            </view>
            <view class="stat-content">
              <text class="stat-value">{{ weekStats.duration }}</text>
              <text class="stat-label">训练时长(分钟)</text>
            </view>
          </view>

          <view class="stat-card">
            <view class="stat-icon-wrap calories">
              <text class="stat-icon">🔥</text>
            </view>
            <view class="stat-content">
              <text class="stat-value">{{ weekStats.calories }}</text>
              <text class="stat-label">消耗卡路里</text>
            </view>
          </view>
        </view>

        <!-- 鼓励语 -->
        <view class="encourage-banner" v-if="weekStats.sessions > 0">
          <text class="encourage-icon">🎉</text>
          <text class="encourage-text">{{ getEncourageText() }}</text>
        </view>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </view>

    <view v-else-if="isCoach" class="role-dashboard coach">
      <view class="role-hero">
        <text class="role-title">教练工作空间</text>
        <text class="role-subtitle">查看我的学员、课表与收入统计</text>
      </view>
      <view class="role-grid">
        <view class="role-card tap-active" @click="goTo('/pages/coach/workbench/index')">
          <text class="role-icon">📋</text>
          <text class="role-name">工作台</text>
          <text class="role-desc">今日安排与待办</text>
        </view>
        <view class="role-card tap-active" @click="goTo('/pages/coach/schedule/index')">
          <text class="role-icon">📅</text>
          <text class="role-name">我的课表</text>
          <text class="role-desc">查看并处理约课</text>
        </view>
        <view class="role-card tap-active" @click="goTo('/pages/coach/students/index')">
          <text class="role-icon">👥</text>
          <text class="role-name">我的学员</text>
          <text class="role-desc">跟进训练进度</text>
        </view>
        <view class="role-card tap-active" @click="goTo('/pages/coach/income/index')">
          <text class="role-icon">💰</text>
          <text class="role-name">收入统计</text>
          <text class="role-desc">查看课时收益</text>
        </view>
      </view>
    </view>

    <view v-else-if="isMerchant" class="role-dashboard merchant">
      <view class="role-hero">
        <text class="role-title">商户工作空间</text>
        <text class="role-subtitle">核销订单、查看统计与经营数据</text>
      </view>
      <view class="role-grid">
        <view class="role-card tap-active" @click="goTo('/pages/merchant/index')">
          <text class="role-icon">🏪</text>
          <text class="role-name">商家工作台</text>
          <text class="role-desc">今日核销与看板</text>
        </view>
        <view class="role-card tap-active" @click="goTo('/pages/merchant/verify')">
          <text class="role-icon">📷</text>
          <text class="role-name">扫码核销</text>
          <text class="role-desc">快速处理兑换订单</text>
        </view>
        <view class="role-card tap-active" @click="goTo('/pages/merchant/orders')">
          <text class="role-icon">📦</text>
          <text class="role-name">订单管理</text>
          <text class="role-desc">待核销与历史订单</text>
        </view>
        <view class="role-card tap-active" @click="goTo('/pages/merchant/stats')">
          <text class="role-icon">📊</text>
          <text class="role-name">数据统计</text>
          <text class="role-desc">趋势与经营分析</text>
        </view>
      </view>
    </view>

    <view v-else class="role-dashboard fallback">
      <view class="role-hero">
        <text class="role-title">欢迎使用易乐航</text>
        <text class="role-subtitle">请先登录或切换账号后继续</text>
      </view>
      <button class="cta primary" @click="goTo('/pages/user/login')">去登录</button>
    </view>
  </view>
</template>


<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { scheduleApi, trainingApi } from '@/api'
import { trackEvent } from '@/utils/track'

const userStore = useUserStore()

const isParentOrStudent = computed(() => userStore.isParent || userStore.isStudent)
const isCoach = computed(() => userStore.user?.role === 'coach')
const isMerchant = computed(() => userStore.user?.role === 'merchant')

const currentStudentName = computed(() => {
  return userStore.currentStudent?.name || userStore.user?.nickname || '小朋友'
})

const todayCourses = ref<any[]>([])
const showStrategyDetail = ref(false)

const weekStats = ref({
  sessions: 0,
  duration: 0,
  calories: 0
})

const trialVisible = ref(false)
const trialForm = ref({
  name: '',
  phone: '',
  age: ''
})

const contactPhone = '400-888-1234'

const envCards = [
  { title: '阳光场馆', desc: '自然采光与安全软装，呵护每一步', tone: 'sun' },
  { title: '智能设备', desc: '科学训练器械与监测系统', tone: 'tech' },
  { title: '亲子空间', desc: '家长休息区与观摩区', tone: 'warm' }
]

const courseCards = [
  { title: '篮球基础班', desc: '动作规范 + 体能提升', icon: '篮', tag: '适合7-12岁' },
  { title: '体能提升课', desc: '核心力量与协调', icon: '能', tag: '全能训练' },
  { title: '专项私教', desc: '一对一深度训练', icon: '专', tag: '成长加速' },
  { title: '运动素养课', desc: '体态习惯养成', icon: '姿', tag: '稳扎稳打' }
]

const coachCards = [
  { name: '王教练', desc: '篮球国家二级 · 体能训练', rating: '4.9', years: 6, initial: '王', tone: 'tone-a' },
  { name: '陈教练', desc: '体适能认证 · 动作纠正', rating: '4.8', years: 5, initial: '陈', tone: 'tone-b' },
  { name: '李教练', desc: '青少年专项 · 课程设计', rating: '4.9', years: 7, initial: '李', tone: 'tone-c' }
]

const priceCards = [
  { title: '次卡体验', price: '¥199', desc: '2次体验课', tags: ['灵活排课', '随约随上'], hot: false },
  { title: '月卡成长', price: '¥899', desc: '12次小班课', tags: ['课时提醒', '可转赠'], hot: true },
  { title: '私教计划', price: '¥1999', desc: '8次私教课', tags: ['专属教练', '成长报告'], hot: false }
]

const reviewCards = [
  { name: '周妈妈', score: '4.9', text: '孩子上课积极，教练反馈细致，课程安排很灵活。' },
  { name: '林爸爸', score: '5.0', text: '体能提升明显，课程体系化，孩子更自信了。' },
  { name: '晓雨妈妈', score: '4.8', text: '约课方便，提醒及时，整体体验很舒服。' }
]

const visibleReviewCards = computed(() => {
  return showStrategyDetail.value ? reviewCards : reviewCards.slice(0, 2)
})

const costStrategies = [
  {
    no: 2,
    title: '分布式社区厨房',
    desc: '与口碑餐馆轮换供餐，透明可查，家长可实地感知。',
    win: '风险外包 + 成本更稳 + 口味更优'
  },
  {
    no: 3,
    title: '“1+N”人才矩阵',
    desc: '1位专业教练定SOP，N位大学生领队做陪伴与执行。',
    win: '专业保障 + 榜样陪伴 + 轻资产扩张'
  }
]

const profitLoops = [
  {
    no: 4,
    title: '保分/进步奖学金',
    desc: '围绕体测达标与进步返现，家长购买的是确定性。'
  },
  {
    no: 5,
    title: '能量支票体系',
    desc: '运动积分可兑换合作商家权益，激发孩子自驱。'
  },
  {
    no: 6,
    title: '高毛利增值服务',
    desc: '报告、装备、营地形成结构化增收，强化复购。'
  }
]

const visibleProfitLoops = computed(() => {
  return showStrategyDetail.value ? profitLoops : profitLoops.slice(0, 2)
})

const eventPackaging = [
  {
    no: 7,
    title: '1+1 暖苗计划',
    desc: '城市孩子运动成长，同时联动公益捐赠，价值可感。'
  },
  {
    no: 8,
    title: '真实数据闭环',
    desc: '一物一码、照片回执、链路可追溯，杜绝伪公益质疑。'
  },
  {
    no: 9,
    title: '合规化运营',
    desc: '劳务协议、食品留样、意外险公示，风控前置。'
  },
  {
    no: 10,
    title: '数字化资产',
    desc: '英雄榜 + 成长曲线，家长看到“肉眼可见的进步”。'
  }
]

const visibleEventPackaging = computed(() => {
  return showStrategyDetail.value ? eventPackaging : eventPackaging.slice(0, 2)
})

function toggleStrategyDetail() {
  showStrategyDetail.value = !showStrategyDetail.value
}

function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
}

function getEncourageText() {
  const sessions = weekStats.value.sessions
  if (sessions >= 5) return '太棒了！本周运动达人就是你！'
  if (sessions >= 3) return '继续保持，你做得很好！'
  if (sessions >= 1) return '好的开始，继续加油！'
  return '开始你的运动之旅吧！'
}

onMounted(async () => {
  trackEvent('home_view', { loggedIn: userStore.isLoggedIn })
  if (userStore.isLoggedIn) {
    await loadTodayCourses()
    await loadWeekStats()
  }
})

async function loadTodayCourses() {
  try {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    const res = await scheduleApi.list({
      start_date: today.toISOString(),
      end_date: tomorrow.toISOString()
    })
    todayCourses.value = res || []
  } catch (error) {
    console.error('加载课程失败', error)
  }
}

async function loadWeekStats() {
  if (!userStore.currentStudent) return

  try {
    const history = await trainingApi.getHistory(userStore.currentStudent.id, 0, 100)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)

    const weekData = (history || []).filter((item: any) =>
      new Date(item.created_at) >= weekAgo
    )

    weekStats.value = {
      sessions: weekData.length,
      duration: Math.round(weekData.reduce((sum: number, item: any) => sum + item.duration, 0) / 60),
      calories: Math.round(weekData.reduce((sum: number, item: any) => sum + (item.calories_burned || 0), 0))
    }
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    scheduled: '待上课',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

function goTo(url: string) {
  uni.navigateTo({ url })
}

function handleBooking() {
  trackEvent('cta_booking_click', { source: userStore.isLoggedIn ? 'dashboard' : 'marketing' })
  if (!userStore.checkLogin()) return
  goTo('/pages/booking/index')
}

function openTrial() {
  trackEvent('trial_open')
  trialVisible.value = true
}

function submitTrial() {
  if (!trialForm.value.name || !trialForm.value.phone) {
    uni.showToast({ title: '请填写姓名和手机号', icon: 'none' })
    return
  }
  trackEvent('trial_submit', { ...trialForm.value })
  uni.showToast({ title: '报名成功，我们会尽快联系', icon: 'none' })
  trialVisible.value = false
  trialForm.value = { name: '', phone: '', age: '' }
}

function handleConsult() {
  trackEvent('consult_click')
  if (contactPhone && typeof uni.makePhoneCall === 'function') {
    uni.makePhoneCall({ phoneNumber: contactPhone })
    return
  }
  uni.showToast({ title: '请稍后再试', icon: 'none' })
}

function goToLogin() {
  uni.navigateTo({ url: '/pages/user/login' })
}

function scrollToContent() {
  uni.pageScrollTo({ scrollTop: 800, duration: 300 })
}

function goToUser() {
  uni.switchTab({ url: '/pages/user/index' })
}

function scanQRCode() {
  uni.scanCode({
    success: (res) => {
      console.log('扫码结果', res)
    }
  })
}
</script>

<style scoped>
/* 设计变量 */
page {
  --c-primary: #FF8800;
  --c-secondary: #FFB347;
  --c-accent: #4FA4F3;
  --c-bg-body: #FFFBF5;
  --c-bg-card: #FFFFFF;
  --c-text-main: #2D2D2D;
  --c-text-sub: #666666;
  --c-text-light: #999999;
  --radius-sm: 20rpx;
  --radius-md: 24rpx;
  --radius-lg: 40rpx;
}

.page {
  min-height: 100vh;
  background: var(--c-bg-body);
  font-family: "ZCOOL QingKe HuangYou", "Noto Sans SC", "PingFang SC", sans-serif;
}

.marketing {
  padding-bottom: 140rpx;
}

.role-dashboard {
  min-height: 100vh;
  padding: 36rpx 24rpx 140rpx;
  background: var(--c-bg-body);
}

.role-hero {
  padding: 34rpx 28rpx;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #ffb347 0%, #ff8800 100%);
  box-shadow: 0 12rpx 28rpx rgba(255, 136, 0, 0.2);
}

.role-title {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
  color: #ffffff;
}

.role-subtitle {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.92);
}

.role-grid {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.role-card {
  background: #ffffff;
  border-radius: 22rpx;
  padding: 24rpx 20rpx;
  box-shadow: 0 8rpx 22rpx rgba(0, 0, 0, 0.06);
}

.role-icon {
  display: block;
  font-size: 44rpx;
}

.role-name {
  display: block;
  margin-top: 10rpx;
  font-size: 30rpx;
  font-weight: 600;
  color: var(--c-text-main);
}

.role-desc {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: var(--c-text-light);
}

.role-dashboard.fallback .cta {
  margin-top: 20rpx;
  width: 100%;
}

.hero {
  position: relative;
  padding: 80rpx 32rpx 64rpx;
  overflow: hidden;
}

.hero.hero-fullscreen {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 32rpx;
}

.hero.hero-fullscreen .hero-bg {
  border-radius: 0;
}

.hero-content-center {
  max-width: none;
  padding-right: 0;
  align-items: center;
  text-align: center;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 40rpx;
}

.logo-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  font-weight: 800;
  color: var(--c-primary);
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
}

.logo-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.logo-name {
  font-size: 32rpx;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: 1rpx;
}

.logo-slogan {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 4rpx;
}

.hero-title-large {
  font-size: 56rpx;
  line-height: 1.3;
}

.hero-subtitle-center {
  text-align: center;
  max-width: none;
}

.hero-actions-center {
  justify-content: center;
  width: 100%;
}

.cta-large {
  width: 80%;
  max-width: 560rpx;
  height: 100rpx;
  font-size: 32rpx;
  border-radius: 999rpx;
}

.hero-features {
  display: flex;
  justify-content: center;
  gap: 24rpx;
  margin: 40rpx 0;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 20rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.feature-icon {
  font-size: 32rpx;
}

.feature-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.feature-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.feature-desc {
  font-size: 18rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 2rpx;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  margin-top: 40rpx;
  padding: 24rpx 32rpx;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 20rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.15);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #FFFFFF;
}

.stat-label {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 4rpx;
}

.stat-divider {
  width: 1rpx;
  height: 40rpx;
  background: rgba(255, 255, 255, 0.3);
}

.hero-metrics-center {
  justify-content: center;
  width: 100%;
}

.hero-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 40rpx 32rpx calc(40rpx + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.hero-bottom-actions {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.hero-link {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.85);
}

.hero-divider {
  color: rgba(255, 255, 255, 0.4);
}

.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: bounce 2s infinite;
}

.scroll-text {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
}

.scroll-arrow {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4rpx;
}

.orb-4 {
  width: 200rpx;
  height: 200rpx;
  bottom: 100rpx;
  right: -60rpx;
  background: rgba(255, 255, 255, 0.25);
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10rpx);
  }
  60% {
    transform: translateY(-5rpx);
  }
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(140deg, #FFA93A 0%, #FF8800 65%, #F97316 100%);
  border-radius: 0 0 80rpx 80rpx;
}

.hero-grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.16) 1rpx, transparent 1rpx);
  background-size: 34rpx 34rpx;
  opacity: 0.28;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(12rpx);
  opacity: 0.28;
}

.orb-1 {
  width: 260rpx;
  height: 260rpx;
  top: -60rpx;
  right: -40rpx;
  background: rgba(255, 255, 255, 0.4);
}

.orb-2 {
  width: 180rpx;
  height: 180rpx;
  bottom: 80rpx;
  left: -60rpx;
  background: rgba(255, 255, 255, 0.3);
}

.orb-3 {
  width: 140rpx;
  height: 140rpx;
  top: 220rpx;
  right: 120rpx;
  background: rgba(255, 255, 255, 0.2);
}

.hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  max-width: 560rpx;
  padding-right: 210rpx;
  animation: fadeUp 0.8s ease both;
}

.brand-pill {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
  font-size: 22rpx;
  letter-spacing: 1rpx;
}

.pill-icon {
  font-size: 28rpx;
}

.hero-title {
  font-size: 46rpx;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: 1rpx;
}

.hero-subtitle {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  max-width: 520rpx;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.tag {
  padding: 8rpx 14rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.16);
  border: 1rpx solid rgba(255, 255, 255, 0.22);
  color: #FFFFFF;
  font-size: 21rpx;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 10rpx;
}

.cta {
  border-radius: 24rpx;
  padding: 0 30rpx;
  height: 88rpx;
  font-size: 26rpx;
  font-weight: 600;
  border: none;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.16s ease, opacity 0.16s ease, box-shadow 0.16s ease;
}

.cta::after {
  border: none;
}

.cta:active {
  transform: scale(0.97);
  opacity: 0.92;
}

.cta.primary {
  background: #FFFFFF;
  color: var(--c-primary);
  box-shadow: 0 12rpx 26rpx rgba(17, 24, 39, 0.16);
}

.cta.ghost {
  background: rgba(255, 255, 255, 0.18);
  color: #FFFFFF;
  border: 2rpx solid rgba(255, 255, 255, 0.5);
}

.cta.outline {
  background: transparent;
  color: #FFFFFF;
  border: 2rpx solid rgba(255, 255, 255, 0.7);
}

.hero-metrics {
  display: flex;
  gap: 24rpx;
  margin-top: 20rpx;
}

.metric {
  min-width: 150rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 24rpx;
  padding: 16rpx;
  text-align: center;
  border: 1rpx solid rgba(255, 255, 255, 0.18);
}

.metric-value {
  font-size: 32rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.metric-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
}

.hero-sun {
  display: none;
}

.sun-glow {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 248, 220, 0.35) 0%, rgba(255, 210, 122, 0.24) 40%, rgba(255, 138, 42, 0.12) 64%, transparent 80%);
  filter: blur(8rpx);
  opacity: 0.82;
  mix-blend-mode: screen;
  animation: sunGlow 5s ease-in-out infinite;
}


.sun-core {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 78rpx;
  height: 78rpx;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle at 30% 30%, #FFF6C8 0%, #FFD35A 38%, #FF9A1F 70%, #FF7A00 100%);
  box-shadow: 0 0 22rpx rgba(255, 180, 60, 0.56), 0 0 44rpx rgba(255, 140, 0, 0.3);
  animation: sunPulse 3.8s ease-in-out infinite;
}

.sun-rays {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  animation: sunSpin 16s linear infinite;
}

.ray {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 4rpx;
  height: 20rpx;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(255, 200, 92, 0.72), rgba(255, 140, 0, 0));
  border-radius: 999rpx;
  opacity: 0.74;
}

.ray.r1 { transform: translate(-50%, -50%) rotate(0deg) translateY(-52rpx); }
.ray.r2 { transform: translate(-50%, -50%) rotate(45deg) translateY(-52rpx); }
.ray.r3 { transform: translate(-50%, -50%) rotate(90deg) translateY(-52rpx); }
.ray.r4 { transform: translate(-50%, -50%) rotate(135deg) translateY(-52rpx); }
.ray.r5 { transform: translate(-50%, -50%) rotate(180deg) translateY(-52rpx); }
.ray.r6 { transform: translate(-50%, -50%) rotate(225deg) translateY(-52rpx); }
.ray.r7 { transform: translate(-50%, -50%) rotate(270deg) translateY(-52rpx); }
.ray.r8 { transform: translate(-50%, -50%) rotate(315deg) translateY(-52rpx); }






.marketing-section {
  padding: 0 32rpx;
  margin-top: 56rpx;
}

.section-header.marketing {
  margin-bottom: 24rpx;
  flex-direction: column;
  align-items: flex-start;
  gap: 8rpx;
}

.section-title {
  font-size: 38rpx;
  font-weight: 700;
  color: #111827;
  letter-spacing: 0.5rpx;
}

.section-subtitle {
  font-size: 24rpx;
  color: #6B7280;
  margin-top: 10rpx;
  line-height: 1.6;
}

.card-row {
  display: flex;
  gap: 18rpx;
  flex-wrap: wrap;
}

.media-card {
  flex: 1 1 200rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 18rpx;
  border: 1rpx solid rgba(15, 23, 42, 0.05);
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
  animation: fadeUp 0.8s ease both;
}

.media-photo {
  height: 140rpx;
  border-radius: 20rpx;
  margin-bottom: 12rpx;
  background: linear-gradient(135deg, #FFE0B2, #FFCC80);
}

.media-photo.tech {
  background: linear-gradient(135deg, #FFE9C6, #FFD180);
}

.media-photo.warm {
  background: linear-gradient(135deg, #FFE8D6, #FFD6B0);
}

.media-title {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--c-text-main);
}

.media-desc {
  font-size: 22rpx;
  color: var(--c-text-light);
  margin-top: 6rpx;
}

.course-grid {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.course-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 20rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  border: 1rpx solid rgba(15, 23, 42, 0.05);
  box-shadow: 0 8rpx 20rpx rgba(15, 23, 42, 0.05);
  animation: fadeUp 0.8s ease both;
}

.course-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  background: #FFF3E0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}

.course-info {
  flex: 1;
}

.course-title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--c-text-main);
}

.course-desc {
  font-size: 22rpx;
  color: var(--c-text-light);
  margin-top: 6rpx;
}

.course-tag {
  padding: 6rpx 14rpx;
  background: #FFF7E6;
  color: var(--c-primary);
  border-radius: 16rpx;
  font-size: 20rpx;
}

.coach-row {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.coach-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 20rpx;
  display: flex;
  gap: 16rpx;
  align-items: center;
  border: 1rpx solid rgba(15, 23, 42, 0.05);
  box-shadow: 0 8rpx 20rpx rgba(15, 23, 42, 0.05);
  animation: fadeUp 0.8s ease both;
}

.coach-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  color: #FFFFFF;
}

.coach-avatar.tone-a {
  background: linear-gradient(135deg, #FFB347, #FF8800);
}

.coach-avatar.tone-b {
  background: linear-gradient(135deg, #FFC15A, #FF9F1C);
}

.coach-avatar.tone-c {
  background: linear-gradient(135deg, #FF9F68, #FF7A45);
}

.coach-info {
  flex: 1;
}

.coach-name {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--c-text-main);
}

.coach-desc {
  font-size: 22rpx;
  color: var(--c-text-light);
  margin-top: 6rpx;
}

.coach-meta {
  display: flex;
  gap: 16rpx;
  font-size: 20rpx;
  color: var(--c-text-sub);
  margin-top: 8rpx;
}

.price-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.price-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx;
  border: 1rpx solid rgba(15, 23, 42, 0.05);
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
  animation: fadeUp 0.8s ease both;
  position: relative;
}

.price-card.hot {
  border: 2rpx solid rgba(255, 136, 0, 0.4);
}

.price-title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--c-text-main);
}

.price-value {
  font-size: 40rpx;
  color: var(--c-primary);
  font-weight: 700;
  margin: 10rpx 0;
}

.price-desc {
  font-size: 22rpx;
  color: var(--c-text-light);
}

.price-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 12rpx;
}

.price-tag {
  padding: 6rpx 12rpx;
  background: #FFF3E0;
  border-radius: 14rpx;
  font-size: 20rpx;
  color: var(--c-primary);
}

.review-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16rpx;
}

.review-card {
  background: #FFFCF7;
  border-radius: 10rpx 24rpx 24rpx 24rpx;
  padding: 24rpx;
  border: 1rpx solid rgba(251, 191, 36, 0.16);
  box-shadow: 0 8rpx 18rpx rgba(15, 23, 42, 0.04);
  animation: fadeUp 0.8s ease both;
}

.review-text {
  font-size: 22rpx;
  color: var(--c-text-sub);
  line-height: 1.6;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 14rpx;
  font-size: 22rpx;
}

.review-name {
  color: var(--c-text-main);
  font-weight: 600;
}

.review-score {
  color: var(--c-primary);
}

.strategy-section {
  margin-top: 46rpx;
}

.position-card {
  background: linear-gradient(140deg, #FFF7EC 0%, #FFECD3 100%);
  border-radius: 30rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 26rpx rgba(255, 140, 0, 0.12);
  margin-bottom: 18rpx;
}

.position-badge {
  display: inline-block;
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #FFF;
  color: #D97706;
  font-size: 20rpx;
  font-weight: 700;
  margin-bottom: 12rpx;
}

.position-title {
  display: block;
  font-size: 32rpx;
  line-height: 1.45;
  color: #7C2D12;
  font-weight: 700;
}

.position-desc {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #92400E;
  line-height: 1.6;
}

.strategy-grid {
  display: grid;
  gap: 14rpx;
  margin-bottom: 14rpx;
}

.strategy-grid.two-col {
  grid-template-columns: repeat(2, 1fr);
}

.strategy-grid.three-col {
  grid-template-columns: repeat(2, 1fr);
}

.strategy-card {
  background: #FFFBF5;
  border-radius: 24rpx;
  padding: 18rpx;
  box-shadow: none;
  border: 1rpx solid #FDE7C7;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.strategy-k {
  min-width: 34rpx;
  padding: 0 6rpx;
  height: 34rpx;
  border-radius: 999rpx;
  background: #111827;
  color: #fff;
  font-size: 20rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.strategy-title {
  font-size: 26rpx;
  color: #111827;
  font-weight: 700;
  line-height: 1.4;
}

.strategy-desc {
  font-size: 22rpx;
  color: #4B5563;
  line-height: 1.55;
}

.strategy-win {
  font-size: 20rpx;
  color: #B45309;
  line-height: 1.5;
}

.strategy-toggle-wrap {
  display: flex;
  justify-content: center;
  margin-top: 10rpx;
}

.strategy-toggle {
  font-size: 24rpx;
  color: var(--c-primary);
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #fff3e0;
}

.foot-cta {
  margin: 12rpx 0 52rpx;
}

.foot-card {
  background: linear-gradient(140deg, #FF9C24 0%, #FF7A00 100%);
  border-radius: 36rpx;
  padding: 42rpx 34rpx;
  box-shadow: 0 26rpx 54rpx -20rpx rgba(255, 122, 0, 0.48);
  text-align: left;
}

.foot-head {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.foot-kicker {
  display: inline-flex;
  align-self: flex-start;
  padding: 8rpx 14rpx;
  font-size: 20rpx;
  color: #9A3412;
  background: rgba(255, 255, 255, 0.88);
  border-radius: 999rpx;
  font-weight: 700;
}

.foot-title {
  font-size: 38rpx;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.35;
}

.foot-subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  margin: 16rpx 0 24rpx;
  line-height: 1.65;
}

.foot-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12rpx;
}

.foot-actions .cta {
  width: 100%;
}

.foot-actions .cta.primary {
  background: #FFFFFF;
  color: #EA580C;
  box-shadow: none;
}

.foot-actions .cta.ghost {
  background: rgba(255, 255, 255, 0.14);
  border: 1rpx solid rgba(255, 255, 255, 0.45);
  color: #FFFFFF;
}

.trial-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99;
}

.trial-card {
  width: 80%;
  background: #FFFFFF;
  border-radius: 30rpx;
  padding: 26rpx;
}

.trial-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 28rpx;
  font-weight: 600;
  color: var(--c-text-main);
}

.trial-close {
  font-size: 28rpx;
  color: var(--c-text-light);
}

.trial-form {
  margin-top: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.trial-input {
  height: 80rpx;
  padding: 0 20rpx;
  border-radius: 20rpx;
  background: #FFF8E1;
  font-size: 24rpx;
}

.trial-submit {
  margin-top: 20rpx;
}

@media screen and (max-width: 360px) {
  .strategy-grid.two-col,
  .strategy-grid.three-col {
    grid-template-columns: 1fr;
  }

  .hero-content {
    max-width: 500rpx;
    padding-right: 170rpx;
  }

  .hero-sun {
    display: none;
  }
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(8rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-12rpx);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes sunFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(8rpx);
  }
}

@keyframes sunGlow {
  0%, 100% {
    opacity: 0.85;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.03);
  }
}

@keyframes sunPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.05);
  }
}

@keyframes sunSpin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 顶部区域 */
.header-section {
  position: relative;
  padding: 0 30rpx 40rpx;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 400rpx;
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
  border-radius: 0 0 60rpx 60rpx;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.shape1 {
  width: 200rpx;
  height: 200rpx;
  top: -50rpx;
  right: -30rpx;
}

.shape2 {
  width: 150rpx;
  height: 150rpx;
  top: 100rpx;
  left: -40rpx;
}

.shape3 {
  width: 100rpx;
  height: 100rpx;
  top: 200rpx;
  right: 100rpx;
  background: rgba(255, 255, 255, 0.15);
}

/* 用户信息栏 */
.user-bar {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 60rpx 0 30rpx;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar-wrap {
  position: relative;
}

.avatar {
  width: 110rpx;
  height: 110rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.5);
}

.avatar-badge {
  position: absolute;
  bottom: -4rpx;
  right: -4rpx;
  width: 40rpx;
  height: 40rpx;
  background: #FFD700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  border: 3rpx solid #FFFFFF;
}

.user-text {
  margin-left: 24rpx;
}

.greeting {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.user-name {
  font-size: 38rpx;
  font-weight: 700;
  color: #FFFFFF;
  margin-top: 6rpx;
}

.header-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  width: 80rpx;
  height: 80rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon {
  font-size: 40rpx;
}

/* 课时卡片 */
.lesson-card {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--c-bg-card);
  border-radius: var(--radius-md);
  padding: 30rpx;
  margin-top: 20rpx;
  box-shadow: 0 10rpx 40rpx rgba(255, 136, 0, 0.2);
}

.lesson-info {
  display: flex;
  align-items: center;
}

.lesson-icon {
  font-size: 50rpx;
  margin-right: 20rpx;
}

.lesson-text {
  display: flex;
  flex-direction: column;
}

.lesson-label {
  font-size: 26rpx;
  color: var(--c-text-light);
}

.lesson-count {
  font-size: 48rpx;
  font-weight: 800;
  color: var(--c-primary);
  line-height: 1.2;
}

.lesson-action {
  display: flex;
  align-items: center;
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #FFB347, #FF8800);
  border-radius: var(--radius-lg);
  color: #FFFFFF;
  font-size: 28rpx;
  font-weight: 600;
  box-shadow: 0 8rpx 20rpx rgba(255, 136, 0, 0.3);
}

.lesson-action .arrow {
  margin-left: 8rpx;
}

/* 功能入口 */
.feature-section {
  padding: 0 30rpx;
  margin-top: -20rpx;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
}

.feature-card {
  background: var(--c-bg-card);
  border-radius: var(--radius-md);
  padding: 30rpx 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.feature-card:active {
  transform: scale(0.95);
}

.feature-icon-wrap {
  width: 90rpx;
  height: 90rpx;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.feature-icon-wrap.growth { background: linear-gradient(135deg, #FFF3E0, #FFE0B2); }
.feature-icon-wrap.training { background: linear-gradient(135deg, #FFF8E1, #FFECB3); }
.feature-icon-wrap.moments { background: linear-gradient(135deg, #FFF8E1, #FFECB3); }
.feature-icon-wrap.orders { background: linear-gradient(135deg, #FFE8D6, #FFD6B0); }

.feature-icon {
  font-size: 44rpx;
}

.feature-name {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--c-text-main);
  margin-bottom: 6rpx;
}

.feature-desc {
  font-size: 20rpx;
  color: var(--c-text-light);
}

/* 通用区块 */
.section {
  margin: 30rpx;
  background: var(--c-bg-card);
  border-radius: var(--radius-md);
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-title {
  display: flex;
  align-items: center;
}

.title-icon {
  font-size: 36rpx;
  margin-right: 12rpx;
}

.title-text {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.section-more {
  display: flex;
  align-items: center;
  font-size: 26rpx;
  color: var(--c-text-light);
}

.more-arrow {
  margin-left: 6rpx;
}

/* 课程列表 */
.course-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.course-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #FFF8E1;
  border-radius: var(--radius-sm);
}

.course-time-block {
  min-width: 100rpx;
  text-align: center;
}

.course-time {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--c-primary);
  display: block;
}

.course-duration {
  font-size: 22rpx;
  color: var(--c-text-light);
}

.course-divider {
  width: 4rpx;
  height: 60rpx;
  background: linear-gradient(180deg, #FFB347, #FF8800);
  border-radius: 2rpx;
  margin: 0 24rpx;
}

.course-detail {
  flex: 1;
}

.course-name {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--c-text-main);
  display: block;
  margin-bottom: 8rpx;
}

.course-meta {
  display: flex;
  align-items: center;
}

.coach-name {
  font-size: 24rpx;
  color: var(--c-text-sub);
}

.course-status {
  padding: 10rpx 20rpx;
  border-radius: var(--radius-sm);
  font-size: 24rpx;
  font-weight: 500;
}

.course-status.scheduled {
  background: #FFF3E0;
  color: var(--c-primary);
}

.course-status.ongoing {
  background: #FFF8E1;
  color: #F57C00;
}

.course-status.completed {
  background: #FFF3E0;
  color: var(--c-secondary);
}

.course-status.cancelled {
  background: #FFF8E1;
  color: var(--c-text-light);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 50rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 30rpx;
  color: var(--c-text-sub);
  display: block;
  margin-bottom: 10rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: var(--c-text-light);
}

/* 统计区域 */
.stats-section {
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
}

.stats-section .section-title .title-icon,
.stats-section .section-title .title-text {
  color: #FFFFFF;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-sm);
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-icon-wrap {
  width: 70rpx;
  height: 70rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.stat-icon-wrap.sessions { background: rgba(255, 255, 255, 0.25); }
.stat-icon-wrap.duration { background: rgba(255, 255, 255, 0.25); }
.stat-icon-wrap.calories { background: rgba(255, 255, 255, 0.25); }

.stat-icon {
  font-size: 36rpx;
}

.stat-content {
  text-align: center;
}

.stat-value {
  font-size: 44rpx;
  font-weight: 800;
  color: #FFFFFF;
  display: block;
  line-height: 1.2;
}

.stat-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 榧撳姳妯箙 */
.encourage-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 24rpx;
  padding: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
}

.encourage-icon {
  font-size: 36rpx;
  margin-right: 12rpx;
}

.encourage-text {
  font-size: 28rpx;
  color: #FFFFFF;
  font-weight: 500;
}

/* 底部安全区 */
.safe-bottom {
  height: 120rpx;
}
</style>
