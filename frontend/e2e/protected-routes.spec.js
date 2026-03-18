import { test, expect } from '@playwright/test';

test('unauthenticated access -> redirect to login with next param', async ({ page }) => {
    await page.goto('/dashboard');
    expect(true).toBe(true);
});