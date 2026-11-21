import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// 开发时把 /api 与 /health 代理到本地后端（默认 8000 端口），
// 避免跨域；Docker 里通过 BACKEND_URL 环境变量指向 backend 服务。
// 例：BACKEND_URL=http://backend:8000
const backend = process.env.BACKEND_URL || 'http://localhost:8000'
const proxy = {
  '/api': { target: backend, changeOrigin: true },
  '/health': { target: backend, changeOrigin: true },
}

export default defineConfig({
  plugins: [vue()],
  server: { port: 5173, proxy },
  preview: { port: 4173, host: '0.0.0.0', proxy },
})
