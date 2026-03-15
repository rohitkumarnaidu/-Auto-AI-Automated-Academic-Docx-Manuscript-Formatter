import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 812 } });

test('mobile upload UI sanity check', async ({ page }) => {
    await page.goto('/upload?guest=1');
    
    // Ensure the upload area isn't dwarfed or hidden
    const uploadArea = page.locator('#file-upload').locator('xpath=..');
    await expect(uploadArea).toBeVisible();
    
    // Check for "Process Document" button at the bottom
    await expect(page.locator('button:has-text("Process Document")')).toBeVisible();
});
