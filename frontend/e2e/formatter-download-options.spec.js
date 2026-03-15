import { test, expect } from '@playwright/test';

test('download format options visibility', async ({ page }) => {
    await page.goto('/download');
    
    const exportButton = page.locator('button:has-text("Choose Export Format")');
    if (await exportButton.isVisible()) {
        await exportButton.click();
        
        // ExportDialog should show options
        await expect(page.locator('text=Word Document (.docx)')).toBeVisible();
        await expect(page.locator('text=PDF Document (.pdf)')).toBeVisible();
    }
});
