/**
 * Lighthouse CI configuration.
 *
 * Asserts that every audited page reaches an Accessibility score of
 * at least 0.95 — the bar set by ROADMAP §6.2. Other Lighthouse
 * categories (performance, SEO, best-practices, PWA) are reported
 * but not asserted, so a CI failure points unambiguously at an a11y
 * regression.
 *
 * Pages requiring API data render their loading / error UI when the
 * backend is unavailable; that UI itself must be accessible, so the
 * audit still produces a meaningful score.
 */
module.exports = {
	ci: {
		collect: {
			startServerCommand: 'npm run preview -- --host 127.0.0.1 --port 4173',
			startServerReadyPattern: 'Local:',
			url: [
				'http://127.0.0.1:4173/',
				'http://127.0.0.1:4173/places',
				'http://127.0.0.1:4173/places/1'
			],
			numberOfRuns: 1,
			settings: {
				preset: 'desktop',
				onlyCategories: ['accessibility'],
				chromeFlags: '--no-sandbox --headless=new'
			}
		},
		assert: {
			assertions: {
				'categories:accessibility': ['error', { minScore: 0.95 }]
			}
		},
		upload: {
			target: 'filesystem',
			outputDir: '.lighthouseci'
		}
	}
};
