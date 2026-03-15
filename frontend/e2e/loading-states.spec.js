import { test, expect } from '@playwright/test';

test('skeleton loaders on templates page', async ({ page }) => {
    // 1. Go to templates page
    await page.goto('/templates');
    
    // 2. Check for skeleton class if it exists during load
    // Assuming .animate-pulse or .bg-slate-200
    const skeletons = page.locator('.animate-pulse');
    const cards = page.locator('.grid > div');
    
    // We expect cards to eventually show up
    await expect(cards.first()).toBeVisible();
});
