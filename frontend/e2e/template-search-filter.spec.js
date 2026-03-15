import { test, expect } from '@playwright/test';

test('template search and filtering', async ({ page }) => {
    await page.goto('/templates');
    
    const searchInput = page.locator('input[placeholder*="Search"]');
    if (await searchInput.isVisible()) {
        await searchInput.fill('IEEE');
        await expect(page.locator('.grid >> text=IEEE')).toBeVisible();
        await expect(page.locator('.grid >> text=Nature')).not.toBeVisible();
    }
});
