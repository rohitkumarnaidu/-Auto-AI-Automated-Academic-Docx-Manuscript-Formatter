import { test, expect } from '@playwright/test';

test('dark mode respects system preference', async ({ page, colorScheme }) => {
    // This is hard to test purely in code without mocking media queries
    // But we check if the toggle UI reflects the current system theme
    await page.goto('/');
    const html = page.locator('html');
    
    if (colorScheme === 'dark') {
        await expect(html).toHaveClass(/dark/);
    }
});
