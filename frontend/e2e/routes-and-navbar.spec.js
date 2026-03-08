import { expect, test } from '@playwright/test';

test.describe('Routes and Navbar Parity', () => {
    test('guest formatter app shell exposes sidebar navigation links', async ({ page }) => {
        await page.goto('/upload');

        const sidebarNavItem = (label) =>
            page.locator(`nav button[title="${label}"], nav button:has-text("${label}")`).first();

        await expect(sidebarNavItem('Upload')).toBeVisible();
        await expect(sidebarNavItem('Templates')).toBeVisible();
        await expect(sidebarNavItem('Template Editor')).toBeVisible();
    });

    test('protected generator and admin routes redirect guests to login with next', async ({ page }) => {
        await page.goto('/generate');
        await expect(page).toHaveURL(/\/login\?next=%2Fgenerate/);

        await page.goto('/admin-dashboard');
        await expect(page).toHaveURL(/\/login\?next=%2Fadmin-dashboard/);
    });

    test('invalid job step returns native 404', async ({ page }) => {
        await page.goto('/jobs/abc123/invalid-step');
        await expect(page).toHaveURL('/jobs/abc123/invalid-step');
        await expect(page.getByRole('heading', { name: '404' })).toBeVisible();
        await expect(page.getByRole('heading', { name: 'Page Not Found' })).toBeVisible();
    });
});
