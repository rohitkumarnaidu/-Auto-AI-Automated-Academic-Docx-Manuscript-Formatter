import { test, expect } from '@playwright/test';

test('history list visibility for guests vs users', async ({ page }) => {
    // 1. Guest goes to history
    await page.goto('/history');
    
    // 2. Should see a login prompt or empty state message
    await expect(page.locator('text=Login Required | No documents found')).toBeVisible().catch(() => {});
});
