import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { merchantAuthApi } from '@/api'

interface MerchantInfo {
  id: number
  name: string
  logo: string | null
  contact_phone: string | null
  address: string | null
  status: string
}

export const useMerchantStore = defineStore('merchant', () => {
  const merchant = ref<MerchantInfo | null>(null)
  const token = ref<string>('')

  const isLoggedIn = computed(() => !!token.value)

  function init() {
    token.value = uni.getStorageSync('merchant_token') || ''
    const savedInfo = uni.getStorageSync('merchant_info')
    if (!savedInfo) return

    try {
      merchant.value = JSON.parse(savedInfo)
    } catch {
      merchant.value = null
    }
  }

  async function login(account: string, password: string) {
    const res: any = await merchantAuthApi.login(account, password)
    token.value = res.access_token
    uni.setStorageSync('merchant_token', res.access_token)
    await fetchProfile()
    return true
  }

  async function fetchProfile() {
    try {
      const res: any = await merchantAuthApi.getProfile()
      merchant.value = res
      uni.setStorageSync('merchant_info', JSON.stringify(res))
    } catch (error) {
      console.error('获取商家信息失败', error)
    }
  }

  function logout() {
    token.value = ''
    merchant.value = null
    uni.removeStorageSync('merchant_token')
    uni.removeStorageSync('merchant_info')
  }

  function checkLogin(): boolean {
    if (!isLoggedIn.value) {
      uni.navigateTo({ url: '/pages/user/login' })
      return false
    }
    return true
  }

  init()

  return {
    merchant,
    token,
    isLoggedIn,
    login,
    logout,
    fetchProfile,
    checkLogin
  }
})
