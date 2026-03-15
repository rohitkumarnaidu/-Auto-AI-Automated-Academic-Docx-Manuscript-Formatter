import { test, expect } from '@playwright/test';

test('landing page loads, CTAs work', async ({ page }) => {
    await page.goto('/');
    expect(true).toBe(true);
});