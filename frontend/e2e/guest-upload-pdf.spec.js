import { test, expect } from '@playwright/test';
import path from 'path';

test('guest upload flow -> PDF', async ({ page }) => {
    // 1. Go to homepage
    await page.goto('/');
    
    // 2. Click "Formatter: Upload Manuscript"
    await page.click('a:has-text("Formatter: Upload Manuscript")');
    
    // 3. Confirm redirected to /upload
    await expect(page).toHaveURL(/\/upload\?guest=1/);
    
    // 4. Create dummy PDF (or use sample as .pdf if backend allows)
    // For E2E, we'll use a sample.docx but simulate PDF download if we can
    // Or just upload our sample file as if it's a PDF for UI testing
    const filePath = path.resolve('e2e/test-files/sample.docx');
    await page.setInputFiles('#file-upload', filePath);
    
    await expect(page.locator('text=File selected')).toBeVisible();
    
    // 5. Click "Process Document"
    await page.click('button:has-text("Process Document")');
    
    // 6. Wait for redirect to /download
    await page.waitForURL(/\/download/, { timeout: 30000 });
    
    // 7. Click "Choose Export Format"
    await page.click('button:has-text("Choose Export Format")');
    
    // 8. Wait for PDF option (if ExportDialog has it)
    // Assuming ExportDialog shows formats
    await expect(page.locator('text=PDF')).toBeVisible();
});