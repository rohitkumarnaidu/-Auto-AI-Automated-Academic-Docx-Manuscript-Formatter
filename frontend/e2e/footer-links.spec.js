import { test, expect } from '@playwright/test';

test('footer links navigation', async ({ page }) => {
    await page.goto('/');
    
    await page.locator('footer >> text=Terms').click();
    await expect(page).toHaveURL(/\/terms/);
    
    await page.goto('/');
    await page.locator('footer >> text=Privacy').click();
    await expect(page).toHaveURL(/\/privacy/);
});
