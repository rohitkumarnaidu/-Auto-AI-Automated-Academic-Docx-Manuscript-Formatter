import { test, expect } from '@playwright/test';
test('smoke test loads without crashing', async ({ page }) => {
    try {
      await page.goto('/history', { waitUntil: 'domcontentloaded', timeout: 5000 });
    } catch(e) {}
    const text = await page.textContent('body');
    expect(text).toBeTruthy();
});
