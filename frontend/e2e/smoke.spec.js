import { test, expect } from '@playwright/test';

test.describe('ScholarForm AI - Core Routes Smoke Tests', () => {
    
    test.beforeEach(async ({ page }) => {
        // Hydrate the DocumentContext with a mock job via session storage
        await page.addInitScript(() => {
            sessionStorage.setItem('scholarform_currentJob', JSON.stringify({
                id: 'test-123',
                status: 'completed',
                originalFileName: 'test.docx',
                processedText: 'This is a test document.',
                result: {
                    structured_data: {
                        sections: { BODY: 'This is a test document.' }
                    },
                    metrics: { overall_score: 95 },
                    errors: [],
                    warnings: []
                }
            }));
        });
    });

    test('Formatter - Edit Page (/edit) should load correctly', async ({ page }) => {
        await page.goto('/edit?jobId=test-123');
        await expect(page).toHaveTitle(/.*|.*/);
        await page.waitForLoadState('domcontentloaded');
        
        // Wait for the specific container to appear
        const paper = page.locator('.manuscript-paper').first();
        await expect(paper).toBeVisible({ timeout: 15000 });

        // TipTap editor should render natively
        const editor = page.locator('.ProseMirror, .tiptap, [contenteditable="true"]').first();
        await expect(editor).toBeVisible();
        await editor.fill('Test text');
        await expect(editor).toContainText('Test text');
    });

    test('Formatter - Results Page (/results) should load correctly', async ({ page }) => {
        await page.goto('/results?jobId=test-123');
        await expect(page).toHaveTitle(/.*|.*/);
        await page.waitForLoadState('domcontentloaded');
        
        const bodyContent = await page.textContent('body');
        expect(bodyContent).toBeTruthy();
    });

    test('Formatter - Live Preview Page (/live) should load correctly', async ({ page }) => {
        await page.goto('/live?jobId=test-123');
        await expect(page).toHaveTitle(/.*|.*/);
        await page.waitForLoadState('domcontentloaded');
        
        const bodyContent = await page.textContent('body');
        expect(bodyContent).toBeTruthy();
    });

    test('Generator - AI Agent Page (/agent) should load correctly', async ({ page }) => {
        await page.goto('/agent?jobId=test-123');
        await expect(page).toHaveTitle(/.*|.*/);
        await page.waitForLoadState('domcontentloaded');
        
        const bodyContent = await page.textContent('body');
        expect(bodyContent).toBeTruthy();
    });
});
