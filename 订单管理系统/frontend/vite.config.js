import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发服务器把 /api 转发到 FastAPI 后端（127.0.0.1:8000），
// 前端代码里统一请求 /api/xxx，不用关心跨域问题
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // 头像等静态文件也走后端
      '/files': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
