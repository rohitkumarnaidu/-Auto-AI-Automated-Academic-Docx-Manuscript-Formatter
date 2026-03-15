import { test, expect } from '@playwright/test';

test('onboarding tour triggers on first visit', async ({ page }) => {
    await page.goto('/upload?onboarding=true');
    
    // Check for Shepherd or Driver.js tour elements
    // Usually they have specific classes like .shepherd-element or .driver-popover
    const tour = page.locator('.shepherd-element, .driver-popover-item, div:has-text("Step 1")');
    await expect(tour).toBeVisible().catch(() => {
        // Fallback check for any overlay that looks like a tour
        const overlay = page.locator('div[style*="z-index"]:has-text("Welcome")');
        return expect(overlay).toBeVisible();
    });
});
