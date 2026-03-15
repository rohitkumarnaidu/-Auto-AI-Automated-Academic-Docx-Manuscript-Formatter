import { test, expect } from '@playwright/test';

test('billing quota indicator visualization', async ({ page }) => {
    await page.goto('/settings?tab=billing');
    
    // Check for "Usage Highlights" and the progress bar
    await expect(page.locator('text=Usage Highlights')).toBeVisible();
    await expect(page.locator('.bg-primary.h-1\\.5.rounded-full')).toBeVisible();
});
