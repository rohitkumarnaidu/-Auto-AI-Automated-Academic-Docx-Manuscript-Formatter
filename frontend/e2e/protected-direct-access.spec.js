import { test, expect } from '@playwright/test';

test('protected route direct access redirect', async ({ page }) => {
    // Access /edit (requires job in context)
    await page.goto('/edit');
    
    // Should redirect to upload if no job
    await expect(page).toHaveURL(/\/(upload|login)/);
});
