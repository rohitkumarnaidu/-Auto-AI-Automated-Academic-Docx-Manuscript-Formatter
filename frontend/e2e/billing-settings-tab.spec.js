import { test, expect } from '@playwright/test';

test('settings tabs interaction', async ({ page }) => {
    await page.goto('/settings');
    
    // Click Billing & Plan
    await page.click('button:has-text("Billing & Plan")');
    await expect(page.locator('text=Your Plan')).toBeVisible();
    
    // Click General
    await page.click('button:has-text("General")');
    await expect(page.locator('text=Upload Preferences')).toBeVisible();
});
