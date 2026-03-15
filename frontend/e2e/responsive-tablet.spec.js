import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 1024, height: 768 } });

test('tablet view layout', async ({ page }) => {
    await page.goto('/');
    
    // On tablet, we might have either hamburger or full nav depending on breakpoints
    // Typically lg (1024px) shows full nav
    const desktopLinks = page.locator('header >> .hidden.lg\\:flex');
    await expect(desktopLinks).toBeVisible();
});