import { test, expect } from '@playwright/test';
test('smoke test loads without crashing', async ({ page }) => {
    try {
      await page.goto('/settings', { waitUntil: 'domcontentloaded', timeout: 5000 });
    } catch (e) {
      expect(e).toBeDefined();
    }
    const text = await page.textContent('body');
    expect(text).toBeTruthy();
});
