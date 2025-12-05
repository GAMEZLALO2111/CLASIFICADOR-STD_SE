import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // Permite acceso desde la red local
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://10.106.113.32:8000',
        changeOrigin: true
      }
    }
  }
})
