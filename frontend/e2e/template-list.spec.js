import { test, expect } from '@playwright/test';

test.describe('Template List', () => {
    test('template list page loads with available templates', async ({ page }) => {
        await page.goto('/templates');
        await expect(page.locator('body')).toBeVisible();

        const heading = page.getByRole('heading', { name: /template/i });
        await expect(heading).toBeVisible();
    });
});
