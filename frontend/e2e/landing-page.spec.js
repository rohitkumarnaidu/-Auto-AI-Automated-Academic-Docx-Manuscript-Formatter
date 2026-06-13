import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
    test('landing page loads with hero section', async ({ page }) => {
        await page.goto('/');
        await expect(page).toHaveTitle(/Automated Academic Manuscript Formatter/i);

        const heading = page.locator('h1').first();
        await expect(heading).toBeVisible();
    });

    test('landing page has hero CTA links to formatter and generator', async ({ page }) => {
        await page.goto('/');

        const formatterCta = page.getByRole('link', { name: /Upload Manuscript/i }).first();
        await expect(formatterCta).toBeVisible();

        const generatorCta = page.getByRole('link', { name: /Create Draft/i }).first();
        await expect(generatorCta).toBeVisible();
    });
});
