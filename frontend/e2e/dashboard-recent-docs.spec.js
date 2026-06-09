import { test, expect } from '@playwright/test';

test.describe('Dashboard Recent Docs', () => {
    test('dashboard page loads with heading', async ({ page }) => {
        await page.goto('/dashboard');
        await expect(page.locator('body')).toBeVisible();

        const heading = page.getByRole('heading', { name: /dashboard/i });
        await expect(heading).toBeVisible();
    });
});
