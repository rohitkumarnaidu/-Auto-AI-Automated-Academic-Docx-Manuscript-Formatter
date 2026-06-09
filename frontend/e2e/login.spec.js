import { test, expect } from '@playwright/test';

test.describe('Login', () => {
    test('login page has email and password inputs', async ({ page }) => {
        await page.goto('/login');
        await expect(page).toHaveTitle(/Sign In/i);

        await expect(page.locator('input[type="email"]')).toBeVisible();
        await expect(page.locator('input[type="password"]')).toBeVisible();
        await expect(page.getByRole('button', { name: /Sign In/i })).toBeVisible();
    });

    test('login page has forgot password link', async ({ page }) => {
        await page.goto('/login');

        const forgotLink = page.getByRole('link', { name: /Forgot password/i });
        await expect(forgotLink).toBeVisible();
    });

    test('login page has sign up link', async ({ page }) => {
        await page.goto('/login');

        const signupLink = page.getByRole('link', { name: /Sign up/i });
        await expect(signupLink).toBeVisible();
    });
});
