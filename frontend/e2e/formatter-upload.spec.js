import { test, expect } from '@playwright/test';

test.describe('Formatter Upload', () => {
    test('upload page loads with manuscript upload heading', async ({ page }) => {
        await page.goto('/upload', { waitUntil: 'domcontentloaded', timeout: 15000 });

        const heading = page.getByRole('heading', { name: /Upload Manuscript/i });
        await expect(heading).toBeVisible();

        const fileInput = page.locator('input[type="file"]');
        await expect(fileInput).toBeAttached();

        const browseButton = page.getByRole('button', { name: /Browse Files/i });
        await expect(browseButton).toBeVisible();
    });
});
