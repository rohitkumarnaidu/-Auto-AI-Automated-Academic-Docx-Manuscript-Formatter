import { test, expect } from '@playwright/test';

test.describe('Dark Mode', () => {
    test('homepage loads and theme toggle is present', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('body')).toBeVisible();

        const themeToggle = page.getByRole('button', { name: /theme|dark|light|mode/i }).first();
        await expect(themeToggle).toBeVisible();
    });

    test('toggling dark mode adds dark class to html', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('body')).toBeVisible();

        const themeToggle = page.getByRole('button', { name: /theme|dark|light|mode/i }).first();
        if (await themeToggle.isVisible()) {
            await themeToggle.click();
            await page.waitForTimeout(300);

            const htmlClass = await page.evaluate(() => document.documentElement.className);
            expect(htmlClass).toMatch(/dark/);
        }
    });
});
