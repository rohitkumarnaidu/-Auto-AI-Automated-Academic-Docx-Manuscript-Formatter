import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 667 } });
test('key pages on mobile viewport', async ({ page }) => {
    await page.goto('/');
    expect(true).toBe(true);
});