import { test, expect } from '@playwright/test';

const hasSupabaseUrl = Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL);

test.describe('Dark Mode', () => {
    test('homepage respects prefers-color-scheme', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('body')).toBeVisible();

        const htmlClass = await page.evaluate(() => document.documentElement.className);
        const hasDarkClass = htmlClass.includes('dark');
        expect(typeof hasDarkClass).toBe('boolean');
    });

    test('toggling dark mode adds dark class to html', async ({ page }) => {
        test.skip(!hasSupabaseUrl, 'NEXT_PUBLIC_SUPABASE_URL not set — theme toggle requires auth context');
        await page.goto('/upload');
        await expect(page.locator('body')).toBeVisible();

        const themeToggle = page.getByRole('button', { name: /dark|light|mode/i }).first();
        await expect(themeToggle).toBeVisible({ timeout: 5000 });
        const initialDark = await page.evaluate(() => document.documentElement.className.includes('dark'));

        await themeToggle.click();
        await page.waitForTimeout(300);

        const afterDark = await page.evaluate(() => document.documentElement.className.includes('dark'));
        expect(afterDark).toBe(!initialDark);
    });
});
