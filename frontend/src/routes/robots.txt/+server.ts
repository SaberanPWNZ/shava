import { env as pubEnv } from '$env/dynamic/public';
import type { RequestHandler } from './$types';

/**
 * `GET /robots.txt` — tells crawlers what to index.
 *
 * Allows everything except auth flows / admin / API endpoints, and
 * advertises the sitemap so search engines can discover place and
 * article URLs without crawling navigational links.
 */
export const GET: RequestHandler = ({ url }) => {
	const origin = (pubEnv.PUBLIC_SITE_URL ?? '').replace(/\/$/, '') || url.origin;
	const body = [
		'User-agent: *',
		'Disallow: /admin/',
		'Disallow: /login',
		'Disallow: /register',
		'Disallow: /forgot-password',
		'Disallow: /reset-password',
		'Disallow: /verify-email',
		'Disallow: /api/',
		'Allow: /',
		'',
		`Sitemap: ${origin}/sitemap.xml`,
		''
	].join('\n');

	return new Response(body, {
		headers: {
			'Content-Type': 'text/plain; charset=utf-8',
			// Crawlers re-fetch robots.txt aggressively; cache 1 h at the
			// edge to keep load off the origin.
			'Cache-Control': 'public, max-age=3600'
		}
	});
};
