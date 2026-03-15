import { test, expect } from '@playwright/test';

test('generator empty state', async ({ page }) => {
    await page.goto('/generate');
    // Check for "No documents yet" or similar guidance
    await expect(page.locator('text=Upload')).toBeVisible();
});
