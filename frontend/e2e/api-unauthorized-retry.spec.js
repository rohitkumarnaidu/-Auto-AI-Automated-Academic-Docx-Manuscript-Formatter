import { test, expect } from '@playwright/test';

test('api unauthorized redirect flow', async ({ page }) => {
    // Navigate to a protected page directly
    await page.goto('/history');
    
    // Should be redirected to /login with next param
    await expect(page).toHaveURL(/\/login\?next=%2Fhistory/);
});
