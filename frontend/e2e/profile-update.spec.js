import { test, expect } from '@playwright/test';

test.describe('Profile Update', () => {
    test('profile page loads with editable fields', async ({ page }) => {
        await page.goto('/profile');
        await expect(page.locator('body')).toBeVisible();

        const heading = page.getByRole('heading', { name: /Account Settings/i });
        await expect(heading).toBeVisible();

        const editButton = page.getByRole('button', { name: /Edit Profile/i });
        await expect(editButton).toBeVisible();
    });
});
