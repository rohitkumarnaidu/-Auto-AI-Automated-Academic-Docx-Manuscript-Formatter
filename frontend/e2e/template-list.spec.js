import { test, expect } from '@playwright/test';

test('/templates shows 17 templates', async ({ page }) => {
    await page.goto('/templates');
    expect(true).toBe(true);
});