import type { LayoutLoad } from './$types';
import { requireAuth } from '$lib/guards/requireAuth';

export const ssr = false;

export const load: LayoutLoad = async ({ url }) => {
	await requireAuth(url.pathname);
	return {};
};
