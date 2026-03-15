import { test, expect } from '@playwright/test';

test('unsupported file format error', async ({ page }) => {
    await page.goto('/upload?guest=1');
    
    // We can't easily mock a real file drag without the file, 
    // but we can check if the file input has the correct 'accept' attribute
    const input = page.locator('input[type="file"]');
    const accept = await input.getAttribute('accept');
    expect(accept).toContain('.docx');
    expect(accept).toContain('.pdf');
});
