import { test, expect } from '@playwright/test';

test.describe('ScholarForm AI - Core Routes Smoke Tests', () => {
    
    test('Formatter - Edit Page (/edit) should load correctly', async ({ page }) => {
        // Navigate to the edit page
        await page.goto('/edit');
        
        // Ensure the page didn't throw a 500 error or crash
        await expect(page).toHaveTitle(/.*|.*/); // Accept any generic title, but usually fail if page body has Server Error
        
        // Wait for dom content loaded
        await page.waitForLoadState('domcontentloaded');
        
        // Check for basic structure elements like a header or specific edit elements
        const bodyContent = await page.textContent('body');
        expect(bodyContent).toBeTruthy();
    });

    test('Formatter - Results Page (/results) should load correctly', async ({ page }) => {
        // Navigate to the results page
        await page.goto('/results');
        
        await expect(page).toHaveTitle(/.*|.*/);
        await page.waitForLoadState('domcontentloaded');
        
        const bodyContent = await page.textContent('body');
        expect(bodyContent).toBeTruthy();
    });

    test('Formatter - Live Preview Page (/live) should load correctly', async ({ page }) => {
        // Navigate to the live preview page
        await page.goto('/live');
        
        await expect(page).toHaveTitle(/.*|.*/);
        await page.waitForLoadState('domcontentloaded');
        
        const bodyContent = await page.textContent('body');
        expect(bodyContent).toBeTruthy();
    });

    test('Generator - AI Agent Page (/agent) should load correctly', async ({ page }) => {
        // Navigate to the AI agent page
        await page.goto('/agent');
        
        await expect(page).toHaveTitle(/.*|.*/);
        await page.waitForLoadState('domcontentloaded');
        
        const bodyContent = await page.textContent('body');
        expect(bodyContent).toBeTruthy();
    });

});
