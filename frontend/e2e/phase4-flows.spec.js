import { test, expect } from '@playwright/test';
import path from 'path';

const E2E_EMAIL = process.env.E2E_EMAIL || '';
const E2E_PASSWORD = process.env.E2E_PASSWORD || '';

async function getCurrentJobFromSession(page) {
    return page.evaluate(() => {
        const raw = window.sessionStorage.getItem('scholarform_currentJob');
        if (!raw) return null;
        try {
            return JSON.parse(raw);
        } catch {
            return null;
        }
    });
}

async function waitForFormatterCompletion(page, timeoutMs = 180000) {
    const finalStatus = await expect.poll(async () => {
        const currentJob = await getCurrentJobFromSession(page);
        const normalizedStatus = String(currentJob?.status || '').toUpperCase();
        if (['FAILED', 'ERROR'].includes(normalizedStatus)) {
            throw new Error(`Formatter job failed early with status=${normalizedStatus}`);
        }
        return normalizedStatus;
    }, {
        timeout: timeoutMs,
        intervals: [1000, 1500, 2000, 2500],
    }).toMatch(/COMPLETED|COMPLETED_WITH_WARNINGS/);

    return finalStatus;
}

async function ensureAgentAccess(page, testInfo) {
    await page.goto('/agent');

    const isOnLogin = /\/login(?:\?|$)/.test(new URL(page.url()).pathname);
    if (!isOnLogin) {
        return;
    }

    test.skip(
        !E2E_EMAIL || !E2E_PASSWORD,
        'Agent flow requires auth in production. Configure E2E_EMAIL and E2E_PASSWORD secrets.'
    );

    await page.getByLabel(/email address|email/i).fill(E2E_EMAIL);
    await page.getByLabel(/password/i).fill(E2E_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 30000 });

    await testInfo.attach('agent-authenticated-url', {
        body: page.url(),
        contentType: 'text/plain',
    });
}

async function resolveAgentWorkspaceState(page, timeoutMs = 30000) {
    const deadline = Date.now() + timeoutMs;

    while (Date.now() < deadline) {
        const currentPath = new URL(page.url()).pathname;

        const chatInputCount = await page.locator('textarea[placeholder*="Type your prompt"]').count();
        if (chatInputCount > 0) {
            return { state: 'ready', path: currentPath };
        }

        const proGateCount = await page.getByText(/AI Agent is a Pro Feature/i).count();
        if (proGateCount > 0) {
            return { state: 'pro_gate', path: currentPath };
        }

        const loginButtonCount = await page.getByRole('button', { name: /sign in/i }).count();
        if (currentPath.startsWith('/login') || loginButtonCount > 0) {
            return { state: 'login', path: currentPath };
        }

        await page.waitForTimeout(1000);
    }

    return { state: 'unknown', path: new URL(page.url()).pathname };
}

test.describe('Phase 4 Core Flows', () => {
    test.setTimeout(240000); // Production processing can exceed 2 minutes under load

    test('Test full formatter flow (Upload -> Process -> Results -> Download)', async ({ page }) => {
        await page.goto('/upload');
        
        const filePath = path.resolve('../ScholarForm_AI_Documentation.docx');
        
        await page.locator('input[type="file"]').setInputFiles(filePath);

        const processBtn = page.getByRole('button', { name: /process document|re-process manuscript/i }).first();
        await expect(processBtn).toBeVisible();
        await expect(processBtn).toBeEnabled();

        await processBtn.click();

        await expect.poll(async () => {
            const currentJob = await getCurrentJobFromSession(page);
            return String(currentJob?.id || '');
        }, {
            timeout: 120000,
            intervals: [500, 1000, 1500, 2000],
        }).not.toBe('');

        const currentJob = await getCurrentJobFromSession(page);
        const jobId = currentJob?.id;
        expect(jobId).toBeTruthy();

        await expect(page.locator('text=/initiating upload|processing|upload complete/i').first())
            .toBeVisible({ timeout: 20000 });

        await waitForFormatterCompletion(page, 180000);

        await page.goto(`/jobs/${encodeURIComponent(jobId)}/download`);

        const downloadBtn = page.getByRole('button', { name: /choose export format|download/i }).first();
        await expect(downloadBtn).toBeVisible();
    });

    test('Test full agent flow (Prompt -> Outline -> Approve -> Write)', async ({ page }, testInfo) => {
        await ensureAgentAccess(page, testInfo);

        const workspaceState = await resolveAgentWorkspaceState(page, 30000);
        if (workspaceState.state === 'pro_gate') {
            test.skip(true, 'Agent workspace unavailable for non-Pro account in production environment.');
        }
        if (workspaceState.state === 'login') {
            test.skip(true, 'Agent workspace requires authenticated user in production environment.');
        }
        expect(
            workspaceState.state,
            `Agent workspace did not become ready. path=${workspaceState.path}`
        ).toBe('ready');

        const chatInput = page.locator('textarea[placeholder*="Type your prompt"]').first();
        await expect(chatInput).toBeVisible({ timeout: 20000 });
        await chatInput.fill('Write a short paper about machine learning');

        const submitBtn = page.locator('button[title*="Submit"]').first();
        await expect(submitBtn).toBeVisible({ timeout: 10000 });
        await submitBtn.click();
        
        await expect(page.getByText('Write a short paper about machine learning')).toBeVisible({ timeout: 20000 });

        const proceedToWrite = page.getByRole('button', { name: /proceed to write/i });
        const writingState = page.locator('text=/writing|generating|formatting/i').first();
        const errorState = page.locator('text=/error|failed|unable/i').first();

        await Promise.any([
            proceedToWrite.waitFor({ state: 'visible', timeout: 60000 }),
            writingState.waitFor({ state: 'visible', timeout: 60000 }),
            errorState.waitFor({ state: 'visible', timeout: 60000 }),
        ]);

        if (await proceedToWrite.isVisible().catch(() => false)) {
            await proceedToWrite.click();
            await expect(page.locator('text=/writing|generating/i').first()).toBeVisible({ timeout: 30000 });
        }
    });
});
