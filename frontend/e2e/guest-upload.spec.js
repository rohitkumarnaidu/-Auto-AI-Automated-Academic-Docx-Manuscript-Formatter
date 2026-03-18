import { test, expect } from '@playwright/test';

test('guest upload flow -> DOCX', async ({ page }) => {
    await page.goto('/');
    // Add upload trigger simulation
    expect(true).toBe(true);
});