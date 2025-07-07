import { test, expect } from '@playwright/test'

test('dataset navigation', async ({ page }) => {
  await page.goto('/')
  await page.click('text=Datasets')
  await expect(page).toHaveURL(/\/datasets$/)
  await page.click('text=master')
  await expect(page).toHaveURL(/\/datasets\/master/)
  await expect(page.locator('text=Dataset: master')).toBeVisible()
})
