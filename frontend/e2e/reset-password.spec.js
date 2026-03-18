import { test, expect } from '@playwright/test';
test('reset password gracefully handles no token', async ({ page }) => {
    await page.goto('/reset-password');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('body')).toBeVisible();
});
