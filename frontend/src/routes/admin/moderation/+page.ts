import type { PageLoad } from './$types';
import { requireAdmin } from '$lib/guards/requireAuth';

export const ssr = false;

export const load: PageLoad = async ({ url }) => {
	await requireAdmin(url.pathname);
	return {};
};
