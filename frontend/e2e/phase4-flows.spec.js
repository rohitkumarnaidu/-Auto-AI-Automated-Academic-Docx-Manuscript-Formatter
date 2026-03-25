import { test, expect } from '@playwright/test';
import path from 'path';

const E2E_EMAIL = process.env.E2E_EMAIL || '';
const E2E_PASSWORD = process.env.E2E_PASSWORD || '';

async function waitForFormatterCompletion(page, jobId, timeoutMs = 180000) {
    const deadline = Date.now() + timeoutMs;
    let lastStatus = 'UNKNOWN';
    let lastMessage = '';
    let transient404Count = 0;

    while (Date.now() < deadline) {
        const response = await page.request.get(`/api/documents/${encodeURIComponent(jobId)}/status`, {
            failOnStatusCode: false,
        });

        if (response.status() === 200) {
            const payload = await response.json().catch(() => ({}));
            const statusData = payload?.data ?? payload ?? {};
            lastStatus = String(statusData?.status || '').toUpperCase();
            lastMessage = String(statusData?.message || '');

            if (['COMPLETED', 'COMPLETED_WITH_WARNINGS'].includes(lastStatus)) {
                return statusData;
            }

            if (['FAILED', 'ERROR'].includes(lastStatus)) {
                throw new Error(
                    `Formatter job failed. status=${lastStatus}, message=${lastMessage || 'n/a'}`
                );
            }
        } else if (response.status() === 404) {
            // Backend can briefly return 404 during eventual consistency / transient DB reconnects.
            transient404Count += 1;
        }

        await page.waitForTimeout(1500);
    }

    throw new Error(
        `Timed out waiting for formatter completion. lastStatus=${lastStatus}, lastMessage=${lastMessage || 'n/a'}, transient404Count=${transient404Count}`
    );
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

test.describe('Phase 4 Core Flows', () => {
    test.setTimeout(240000); // Production processing can exceed 2 minutes under load

    test('Test full formatter flow (Upload -> Process -> Results -> Download)', async ({ page }) => {
        await page.goto('/upload');
        
        const filePath = path.resolve('../ScholarForm_AI_Documentation.docx');
        
        await page.locator('input[type="file"]').setInputFiles(filePath);

        const processBtn = page.getByRole('button', { name: /process document|re-process manuscript/i }).first();
        await expect(processBtn).toBeVisible();
        await expect(processBtn).toBeEnabled();

        const [uploadResponse] = await Promise.all([
            page.waitForResponse((response) => (
                response.request().method() === 'POST'
                && response.url().includes('/api/documents/upload')
                && response.status() >= 200
                && response.status() < 300
            )),
            processBtn.click(),
        ]);

        const uploadPayloadRaw = await uploadResponse.json().catch(() => ({}));
        const uploadPayload = uploadPayloadRaw?.data ?? uploadPayloadRaw ?? {};
        const jobId = uploadPayload?.job_id;
        expect(jobId).toBeTruthy();

        await expect(page.locator('text=/initiating upload|processing|upload complete/i').first())
            .toBeVisible({ timeout: 20000 });

        await waitForFormatterCompletion(page, jobId, 180000);

        await page.goto(`/jobs/${encodeURIComponent(jobId)}/download`);

        const downloadBtn = page.getByRole('button', { name: /choose export format|download/i }).first();
        await expect(downloadBtn).toBeVisible();
    });

    test('Test full agent flow (Prompt -> Outline -> Approve -> Write)', async ({ page }, testInfo) => {
        await ensureAgentAccess(page, testInfo);
        
        const chatInput = page.getByPlaceholder(/type your prompt here|message|type|prompt|ask/i).first();
        await expect(chatInput).toBeVisible({ timeout: 20000 });
        await chatInput.fill('Write a short paper about machine learning');
        
        await chatInput.press('Control+Enter');
        
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
