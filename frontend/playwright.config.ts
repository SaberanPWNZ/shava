import { defineConfig } from '@playwright/test';

export default defineConfig({
	webServer: {
		command: 'npm run build && npm run preview',
		port: 4173
	},
	use: process.env.PLAYWRIGHT_EXECUTABLE_PATH
		? { launchOptions: { executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH } }
		: {},
	testDir: 'e2e'
});
