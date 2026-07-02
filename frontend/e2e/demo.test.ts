import { expect, test } from '@playwright/test';

test.use({ locale: 'uk-UA' });

test('home page shows the landing hero', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toContainText(/полюбиш/i);
});

test('home page renders in English with the locale cookie', async ({ page, context }) => {
	await context.addCookies([
		{ name: 'PARAGLIDE_LOCALE', value: 'en', url: 'http://localhost:4173' }
	]);
	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toContainText(/love/i);
});

test('login page renders the form', async ({ page }) => {
	await page.goto('/login');
	await expect(page.getByLabel('Email')).toBeVisible();
	await expect(page.getByRole('textbox', { name: 'Пароль' })).toBeVisible();
	await expect(page.getByRole('button', { name: 'Увійти' })).toBeVisible();
});

test('register page renders the form', async ({ page }) => {
	await page.goto('/register');
	await expect(page.getByLabel('Email')).toBeVisible();
	await expect(page.getByLabel('Підтвердження пароля')).toBeVisible();
});

test('protected route redirects to login when unauthenticated', async ({ page }) => {
	await page.goto('/profile');
	await page.waitForURL(/\/login/);
	await expect(page).toHaveURL(/\/login/);
});
