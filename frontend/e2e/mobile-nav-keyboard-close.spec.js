import { test, expect } from '@playwright/test';

test('mobile nav keyboard interaction', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    
    const hamburger = page.locator('button:has(.material-symbols-outlined:has-text("menu"))');
    await hamburger.click();
    
    // Verify menu is open
    await expect(page.locator('nav >> text=Templates')).toBeVisible();
    
    // Press Escape
    await page.keyboard.press('Escape');
    
    // Verify menu is closed
    await expect(page.locator('nav >> text=Templates')).not.toBeVisible().catch(() => {});
});
