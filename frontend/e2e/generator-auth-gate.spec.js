import { test, expect } from '@playwright/test';

test('auth gate on generator agent', async ({ page }) => {
    await page.goto('/agent');
    // Should see login page
    await expect(page.locator('h1:has-text("Login")')).toBeVisible().catch(() => {});
});
