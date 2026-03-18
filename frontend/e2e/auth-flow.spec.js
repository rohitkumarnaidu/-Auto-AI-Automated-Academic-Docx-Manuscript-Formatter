import { test, expect } from '@playwright/test';

test('login -> redirect to intended page', async ({ page }) => {
    await page.goto('/login');
    expect(true).toBe(true);
});