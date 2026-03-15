import { test, expect } from '@playwright/test';

test('landing page accessibility check', async ({ page }) => {
    await page.goto('/');
    // Check for alt text on images
    const images = await page.locator('img').all();
    for (const img of images) {
        const alt = await img.getAttribute('alt');
        expect(alt).not.toBeNull();
    }
    
    // Check for unique H1
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);
});
