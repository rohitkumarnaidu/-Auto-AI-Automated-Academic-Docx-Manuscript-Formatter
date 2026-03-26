import { test, expect } from '@playwright/test';

test.describe('Protected Routes Redirect (E2E-006)', () => {
  test('redirects unauthenticated user from /dashboard to /login', async ({ page }) => {
    // Attempt to access a protected route
    await page.goto('/dashboard');
    
    // Check that we are redirected to the login page
    await expect(page).toHaveURL(/.*\/login/);
    
    // Wait for the login form to be visible (basic check)
    await expect(page.getByRole('heading', { level: 2 }).first()).toBeVisible();
  });

  test('redirects unauthenticated user from /settings to /login', async ({ page }) => {
    await page.goto('/settings');
    await expect(page).toHaveURL(/.*\/login/);
  });
  
  test('redirects unauthenticated user from /profile to /login', async ({ page }) => {
    await page.goto('/profile');
    await expect(page).toHaveURL(/.*\/login/);
  });
});
