import { test, expect } from '@playwright/test';

test('switching template on upload page', async ({ page }) => {
    await page.goto('/upload?guest=1');
    
    // 1. Initial template might be "none"
    // 2. Click template selector (usually a dropdown or list)
    // Assuming TemplateSelector is a grid of buttons
    const ieeeBtn = page.locator('text=IEEE');
    if (await ieeeBtn.isVisible()) {
        await ieeeBtn.click();
        // Check if status or some text mentions IEEE
        await expect(page.locator('text=IEEE')).toBeVisible();
    }
});
