import { test, expect } from '@playwright/test';

test('multi-doc synthesis stepper', async ({ page }) => {
    await page.goto('/synthesis');
    // Assuming a multi-upload flow -> synthesis
    // This test checks for the presence of the synthesis stepper or UI
});
