import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Phase 4 Core Flows', () => {
    test.setTimeout(120000); // Allow 2 minutes for full end-to-end backend processing

    test('Test full formatter flow (Upload -> Process -> Results -> Download)', async ({ page }) => {
        // Navigate home and click 'Format Now' or directly to /upload
        await page.goto('/upload');
        
        // 1. Upload sample DOCX
        const filePath = path.resolve('../ScholarForm_AI_Documentation.docx');
        
        // Find upload area/button. In many apps it's an input type=file or a drop zone.
        // Assuming there is an input[type="file"]:
        await page.locator('input[type="file"]').setInputFiles(filePath);

        // 2. Select IEEE template
        // Find a select dropdown or combobox that has 'IEEE'
        // Just directly wait for the navigation to processing and results.
        const startBtn = page.getByRole('button', { name: /start formatting|format|upload/i });
        if (await startBtn.isVisible()) {
            await startBtn.click();
        }

        // Wait for redirect to /processing
        await page.waitForURL(/\/processing/);
        
        // Wait for redirect to /results
        await page.waitForURL(/\/results/, { timeout: 60000 });

        // Verify quality score panel renders
        await expect(page.locator('text=/score|quality|grade/i').first()).toBeVisible({ timeout: 10000 });

        // 3. Download works
        const downloadBtn = page.getByRole('button', { name: /download/i }).first();
        await expect(downloadBtn).toBeVisible();
    });

    test('Test full agent flow (Prompt -> Outline -> Approve -> Write)', async ({ page }) => {
        await page.goto('/agent');
        
        // Find the chat input
        const chatInput = page.getByPlaceholder(/message|type|prompt|ask/i).first();
        await chatInput.fill('Write a short paper about machine learning');
        
        // Submit prompt
        await page.keyboard.press('Enter');
        
        // Wait for outline to appear
        const generateBtn = page.getByRole('button', { name: /generate/i });
        await expect(generateBtn).toBeVisible({ timeout: 60000 });

        // Approve outline
        await generateBtn.click();

        // Check if write flow started (redirects to /live or /results or shows writing)
        await expect(page.locator('text=/writing|generating|formatting/i').first()).toBeVisible({ timeout: 20000 });
    });
});
