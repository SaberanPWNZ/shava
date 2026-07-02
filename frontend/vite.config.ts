import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import { paraglideVitePlugin } from '@inlang/paraglide-js';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		paraglideVitePlugin({
			project: './project.inlang',
			outdir: './src/lib/paraglide',
			strategy: ['cookie', 'preferredLanguage', 'baseLocale']
		}),
		sveltekit(),
		SvelteKitPWA({
			registerType: 'autoUpdate',
			injectRegister: 'auto',
			strategies: 'generateSW',
			scope: '/',
			base: '/',
			manifest: {
				name: 'Shava — find great shawarma near you',
				short_name: 'Shava',
				description: 'Discover, rate and review the best shawarma places in your city.',
				theme_color: '#d97706',
				background_color: '#fafaf9',
				display: 'standalone',
				orientation: 'portrait',
				start_url: '/',
				lang: 'uk',
				categories: ['food', 'lifestyle', 'social'],
				icons: [
					{ src: 'pwa-64x64.png', sizes: '64x64', type: 'image/png' },
					{ src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
					{ src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
					{
						src: 'maskable-icon-512x512.png',
						sizes: '512x512',
						type: 'image/png',
						purpose: 'maskable'
					}
				]
			},
			workbox: {
				globPatterns: ['client/**/*.{js,css,ico,png,svg,webp,woff,woff2}'],
				navigateFallback: '/offline',
				navigateFallbackDenylist: [/^\/api\//],
				cleanupOutdatedCaches: true,
				clientsClaim: true,
				runtimeCaching: [
					{
						urlPattern: ({ url }) => url.pathname.startsWith('/_app/immutable/'),
						handler: 'CacheFirst',
						options: {
							cacheName: 'sveltekit-immutable',
							expiration: { maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 30 }
						}
					},
					{
						urlPattern: ({ request }) =>
							['style', 'script', 'image', 'font'].includes(request.destination),
						handler: 'StaleWhileRevalidate',
						options: {
							cacheName: 'static-assets',
							expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 7 }
						}
					},
					{
						urlPattern: ({ url, request }) =>
							request.method === 'GET' && url.pathname.startsWith('/api/'),
						handler: 'NetworkFirst',
						options: {
							cacheName: 'api-get',
							networkTimeoutSeconds: 5,
							expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 },
							cacheableResponse: { statuses: [0, 200] }
						}
					}
				]
			},
			devOptions: {
				enabled: false,
				type: 'module',
				navigateFallback: '/'
			},
			kit: {
				includeVersionFile: true
			}
		})
	]
});
