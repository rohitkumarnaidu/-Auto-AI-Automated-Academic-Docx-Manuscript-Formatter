import { test, expect } from '@playwright/test';

test('billing tier badge in settings', async ({ page }) => {
    await page.goto('/settings?tab=billing');
    
    // Check for "Free Plan" or "Pro Plan" badge
    const badge = page.locator('.px-3.py-1.text-sm.font-semibold.rounded-full');
    await expect(badge).toBeVisible();
    await expect(badge).toContainText(/Plan/);
});
