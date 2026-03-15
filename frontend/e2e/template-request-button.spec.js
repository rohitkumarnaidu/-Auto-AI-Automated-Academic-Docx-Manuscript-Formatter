import { test, expect } from '@playwright/test';

test('request template card link', async ({ page }) => {
    await page.goto('/templates');
    
    const requestCard = page.locator('text=Request Template');
    await expect(requestCard).toBeVisible();
    
    // It should open a mailto or a form
    // await requestCard.click();
});
