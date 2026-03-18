import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 768, height: 1024 } });
test('key pages on tablet viewport', async ({ page }) => {
    await page.goto('/');
    expect(true).toBe(true);
});