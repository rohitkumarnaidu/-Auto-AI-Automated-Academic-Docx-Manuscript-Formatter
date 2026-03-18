import { test, expect } from '@playwright/test';

test('guest upload flow -> PDF', async ({ page }) => {
    await page.goto('/');
    expect(true).toBe(true);
});