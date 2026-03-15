import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 812 } });

test('mobile view has visible hamburger menu', async ({ page }) => {
    await page.goto('/');
    
    // 1. Check hamburger menu visibility
    const hamburger = page.locator('button:has(.material-symbols-outlined:has-text("menu"))');
    await expect(hamburger).toBeVisible();
    
    // 2. Open menu
    await hamburger.click();
    
    // 3. Verify mobile links are visible
    // "Templates" or "API" should be in the mobile nav
    await expect(page.locator('nav >> text=Templates')).toBeVisible();
});

test('mobile view hides desktop navigation', async ({ page }) => {
    await page.goto('/');
    
    // Desktop navigation links usually have specific classes or are hidden on mobile
    // We expect the direct links in the header (outside hamburger) to be hidden
    // e.g. .hidden lg:flex
    const desktopLinks = page.locator('header >> .hidden.lg\\:flex');
    await expect(desktopLinks).not.toBeVisible();
});