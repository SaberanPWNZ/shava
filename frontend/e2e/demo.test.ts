import { expect, test } from '@playwright/test';

test('home page shows the landing hero', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toContainText(/love/i);
});

test('login page renders the form', async ({ page }) => {
	await page.goto('/login');
	await expect(page.getByLabel('Email')).toBeVisible();
	await expect(page.getByLabel('Password')).toBeVisible();
	await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
});

test('register page renders the form', async ({ page }) => {
	await page.goto('/register');
	await expect(page.getByLabel('Email')).toBeVisible();
	await expect(page.getByLabel('Confirm password')).toBeVisible();
});

test('protected route redirects to login when unauthenticated', async ({ page }) => {
	await page.goto('/profile');
	await page.waitForURL(/\/login/);
	await expect(page).toHaveURL(/\/login/);
});
