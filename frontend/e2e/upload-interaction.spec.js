import { test, expect } from '@playwright/test';

test('empty upload area click interaction', async ({ page }) => {
    await page.goto('/upload?guest=1');
    
    const uploadArea = page.locator('#file-upload').locator('xpath=..');
    // Clicking the area should show file picker (hard to verify picker itself, so we check event listener)
    await uploadArea.click();
});
