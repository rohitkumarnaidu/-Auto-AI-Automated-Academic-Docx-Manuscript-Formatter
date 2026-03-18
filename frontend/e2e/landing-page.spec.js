import { test, expect } from '@playwright/test';
test('landing page loads hero section', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible();
});
