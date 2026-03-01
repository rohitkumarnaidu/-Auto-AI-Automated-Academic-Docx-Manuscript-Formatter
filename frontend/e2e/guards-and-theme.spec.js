import { expect, test } from '@playwright/test';

test.describe('Guards and Theme', () => {
    test('guest is redirected to login with next parameter for protected routes', async ({ page }) => {
        await page.goto('/dashboard');
        await expect(page).toHaveURL(/\/login\?next=%2Fdashboard/);
        await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
    });

    test('global header theme toggle switches root theme class', async ({ page }) => {
        await page.goto('/');

        const html = page.locator('html');
        await expect(html).toHaveClass(/light/);

        const themeToggle = page.getByRole('button', { name: /Switch to (dark|light) mode/i });
        await themeToggle.click();

        await expect(html).toHaveClass(/dark/);
        await expect(page.getByLabel('Formatter Mode')).toHaveCount(0);
    });
});
