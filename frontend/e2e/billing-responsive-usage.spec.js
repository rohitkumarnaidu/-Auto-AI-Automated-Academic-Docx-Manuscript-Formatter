import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 812 } });

test('mobile billing UI check', async ({ page }) => {
    await page.goto('/settings?tab=billing');
    
    // Ensure usage card is visible
    await expect(page.locator('text=Usage Highlights')).toBeVisible();
    
    // Upgrade button should be full width
    const upgradeBtn = page.locator('button:has-text("Upgrade")').first();
    if (await upgradeBtn.isVisible()) {
        const box = await upgradeBtn.boundingBox();
        expect(box.width).toBeGreaterThan(300);
    }
});
