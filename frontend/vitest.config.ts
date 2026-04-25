/// <reference types="vitest" />
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { fileURLToPath } from 'node:url';

// Dedicated config for `npm run test:unit` so vitest doesn't pull in the
// full SvelteKit runtime (no router, no app/* hooks at boot). We use the
// raw Svelte plugin to compile `.svelte` and `.svelte.ts` files (runes)
// and resolve the SvelteKit virtual modules (`$app/*`) to local stubs.
export default defineConfig({
	plugins: [svelte({ hot: false })],
	resolve: {
		alias: {
			$lib: fileURLToPath(new URL('./src/lib', import.meta.url)),
			'$app/environment': fileURLToPath(
				new URL('./tests/unit/stubs/app-environment.ts', import.meta.url)
			),
			'$app/navigation': fileURLToPath(
				new URL('./tests/unit/stubs/app-navigation.ts', import.meta.url)
			)
		}
	},
	test: {
		environment: 'happy-dom',
		globals: false,
		include: ['tests/unit/**/*.test.ts'],
		// `setupFiles` runs before every test file — we use it to reset
		// `localStorage` and `fetch` mocks so tests stay independent.
		setupFiles: ['./tests/unit/setup.ts'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'lcov'],
			include: [
				'src/lib/api/client.ts',
				'src/lib/services/auth.service.ts',
				'src/lib/stores/auth.svelte.ts',
				'src/lib/guards/requireAuth.ts'
			]
		}
	}
});
