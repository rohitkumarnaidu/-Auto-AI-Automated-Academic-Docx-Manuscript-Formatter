import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
    test('landing page loads with hero section', async ({ page }) => {
        await page.goto('/');
        await expect(page).toHaveTitle(/Automated Academic Manuscript Formatter/i);

        const heading = page.locator('h1').first();
        await expect(heading).toBeVisible();
    });

    test('landing page has navigation to login and signup', async ({ page }) => {
        await page.goto('/');

        const loginLink = page.getByRole('link', { name: /Sign In|Login/i }).first();
        await expect(loginLink).toBeVisible();

        const signupLink = page.getByRole('link', { name: /Sign Up|Get Started/i }).first();
        await expect(signupLink).toBeVisible();
    });
});
