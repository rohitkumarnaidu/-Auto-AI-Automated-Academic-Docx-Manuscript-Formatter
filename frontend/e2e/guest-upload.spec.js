import { test, expect } from '@playwright/test';
import path from 'path';

test('guest upload flow -> DOCX', async ({ page }) => {
    // 1. Go to homepage
    await page.goto('/');
    
    // 2. Click "Formatter: Upload Manuscript"
    // Expecting: <Link href="/upload?guest=1">...</Link>
    await page.click('a:has-text("Formatter: Upload Manuscript")');
    
    // 3. Confirm redirected to /upload
    await expect(page).toHaveURL(/\/upload\?guest=1/);
    
    // 4. Upload file
    const filePath = path.resolve('e2e/test-files/sample.docx');
    await page.setInputFiles('#file-upload', filePath);
    
    // 5. Wait for "File selected" text or checkmark
    await expect(page.locator('text=File selected')).toBeVisible();
    
    // 6. Start processing
    // Button text is "Process Document" initially
    await page.click('button:has-text("Process Document")');
    
    // 7. Wait for processing to complete and redirect to /download
    // We expect the URL to change to /download or a processing status message to appear
    // Since processing might take time, we wait for the "Formatting Complete!" title on the next page
    await page.waitForURL(/\/download/, { timeout: 30000 });
    
    // 8. Verify success on download page
    await expect(page.locator('h1')).toContainText('Formatting Complete!');
    
    // 9. Verify download button is present
    await expect(page.locator('button:has-text("Choose Export Format")')).toBeVisible();
});