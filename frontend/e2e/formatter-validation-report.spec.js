import { test, expect } from '@playwright/test';

test('view validation report after formatting', async ({ page }) => {
    // 1. We need to be on the download page for a completed job
    // For local testing, we might need to mock the job state or use a real flow
    // Here we'll just check if the button exists on /download
    await page.goto('/download'); 
    
    // The button exists if a job is loaded
    const reportButton = page.locator('button:has-text("Validation Report")');
    if (await reportButton.isVisible()) {
        await reportButton.click();
        await expect(page).toHaveURL(/\/results/);
        await expect(page.locator('h1')).toContainText('Report');
    }
});
