import { defineConfig } from '@playwright/test'
import { fileURLToPath } from 'url'
import path from 'path'

export default defineConfig({
  testDir: './e2e',
  webServer: {
    command: 'pnpm dev',
    cwd: path.dirname(fileURLToPath(import.meta.url)),
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://localhost:5173',
  },
})
