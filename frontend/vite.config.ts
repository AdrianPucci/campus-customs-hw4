import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Send API calls and product images to the FastAPI backend on port 8000,
    // so the browser only ever talks to one address.
    proxy: {
      '/api': 'http://localhost:8000',
      '/media': 'http://localhost:8000',
    },
  },
})
