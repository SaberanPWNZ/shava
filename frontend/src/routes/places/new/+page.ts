import type { PageLoad } from './$types';
import { requireAuth } from '$lib/guards/requireAuth';

export const ssr = false;

export const load: PageLoad = async ({ url }) => {
	await requireAuth(url.pathname);
	return {};
};
