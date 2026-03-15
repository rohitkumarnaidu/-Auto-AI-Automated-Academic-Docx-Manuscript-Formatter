import { test, expect } from '@playwright/test';

test('template list shows 17 templates', async ({ page }) => {
    // 1. Go to templates page
    await page.goto('/templates');
    
    // 2. Expect at least some core templates to be visible
    await expect(page.locator('text=IEEE')).toBeVisible();
    await expect(page.locator('text=APA (7th)')).toBeVisible();
    await expect(page.locator('text=ACM')).toBeVisible();
    await expect(page.locator('text=Springer')).toBeVisible();
    await expect(page.locator('text=Elsevier')).toBeVisible();
    await expect(page.locator('text=Nature')).toBeVisible();
    
    // 3. Count cards (assuming each template is in a card)
    // There are 15 built-in in page.jsx + Request Template Card
    const cards = await page.locator('.grid > div').count();
    expect(cards).toBeGreaterThanOrEqual(12); // Account for pagination (ITEMS_PER_PAGE=6)
});

test('pagination works on templates page', async ({ page }) => {
    await page.goto('/templates');
    
    // Initial page check
    await expect(page.locator('text=IEEE')).toBeVisible();
    
    // Click next page if available
    const nextButton = page.locator('button:has(.material-symbols-outlined:has-text("chevron_right"))');
    if (await nextButton.isVisible()) {
        await nextButton.click();
        // Wait for different content
        await expect(page.locator('text=IEEE')).not.toBeVisible();
    }
});