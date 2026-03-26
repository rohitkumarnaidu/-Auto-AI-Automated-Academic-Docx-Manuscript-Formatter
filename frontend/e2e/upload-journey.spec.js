import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Upload -> Processing -> Download Journey (E2E-001)', () => {
  test('allows guest to upload, process, and see results', async ({ page }) => {
    // 1. Go to upload page
    await page.goto('/upload');
    
    // Ensure we are on the upload page
    await expect(page).toHaveURL(/.*\/upload/);

    // Provide a sample file to the dropzone file input
    const fileChooserPromise = page.waitForEvent('filechooser');
    // Click the dropzone to trigger the file chooser
    await page.locator('text="Click to browse"').click();
    const fileChooser = await fileChooserPromise;
    
    // Use the existing sample.docx
    const sampleFilePath = path.join(__dirname, 'test-files', 'sample.docx');
    await fileChooser.setFiles(sampleFilePath);

    // Wait and click format button
    await page.getByRole('button', { name: /format document/i }).click();

    // 2. Journey to Processing page
    await expect(page).toHaveURL(/.*\/processing/);
    
    // Wait for the text "Processing your document"
    await expect(page.getByText(/processing your document/i)).toBeVisible();

    // 3. Journey automatically moves to Results (this might take some time, increase timeout)
    await expect(page).toHaveURL(/.*\/results/, { timeout: 45000 });

    // Review Results page
    await expect(page.getByText(/quality score/i)).toBeVisible();
    
    // Click Download button
    await page.getByRole('button', { name: /download/i }).first().click();
    
    // Journey continues to Download options page
    await expect(page).toHaveURL(/.*\/download/);
    
    // Ensure download format options are visible
    await expect(page.getByText(/Export Options/i)).toBeVisible();
  });
});
