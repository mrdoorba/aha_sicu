import path from 'path'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined

          if (id.includes('firebase')) return 'firebase-vendor'
          if (id.includes('recharts') || id.includes('/d3-')) return 'charts-vendor'
          if (
            id.includes('@tanstack/react-query') ||
            id.includes('@tanstack/query-core') ||
            id.includes('openapi-fetch')
          ) {
            return 'data-vendor'
          }
          if (
            id.includes('react-router') ||
            id.includes('/react/') ||
            id.includes('/react-dom/')
          ) {
            return 'react-vendor'
          }
          if (
            id.includes('@radix-ui') ||
            id.includes('/radix-ui/') ||
            id.includes('react-day-picker') ||
            id.includes('lucide-react') ||
            id.includes('sonner')
          ) {
            return 'ui-vendor'
          }
          if (
            id.includes('i18next') ||
            id.includes('react-i18next') ||
            id.includes('date-fns')
          ) {
            return 'i18n-vendor'
          }
          
          return undefined
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    pool: 'forks',
    // Keep local full-suite runs stable when git hooks run lint/typecheck in parallel.
    maxWorkers: 1,
  },
})
