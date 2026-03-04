import { expect, test } from '@playwright/test';

test.describe('Routes and Navbar Parity', () => {
    test('guest navbar on formatter pages shows expected app links', async ({ page }) => {
        await page.goto('/upload');

        await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Upload' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Templates' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Template Editor' })).toBeVisible();
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
