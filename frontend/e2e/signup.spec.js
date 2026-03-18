import { test, expect } from '@playwright/test';
test('signup page has form inputs', async ({ page }) => {
    await page.goto('/signup');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
});
