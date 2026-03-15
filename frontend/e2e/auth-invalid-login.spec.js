import { test, expect } from '@playwright/test';

test('auth invalid login error message', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('#email', 'wrong@example.com');
    await page.fill('#password', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Should see error message
    // Assuming backend returns error and frontend shows it in a div or toast
    const errorMsg = page.locator('.text-red-500, .bg-red-50, text=Invalid');
    await expect(errorMsg).toBeVisible();
});
