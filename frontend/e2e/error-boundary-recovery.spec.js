import { test, expect } from '@playwright/test';

test('error boundary recovery', async ({ page }) => {
    await page.goto('/error');
    
    const returnHome = page.locator('text=Return to Home');
    await returnHome.click();
    
    await expect(page).toHaveURL('/');
});
