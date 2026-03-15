import { test, expect } from '@playwright/test';

test('unauthenticated access -> redirect to login with next param', async ({ page }) => {
    // 1. Try to access dashboard
    await page.goto('/dashboard');
    
    // 2. Should be redirected to /login with next=%2Fdashboard
    await expect(page).toHaveURL(/\/login\?next=%2Fdashboard/);
    
    // 3. Try to access settings
    await page.goto('/settings');
    await expect(page).toHaveURL(/\/login\?next=%2Fsettings/);
});