import { test, expect } from '@playwright/test';

test('404 page shows up for invalid routes', async ({ page }) => {
    await page.goto('/this-page-does-not-exist');
    
    await expect(page.locator('text=404')).toBeVisible();
    await expect(page.locator('text=Return Home')).toBeVisible();
});
