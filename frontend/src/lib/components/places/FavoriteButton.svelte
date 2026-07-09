<script lang="ts">
	import { placesApi } from '$lib/api/places.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toasts } from '$lib/stores/toasts.svelte';
	import { m } from '$lib/paraglide/messages';

	let {
		placeId,
		favorited = false,
		count = 0
	} = $props<{ placeId: number; favorited?: boolean; count?: number }>();

	let isFavorited = $state(false);
	let favoritesCount = $state(0);
	let busy = $state(false);

	// Keep local (optimistic) state in sync when the parent re-fetches.
	$effect(() => {
		isFavorited = favorited;
		favoritesCount = count;
	});

	async function toggle() {
		if (!authStore.isAuthenticated) {
			toasts.error(m.favorite_sign_in_required());
			return;
		}
		if (busy) return;
		busy = true;
		// Optimistic flip; the response carries the authoritative state.
		const previous = { isFavorited, favoritesCount };
		isFavorited = !isFavorited;
		favoritesCount += isFavorited ? 1 : -1;
		try {
			const result = isFavorited
				? await placesApi.favorite(placeId)
				: await placesApi.unfavorite(placeId);
			isFavorited = result.favorited;
			favoritesCount = result.favorites_count;
			toasts.success(isFavorited ? m.favorite_added() : m.favorite_removed());
		} catch (e) {
			isFavorited = previous.isFavorited;
			favoritesCount = previous.favoritesCount;
			toasts.error((e as Error).message);
		} finally {
			busy = false;
		}
	}
</script>

<button
	type="button"
	class="inline-flex min-h-10 items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-semibold transition focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none disabled:opacity-60
		{isFavorited
		? 'border-amber-400 bg-amber-50 text-amber-800 hover:bg-amber-100 dark:border-amber-600 dark:bg-amber-950 dark:text-amber-300'
		: 'border-stone-300 bg-white text-stone-700 hover:border-amber-300 hover:text-amber-700 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200'}"
	aria-pressed={isFavorited}
	disabled={busy}
	onclick={toggle}
>
	<span aria-hidden="true">{isFavorited ? '❤️' : '🤍'}</span>
	<span>{isFavorited ? m.favorite_saved() : m.favorite_save()}</span>
	{#if favoritesCount > 0}
		<span class="text-xs text-stone-500 dark:text-stone-400">({favoritesCount})</span>
	{/if}
</button>
