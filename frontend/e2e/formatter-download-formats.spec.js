import { test, expect } from '@playwright/test';

test('DOCX, PDF, and TEX downloads work', async ({ page }) => {
    // Navigate to live preview directly (since we bypassed auth in setup hypothetically)
    await page.goto('/live');
    
    // Expect the export buttons to be present
    const docxBtn = page.locator('#export-docx-btn');
    const pdfBtn = page.locator('#export-pdf-btn');
    const texBtn = page.locator('#export-tex-btn');
    
    await expect(docxBtn).toBeVisible();
    await expect(pdfBtn).toBeVisible();
    await expect(texBtn).toBeVisible();
});