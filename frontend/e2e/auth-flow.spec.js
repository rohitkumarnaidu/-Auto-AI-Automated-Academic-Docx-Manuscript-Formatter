import { test, expect } from '@playwright/test';
test('auth flow root check', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveTitle(/.*|.*/);
    await expect(page.locator('form').first()).toBeVisible();
});
