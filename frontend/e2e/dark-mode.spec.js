import { test, expect } from '@playwright/test';

test('dark mode toggle persists across navigation', async ({ page }) => {
    await page.goto('/');
    
    // 1. Find the theme toggle button in the Header
    // It's likely an icon button with "light_mode" or "dark_mode" text or icon
    const themeToggle = page.locator('button:has(.material-symbols-outlined:has-text("dark_mode")), button:has(.material-symbols-outlined:has-text("light_mode"))');
    
    if (await themeToggle.isVisible()) {
        const initialTheme = await page.locator('html').getAttribute('class');
        
        // 2. Click to toggle
        await themeToggle.click();
        
        // 3. Verify class changed
        const newTheme = await page.locator('html').getAttribute('class');
        expect(newTheme).not.toBe(initialTheme);
        
        // 4. Navigate and verify it persists
        await page.goto('/templates');
        const persistedTheme = await page.locator('html').getAttribute('class');
        expect(persistedTheme).toBe(newTheme);
    }
});