import { expect, test } from '@playwright/test';

test.describe('Template System', () => {
    test('templates page renders full built-in library and accessible preview dialog', async ({ page }) => {
        await page.goto('/templates');

        await expect(
            page.getByRole('heading', { name: 'Journal Template Library' })
        ).toBeVisible();

        await expect(page.getByText('IEEE')).toBeVisible();
        await expect(page.getByText('Modern Red')).toBeVisible();
        await expect(page.getByRole('button', { name: '3' })).toBeVisible();

        await page.getByRole('button', { name: 'Preview Guidelines' }).first().click();
        await expect(page.getByRole('dialog')).toBeVisible();
        await page.keyboard.press('Escape');
        await expect(page.getByRole('dialog')).not.toBeVisible();
    });

    test('upload template selector exposes all 15 templates', async ({ page }) => {
        await page.goto('/upload');
        await expect(page.getByText('Select Template')).toBeVisible();

        const templateSelect = page.locator('select').first();
        await expect(templateSelect.locator('option')).toHaveCount(15);
        await expect(templateSelect.locator('option[value="springer"]')).toHaveText('Springer');
        await expect(templateSelect.locator('option[value="modern_blue"]')).toHaveText('Modern Blue');
        await expect(templateSelect.locator('option[value="modern_red"]')).toHaveText('Modern Red');
    });
});
