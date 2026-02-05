<template>
  <view class="page">
    <view v-if="!userStore.isLoggedIn" class="marketing">
      <view class="hero">
        <view class="hero-bg">
          <view class="hero-orb orb-1"></view>
          <view class="hero-orb orb-2"></view>
          <view class="hero-orb orb-3"></view>
          <view class="hero-grid"></view>
        </view>
        <view class="hero-content">
          <view class="brand-pill">
            <text class="pill-icon">鈽€锔?/text>
            <text>鏄撲箰鑸稩TS鏅烘収浣撴暀</text>
          </view>
          <text class="hero-title">闈掓槬鍚戜笂 路 杩愬姩鏇村揩涔?/text>
          <text class="hero-subtitle">涓撲笟鏁欑粌 + 绉戝璇炬椂 + 鏅鸿兘闄粌锛屾墦閫犲瀛愮殑杩愬姩鎴愰暱浣撶郴</text>
          <view class="hero-tags">
            <view class="tag">涓撲笟鏁欑粌</view>
            <view class="tag">鐏垫椿绾﹁</view>
            <view class="tag">AI闄粌</view>
            <view class="tag">瀹夊叏鍚堣</view>
          </view>
          <view class="hero-actions">
            <button class="cta primary" @click="handleBooking">鍦ㄧ嚎棰勭害</button>
            <button class="cta ghost" @click="openTrial">鍏嶈垂浣撻獙璇炬姤鍚?/button>
            <button class="cta outline" @click="handleConsult">涓€閿挩璇?/button>
          </view>
          <view class="hero-metrics">
            <view class="metric">
              <text class="metric-value">98%</text>
              <text class="metric-label">婊℃剰搴?/text>
            </view>
            <view class="metric">
              <text class="metric-value">12K+</text>
              <text class="metric-label">绱涓婅</text>
            </view>
            <view class="metric">
              <text class="metric-value">50+</text>
              <text class="metric-label">鏄庢槦鏁欑粌</text>
            </view>
          </view>
        </view>
        <view class="hero-mascot">
          <view class="mascot-core">
            <view class="mascot-face">鈿?/view>
          </view>
          <view class="mascot-ring"></view>
          <view class="mascot-label">鑸粩 路 杩愬姩IP</view>
        </view>
      </view>

      <view class="marketing-section">
        <view class="section-header marketing">
          <text class="section-title">鐜涓庡満棣?/text>
          <text class="section-subtitle">瀹夊叏銆佸共鍑€銆佹槑浜紝瀛╁瓙杩愬姩鏇翠笓娉?/text>
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
          <text class="section-title">绮惧搧璇剧▼</text>
          <text class="section-subtitle">娆″崱 / 鏈堝崱 / 绉佹暀 / 濂楅锛岃鐩栧鍦烘櫙</text>
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
          <text class="section-title">鏁欑粌鍥㈤槦</text>
          <text class="section-subtitle">澶氶」鐩璇侊紝骞冲潎5骞翠互涓婃暀瀛︾粡楠?/text>
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
                <text>猸?{{ coach.rating }}</text>
                <text>{{ coach.years }}骞寸粡楠?/text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="marketing-section">
        <view class="section-header marketing">
          <text class="section-title">浠锋牸鏂规</text>
          <text class="section-subtitle">鐏垫椿璁¤垂锛屾敮鎸佸彂绁ㄤ笌缁垂鎻愰啋</text>
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
          <text class="section-title">瀛﹀憳鍙ｇ</text>
          <text class="section-subtitle">鐪熷疄瀹堕暱鍙嶉锛屽璐巼鎸佺画涓婂崌</text>
        </view>
        <view class="review-grid">
          <view
            v-for="(review, index) in reviewCards"
            :key="review.name"
            class="review-card"
            :style="{ animationDelay: `${index * 0.06}s` }"
          >
            <text class="review-text">{{ review.text }}</text>
            <view class="review-footer">
              <text class="review-name">{{ review.name }}</text>
              <text class="review-score">猸?{{ review.score }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="marketing-section ai-section">
        <view class="ai-card">
          <view class="ai-content">
            <text class="ai-title">AI闄粌 路 鏅鸿兘鎴愰暱鍔╂墜</text>
            <text class="ai-desc">璺崇怀鍔ㄤ綔璇嗗埆銆佸Э鎬佽瘎浼般€佽繍鍔ㄥ缓璁笌楗寤鸿锛屾敮鎸佸闀挎彁闂€?/text>
            <view class="ai-features">
              <text class="ai-chip">鑷姩璁℃暟</text>
              <text class="ai-chip">鍔ㄤ綔绾犳</text>
              <text class="ai-chip">鎴愰暱鎶ュ憡</text>
              <text class="ai-chip">瀹堕暱闂瓟</text>
            </view>
          </view>
          <view class="ai-cta">
            <button class="cta primary" @click="goTo('/pages/training/index')">浣撻獙AI闄粌</button>
            <text class="ai-note">* AI妯″潡鍙€愭鍚敤</text>
          </view>
        </view>
      </view>

      <view class="marketing-section foot-cta">
        <view class="foot-card">
          <text class="foot-title">鍑嗗濂藉紑濮嬩簡鍚楋紵</text>
          <text class="foot-subtitle">涓€閿绾︼紝涓撳睘鏁欑粌涓哄瀛愯鍒掕绋嬨€?/text>
          <view class="foot-actions">
            <button class="cta primary" @click="handleBooking">绔嬪嵆棰勭害</button>
            <button class="cta ghost" @click="openTrial">棰嗗彇浣撻獙璇?/button>
          </view>
        </view>
      </view>

      <view class="trial-modal" v-if="trialVisible">
        <view class="trial-card">
          <view class="trial-header">
            <text>鍏嶈垂浣撻獙璇炬姤鍚?/text>
            <text class="trial-close" @click="trialVisible = false">鉁?/text>
          </view>
          <view class="trial-form">
            <input class="trial-input" v-model="trialForm.name" placeholder="瀛╁瓙濮撳悕" />
            <input class="trial-input" v-model="trialForm.phone" placeholder="瀹堕暱鎵嬫満鍙? />
            <input class="trial-input" v-model="trialForm.age" placeholder="瀛╁瓙骞撮緞" />
          </view>
          <button class="cta primary trial-submit" @click="submitTrial">鎻愪氦鎶ュ悕</button>
        </view>
      </view>
    </view>

    <view v-else class="dashboard">
      <!-- 椤堕儴鍖哄煙 -->
    <view class="header-section">
      <!-- 鑳屾櫙瑁呴グ -->
      <view class="header-bg">
        <view class="bg-shape shape1"></view>
        <view class="bg-shape shape2"></view>
        <view class="bg-shape shape3"></view>
      </view>

      <!-- 鐢ㄦ埛淇℃伅鏍?-->
      <view class="user-bar">
        <view class="user-info" @click="goToUser">
          <view class="avatar-wrap">
            <image class="avatar" :src="userStore.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
            <view class="avatar-badge">馃弮</view>
          </view>
          <view class="user-text">
            <text class="greeting">{{ getGreeting() }}</text>
            <text class="user-name">{{ currentStudentName }}</text>
          </view>
        </view>
        <view class="header-actions">
          <view class="action-btn" @click="scanQRCode">
            <text class="action-icon">馃摲</text>
          </view>
        </view>
      </view>

      <!-- 璇炬椂鍗＄墖 -->
      <view class="lesson-card">
        <view class="lesson-info">
          <view class="lesson-icon">鈴憋笍</view>
          <view class="lesson-text">
            <text class="lesson-label">鍓╀綑璇炬椂</text>
            <text class="lesson-count">{{ userStore.currentStudent?.remaining_lessons || 0 }}</text>
          </view>
        </view>
        <view class="lesson-action" @click="goTo('/pages/membership/index')">
          <text>鍏呭€?/text>
          <text class="arrow">鈫?/text>
        </view>
      </view>
    </view>

    <!-- 鍔熻兘鍏ュ彛 -->
    <view class="feature-section">
      <view class="feature-grid">
        <view class="feature-card" @click="goTo('/pages/growth/index')">
          <view class="feature-icon-wrap growth">
            <text class="feature-icon">馃搳</text>
          </view>
          <text class="feature-name">鎴愰暱妗ｆ</text>
          <text class="feature-desc">鏌ョ湅杩愬姩鏁版嵁</text>
        </view>

        <view class="feature-card" @click="goTo('/pages/training/index')">
          <view class="feature-icon-wrap training">
            <text class="feature-icon">馃</text>
          </view>
          <text class="feature-name">AI闄粌</text>
          <text class="feature-desc">鏅鸿兘杩愬姩鎸囧</text>
        </view>

        <view class="feature-card" @click="goTo('/pages/moments/index')">
          <view class="feature-icon-wrap moments">
            <text class="feature-icon">馃摳</text>
          </view>
          <text class="feature-name">绮惧僵鐬棿</text>
          <text class="feature-desc">璁板綍鎴愰暱鏃跺埢</text>
        </view>

        <view class="feature-card" @click="goTo('/pages/booking/index')">
          <view class="feature-icon-wrap orders">
            <text class="feature-icon">馃Ь</text>
          </view>
          <text class="feature-name">鎴戠殑璁㈠崟</text>
          <text class="feature-desc">棰勭害涓庢秷璐?/text>
        </view>
      </view>
    </view>

    <!-- 浠婃棩璇剧▼ -->
    <view class="section">
      <view class="section-header">
        <view class="section-title">
          <text class="title-icon">馃搮</text>
          <text class="title-text">浠婃棩璇剧▼</text>
        </view>
        <view class="section-more" @click="goTo('/pages/schedule/index')">
          <text>鍏ㄩ儴</text>
          <text class="more-arrow">鈫?/text>
        </view>
      </view>

      <view class="course-list" v-if="todayCourses.length">
        <view class="course-item" v-for="course in todayCourses" :key="course.id">
          <view class="course-time-block">
            <text class="course-time">{{ formatTime(course.start_time) }}</text>
            <text class="course-duration">{{ course.duration }}鍒嗛挓</text>
          </view>
          <view class="course-divider"></view>
          <view class="course-detail">
            <text class="course-name">{{ course.name }}</text>
            <view class="course-meta">
              <text class="coach-name">馃懆鈥嶐煆?{{ course.coach_name }}</text>
            </view>
          </view>
          <view :class="['course-status', course.status]">
            <text>{{ getStatusText(course.status) }}</text>
          </view>
        </view>
      </view>

      <view class="empty-state" v-else>
        <view class="empty-icon">馃専</view>
        <text class="empty-text">浠婃棩鏆傛棤璇剧▼</text>
        <text class="empty-hint">鍘婚绾︿竴鑺傝鍚?/text>
      </view>
    </view>

    <!-- 鏈懆缁熻 -->
    <view class="section stats-section">
      <view class="section-header">
        <view class="section-title">
          <text class="title-icon">馃搱</text>
          <text class="title-text">鏈懆杩愬姩</text>
        </view>
      </view>

      <view class="stats-grid">
        <view class="stat-card">
          <view class="stat-icon-wrap sessions">
            <text class="stat-icon">馃弸锔?/text>
          </view>
          <view class="stat-content">
            <text class="stat-value">{{ weekStats.sessions }}</text>
            <text class="stat-label">璁粌娆℃暟</text>
          </view>
        </view>

        <view class="stat-card">
          <view class="stat-icon-wrap duration">
            <text class="stat-icon">鈴?/text>
          </view>
          <view class="stat-content">
            <text class="stat-value">{{ weekStats.duration }}</text>
            <text class="stat-label">璁粌鏃堕暱(鍒?</text>
          </view>
        </view>

        <view class="stat-card">
          <view class="stat-icon-wrap calories">
            <text class="stat-icon">馃敟</text>
          </view>
          <view class="stat-content">
            <text class="stat-value">{{ weekStats.calories }}</text>
            <text class="stat-label">娑堣€楀崱璺噷</text>
          </view>
        </view>
      </view>

      <!-- 榧撳姳璇?-->
      <view class="encourage-banner" v-if="weekStats.sessions > 0">
        <text class="encourage-icon">馃挭</text>
        <text class="encourage-text">{{ getEncourageText() }}</text>
      </view>
    </view>

    <!-- 搴曢儴瀹夊叏鍖?-->
    <view class="safe-bottom"></view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { scheduleApi, trainingApi } from '@/api'
import { trackEvent } from '@/utils/track'

const userStore = useUserStore()

const currentStudentName = computed(() => {
  return userStore.currentStudent?.name || userStore.user?.nickname || '灏忔湅鍙?
})

const todayCourses = ref<any[]>([])

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
  { title: '闃冲厜鍦洪', desc: '鑷劧閲囧厜涓庡畨鍏ㄨ蒋鍨紝瀹堟姢姣忎竴姝?, tone: 'sun' },
  { title: '鏅鸿兘璁惧', desc: '绉戝璁粌鍣ㄦ涓庣洃娴嬬郴缁?, tone: 'tech' },
  { title: '浜插瓙绌洪棿', desc: '瀹堕暱浼戞伅鍖轰笌瑙傛懇鍖?, tone: 'warm' }
]

const courseCards = [
  { title: '绡悆鍩虹鐝?, desc: '鍔ㄤ綔瑙勮寖 + 浣撹兘鎻愬崌', icon: '馃弨', tag: '閫傚悎7-12宀? },
  { title: '浣撹兘鎻愬崌璇?, desc: '鏍稿績鍔涢噺涓庡崗璋?, icon: '馃敟', tag: '鍏ㄨ兘璁粌' },
  { title: '涓撻」绉佹暀', desc: '涓€瀵逛竴娣卞害璁粌', icon: '馃幆', tag: '鎴愰暱鍔犻€? },
  { title: '杩愬姩绱犲吇璇?, desc: '浣撴€?涔犳儻鍏绘垚', icon: '馃尶', tag: '绋虫墡绋虫墦' }
]

const coachCards = [
  { name: '鐜嬫暀缁?, desc: '绡悆鍥藉浜岀骇 路 浣撹兘璁粌', rating: '4.9', years: 6, initial: '鐜?, tone: 'tone-a' },
  { name: '闄堟暀缁?, desc: '浣撻€傝兘璁よ瘉 路 鍔ㄤ綔绾犳', rating: '4.8', years: 5, initial: '闄?, tone: 'tone-b' },
  { name: '鏉庢暀缁?, desc: '闈掑皯骞翠笓椤?路 璇剧▼璁捐', rating: '4.9', years: 7, initial: '鏉?, tone: 'tone-c' }
]

const priceCards = [
  { title: '娆″崱浣撻獙', price: '楼199', desc: '2娆′綋楠岃', tags: ['鐏垫椿鎺掕', '闅忕害闅忎笂'], hot: false },
  { title: '鏈堝崱鎴愰暱', price: '楼899', desc: '12娆″皬鐝', tags: ['璇炬椂鎻愰啋', '鍙浆璧?], hot: true },
  { title: '绉佹暀璁″垝', price: '楼1999', desc: '8娆＄鏁欒', tags: ['涓撳睘鏁欑粌', '鎴愰暱鎶ュ憡'], hot: false }
]

const reviewCards = [
  { name: '鍛ㄥ濡?, score: '4.9', text: '瀛╁瓙涓婅寰堢Н鏋侊紝鏁欑粌鍙嶉缁嗚嚧锛岃绋嬪畨鎺掍篃寰堢伒娲汇€? },
  { name: '鏋楃埜鐖?, score: '5.0', text: '浣撹兘鏀瑰杽鏄庢樉锛岃绋嬬郴缁燂紝瀛╁瓙鏇磋嚜淇′簡銆? },
  { name: '鏅撻洦濡堝', score: '4.8', text: '绾﹁鏂逛究锛屾彁閱掑強鏃讹紝鏁翠綋浣撻獙寰堣垝鏈嶃€? }
]

function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 6) return '澶滄繁浜?
  if (hour < 9) return '鏃╀笂濂?
  if (hour < 12) return '涓婂崍濂?
  if (hour < 14) return '涓崍濂?
  if (hour < 18) return '涓嬪崍濂?
  if (hour < 22) return '鏅氫笂濂?
  return '澶滄繁浜?
}

function getEncourageText() {
  const sessions = weekStats.value.sessions
  if (sessions >= 5) return '澶浜嗭紒鏈懆杩愬姩杈句汉灏辨槸浣狅紒'
  if (sessions >= 3) return '缁х画淇濇寔锛屼綘鍋氬緱寰堝ソ锛?
  if (sessions >= 1) return '濂界殑寮€濮嬶紝缁х画鍔犳补锛?
  return '寮€濮嬩綘鐨勮繍鍔ㄤ箣鏃呭惂锛?
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
    console.error('鍔犺浇璇剧▼澶辫触', error)
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
    console.error('鍔犺浇缁熻澶辫触', error)
  }
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    scheduled: '寰呬笂璇?,
    ongoing: '杩涜涓?,
    completed: '宸插畬鎴?,
    cancelled: '宸插彇娑?
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
    uni.showToast({ title: '璇峰～鍐欏鍚嶅拰鎵嬫満鍙?, icon: 'none' })
    return
  }
  trackEvent('trial_submit', { ...trialForm.value })
  uni.showToast({ title: '鎶ュ悕鎴愬姛锛屾垜浠細灏藉揩鑱旂郴', icon: 'none' })
  trialVisible.value = false
  trialForm.value = { name: '', phone: '', age: '' }
}

function handleConsult() {
  trackEvent('consult_click')
  if (contactPhone && typeof uni.makePhoneCall === 'function') {
    uni.makePhoneCall({ phoneNumber: contactPhone })
    return
  }
  uni.showToast({ title: '璇风◢鍚庡啀璇?, icon: 'none' })
}

function goToUser() {
  uni.switchTab({ url: '/pages/user/index' })
}

function scanQRCode() {
  uni.scanCode({
    success: (res) => {
      console.log('鎵爜缁撴灉', res)
    }
  })
}
</script>

<style scoped>
/* 璁捐鍙橀噺 */
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

.hero {
  position: relative;
  padding: 80rpx 28rpx 60rpx;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 60%, #FF7A18 100%);
  border-radius: 0 0 80rpx 80rpx;
}

.hero-grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.16) 1rpx, transparent 1rpx);
  background-size: 30rpx 30rpx;
  opacity: 0.5;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(6rpx);
  opacity: 0.5;
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
  animation: fadeUp 0.8s ease both;
}

.brand-pill {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
  font-size: 24rpx;
  letter-spacing: 2rpx;
}

.pill-icon {
  font-size: 28rpx;
}

.hero-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.hero-subtitle {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
  font-size: 22rpx;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 10rpx;
}

.cta {
  border-radius: 999rpx;
  padding: 20rpx 30rpx;
  font-size: 26rpx;
  font-weight: 600;
  border: none;
  line-height: 1;
}

.cta::after {
  border: none;
}

.cta.primary {
  background: #FFFFFF;
  color: var(--c-primary);
  box-shadow: 0 12rpx 24rpx rgba(0, 0, 0, 0.15);
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
  background: rgba(255, 255, 255, 0.18);
  border-radius: 24rpx;
  padding: 16rpx;
  text-align: center;
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

.hero-mascot {
  position: absolute;
  right: 26rpx;
  bottom: -40rpx;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mascot-core {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20rpx 40rpx rgba(0, 0, 0, 0.2);
  animation: float 4s ease-in-out infinite;
}

.mascot-face {
  font-size: 64rpx;
}

.mascot-ring {
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  border: 6rpx dashed rgba(255, 255, 255, 0.6);
  margin-top: -180rpx;
  animation: spin 12s linear infinite;
}

.mascot-label {
  margin-top: 12rpx;
  font-size: 22rpx;
  color: #FFFFFF;
}

.marketing-section {
  padding: 0 28rpx;
  margin-top: 40rpx;
}

.section-header.marketing {
  margin-bottom: 20rpx;
  flex-direction: column;
  align-items: flex-start;
  gap: 6rpx;
}

.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.section-subtitle {
  font-size: 24rpx;
  color: var(--c-text-light);
  margin-top: 8rpx;
}

.card-row {
  display: flex;
  gap: 18rpx;
  flex-wrap: wrap;
}

.media-card {
  flex: 1 1 200rpx;
  background: #FFFFFF;
  border-radius: 26rpx;
  padding: 16rpx;
  box-shadow: 0 10rpx 26rpx rgba(0, 0, 0, 0.06);
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
  box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.06);
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
  box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.06);
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
  border-radius: 26rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 26rpx rgba(0, 0, 0, 0.06);
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
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.review-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 20rpx;
  box-shadow: 0 10rpx 24rpx rgba(0, 0, 0, 0.06);
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

.ai-section {
  margin-top: 50rpx;
}

.ai-card {
  background: linear-gradient(135deg, #FFB347 0%, #FF8800 100%);
  border-radius: 30rpx;
  padding: 28rpx;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  box-shadow: 0 16rpx 30rpx rgba(255, 136, 0, 0.3);
}

.ai-title {
  font-size: 32rpx;
  font-weight: 700;
}

.ai-desc {
  font-size: 24rpx;
  opacity: 0.95;
  line-height: 1.6;
}

.ai-features {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.ai-chip {
  padding: 8rpx 16rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 18rpx;
  font-size: 22rpx;
}

.ai-cta {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.ai-note {
  font-size: 20rpx;
  opacity: 0.8;
}

.foot-cta {
  margin-bottom: 40rpx;
}

.foot-card {
  background: #FFFFFF;
  border-radius: 30rpx;
  padding: 28rpx;
  box-shadow: 0 14rpx 26rpx rgba(0, 0, 0, 0.06);
  text-align: center;
}

.foot-title {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--c-text-main);
}

.foot-subtitle {
  font-size: 24rpx;
  color: var(--c-text-light);
  margin: 12rpx 0 20rpx;
}

.foot-actions {
  display: flex;
  justify-content: center;
  gap: 16rpx;
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

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16rpx);
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

/* 椤堕儴鍖哄煙 */
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

/* 鐢ㄦ埛淇℃伅鏍?*/
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

/* 璇炬椂鍗＄墖 */
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

/* 鍔熻兘鍏ュ彛 */
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

/* 閫氱敤鍖哄潡 */
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

/* 璇剧▼鍒楄〃 */
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

/* 绌虹姸鎬?*/
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

/* 缁熻鍖哄潡 */
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

/* 榧撳姳妯箙 */
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

/* 搴曢儴瀹夊叏鍖?*/
.safe-bottom {
  height: 120rpx;
}
</style>
