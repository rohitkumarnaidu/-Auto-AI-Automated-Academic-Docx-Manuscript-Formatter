import { test, expect } from '@playwright/test';

test('header shadow on scroll', async ({ page }) => {
    await page.goto('/');
    
    // Initial state: no shadow or transparent
    const header = page.locator('header').first();
    
    // Scroll down
    await page.mouse.wheel(0, 500);
    
    // Check for shadow class or style
    await expect(header).toHaveClass(/shadow/);
});
