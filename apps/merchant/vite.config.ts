import { defineConfig } from 'vite'
// @ts-ignore
import UniPlugin from '@dcloudio/vite-plugin-uni'

const uni = UniPlugin.default || UniPlugin

export default defineConfig({
  plugins: [uni()],
  server: {
    port: 5175,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
