import { test, expect } from '@playwright/test';

test('SEO metadata check', async ({ page }) => {
    await page.goto('/');
    
    await expect(page).toHaveTitle(/ScholarForm AI/);
    
    const metaDescription = page.locator('meta[name="description"]');
    await expect(metaDescription).toHaveAttribute('content', /academic|manuscript|formatter/i);
});
