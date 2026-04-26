import { env as pubEnv } from '$env/dynamic/public';
import type { RequestHandler } from './$types';

interface SitemapEntry {
	loc: string;
	lastmod?: string;
	changefreq?: string;
	priority?: number;
}

interface PlaceForSitemap {
	id: number;
	updated_at?: string;
	status?: string;
}
interface ArticleForSitemap {
	slug: string;
	updated_at?: string;
}
interface Paginated<T> {
	count: number;
	next: string | null;
	results: T[];
}

const STATIC_PATHS: ReadonlyArray<{ path: string; priority: number; changefreq: string }> = [
	{ path: '/', priority: 1.0, changefreq: 'daily' },
	{ path: '/places', priority: 0.9, changefreq: 'daily' },
	{ path: '/articles', priority: 0.8, changefreq: 'daily' },
	{ path: '/leaderboard', priority: 0.5, changefreq: 'daily' }
];

function xmlEscape(value: string): string {
	return value
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&apos;');
}

function renderSitemap(entries: ReadonlyArray<SitemapEntry>): string {
	const urls = entries
		.map((e) => {
			const parts = [`    <loc>${xmlEscape(e.loc)}</loc>`];
			if (e.lastmod) parts.push(`    <lastmod>${xmlEscape(e.lastmod)}</lastmod>`);
			if (e.changefreq) parts.push(`    <changefreq>${e.changefreq}</changefreq>`);
			if (e.priority !== undefined)
				parts.push(`    <priority>${e.priority.toFixed(1)}</priority>`);
			return `  <url>\n${parts.join('\n')}\n  </url>`;
		})
		.join('\n');
	return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;
}

function resolveApiBase(): string {
	const fromBuildEnv = (import.meta as unknown as { env?: Record<string, string> }).env
		?.VITE_API_BASE_URL;
	if (fromBuildEnv) return fromBuildEnv.replace(/\/$/, '');
	return '/api/v1';
}

async function fetchAllPages<T>(
	startUrl: string,
	doFetch: typeof fetch,
	{ maxPages = 20 }: { maxPages?: number } = {}
): Promise<T[]> {
	const out: T[] = [];
	let url: string | null = startUrl;
	let pages = 0;
	while (url && pages < maxPages) {
		const resp: Response = await doFetch(url);
		if (!resp.ok) break;
		const data = (await resp.json()) as Paginated<T>;
		out.push(...data.results);
		url = data.next;
		pages += 1;
	}
	return out;
}

/**
 * `GET /sitemap.xml` — XML sitemap covering static pages plus every
 * approved place and every published article. Indexed by search
 * engines so users can find content without crawling auth-walled
 * navigation.
 *
 * Soft-fails on backend errors: if the API is unreachable we still
 * serve the static portion of the sitemap rather than 5xx-ing.
 */
export const GET: RequestHandler = async ({ url, fetch }) => {
	const origin = (pubEnv.PUBLIC_SITE_URL ?? '').replace(/\/$/, '') || url.origin;
	const apiBase = resolveApiBase();

	let placeEntries: SitemapEntry[] = [];
	let articleEntries: SitemapEntry[] = [];

	try {
		const places = await fetchAllPages<PlaceForSitemap>(
			`${apiBase}/places/?ordering=-updated_at`,
			fetch
		);
		placeEntries = places
			// Only surface approved places — drafts / rejected ones must not
			// leak into the sitemap.
			.filter((p) => !p.status || p.status === 'approved')
			.map((p) => ({
				loc: `${origin}/places/${p.id}`,
				lastmod: p.updated_at?.slice(0, 10),
				changefreq: 'weekly',
				priority: 0.7
			}));
	} catch {
		// Soft-fail: backend down should not 5xx the sitemap.
	}

	try {
		const articles = await fetchAllPages<ArticleForSitemap>(`${apiBase}/articles/`, fetch);
		articleEntries = articles.map((a) => ({
			loc: `${origin}/articles/${a.slug}`,
			lastmod: a.updated_at?.slice(0, 10),
			changefreq: 'monthly',
			priority: 0.6
		}));
	} catch {
		// Soft-fail.
	}

	const staticEntries: SitemapEntry[] = STATIC_PATHS.map((s) => ({
		loc: `${origin}${s.path}`,
		changefreq: s.changefreq,
		priority: s.priority
	}));

	const body = renderSitemap([...staticEntries, ...placeEntries, ...articleEntries]);

	return new Response(body, {
		headers: {
			'Content-Type': 'application/xml; charset=utf-8',
			// Sitemap is moderately expensive to build; cache 15 min.
			'Cache-Control': 'public, max-age=900'
		}
	});
};
