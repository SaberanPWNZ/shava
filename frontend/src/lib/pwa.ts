/**
 * Service-worker registration helper.
 *
 * `virtual:pwa-register` is provided by `vite-plugin-pwa` and resolves
 * to a tiny module whose `registerSW()` function attaches the worker
 * lifecycle to the page. The module is unavailable in unit-test builds,
 * so we lazy-import it from a client-only context.
 */
export async function registerServiceWorker(): Promise<void> {
	if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
		return;
	}
	try {
		// @ts-expect-error - virtual module provided by vite-plugin-pwa at build time
		const { registerSW } = await import('virtual:pwa-register');
		registerSW({ immediate: true });
	} catch {
		// Plugin not registered (e.g. tests, dev with PWA disabled) — ignore.
	}
}
