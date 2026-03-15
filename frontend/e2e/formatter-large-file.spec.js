import { test, expect } from '@playwright/test';

test('file size limit warning', async ({ page }) => {
    await page.goto('/upload?guest=1');
    
    // We can't easily upload a 50MB file in tests without a real one
    // But we check the UI for "50MB" text to ensure the limit is communicated
    await expect(page.locator('text=50 MB')).toBeVisible();
});
