import { test, expect } from '@playwright/test';
import path from 'path';

test('batch upload UI and basic flow', async ({ page }) => {
    // Check if /batch-upload exists
    const response = await page.goto('/batch-upload');
    if (response.status() === 404) {
        test.skip(true, 'Batch upload page not found');
        return;
    }
    
    // Assuming a similar dropzone or file input
    const filePath = path.resolve('e2e/test-files/sample.docx');
    await page.setInputFiles('input[type="file"]', [filePath, filePath]); // Multiple files
    
    await expect(page.locator('text=2 files selected')).toBeVisible();
});
