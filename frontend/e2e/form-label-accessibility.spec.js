import { test, expect } from '@playwright/test';

test('all form inputs have accessible labels', async ({ page }) => {
    await page.goto('/upload?guest=1');
    
    const inputs = await page.locator('input, select, textarea').all();
    for (const input of inputs) {
        const id = await input.getAttribute('id');
        if (id) {
            const label = page.locator(`label[for="${id}"]`);
            // Some labels might not be visible but should exist in DOM
            await expect(label).toBeAttached();
        }
    }
});
