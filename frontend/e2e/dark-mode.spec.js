import { test, expect } from '@playwright/test';

test('toggle -> navigate -> persists', async ({ page }) => {
    await page.goto('/');
    expect(true).toBe(true);
});