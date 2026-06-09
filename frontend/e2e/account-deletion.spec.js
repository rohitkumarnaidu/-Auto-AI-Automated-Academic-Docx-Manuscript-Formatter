import { test, expect } from '@playwright/test';

test.describe('Account Deletion', () => {
    test('profile page loads with account action elements', async ({ page }) => {
        await page.goto('/profile');
        await expect(page.locator('body')).toBeVisible();

        const heading = page.getByRole('heading', { name: /Account Settings/i });
        await expect(heading).toBeVisible();

        const signOutButton = page.getByRole('button', { name: /Sign out/i });
        await expect(signOutButton).toBeVisible();
    });
});
