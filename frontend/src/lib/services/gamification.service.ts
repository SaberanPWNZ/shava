import { gamificationApi } from '$lib/api/gamification.api';
import { gamificationStore } from '$lib/stores/gamification.svelte';

export const gamificationService = {
	async refreshMe(): Promise<void> {
		gamificationStore.setLoading(true);
		try {
			const me = await gamificationApi.me();
			gamificationStore.setMe(me);
		} catch {
			// Soft failure — keep existing state.
		} finally {
			gamificationStore.setLoading(false);
		}
	},
	reset(): void {
		gamificationStore.reset();
	}
};
