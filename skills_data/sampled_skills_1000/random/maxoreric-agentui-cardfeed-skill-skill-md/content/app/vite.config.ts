import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Serve the data folder at /data
    proxy: {
      '/data': {
        target: 'http://localhost:5173',
        rewrite: () => '',
      }
    }
  },
  publicDir: path.resolve(__dirname, '../data'),
})
