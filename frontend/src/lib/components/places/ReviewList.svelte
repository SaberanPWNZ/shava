<script lang="ts">
	import StarRating from '$lib/components/places/StarRating.svelte';
	import { reviewsHelpfulApi } from '$lib/api/gamification.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { ApiError } from '$lib/types/auth';
	import type { Review } from '$lib/types';

	let { reviews = [] } = $props<{ reviews?: Review[] }>();

	// Seed local toggle state from the server's ``viewer_voted`` flag so
	// the button reflects truth on first paint and survives re-render. We
	// derive (rather than ``$state``-init) so re-runs after the parent
	// refreshes the ``reviews`` prop pick up the new server values.
	const voted = $derived<Record<number, boolean>>(
		Object.fromEntries(reviews.map((r: Review) => [r.id, r.viewer_voted ?? false]))
	);
	// Override map populated only after the user clicks — takes precedence
	// over the server-derived value above.
	const overrides = $state<Record<number, boolean>>({});
	const counts = $state<Record<number, number>>({});
	let voting = $state<number | null>(null);

	function isVoted(review: Review): boolean {
		return overrides[review.id] ?? voted[review.id] ?? false;
	}

	function getCount(review: Review): number {
		return counts[review.id] ?? review.helpful_count ?? 0;
	}

	async function toggleHelpful(review: Review) {
		if (!authStore.isAuthenticated) return;
		if (review.author === authStore.user?.id) return;
		voting = review.id;
		try {
			const result = isVoted(review)
				? await reviewsHelpfulApi.unvote(review.id)
				: await reviewsHelpfulApi.vote(review.id);
			counts[review.id] = result.helpful_count;
			overrides[review.id] = result.voted;
		} catch (error) {
			// Surface 4xx (e.g. self-vote) silently — no UI flow for this in MVP.
			if (!(error instanceof ApiError)) throw error;
		} finally {
			voting = null;
		}
	}
</script>

{#if reviews.length === 0}
	<p class="text-sm text-zinc-500 dark:text-zinc-400">Be the first to leave a review.</p>
{:else}
	<ul class="flex flex-col gap-4">
		{#each reviews as review (review.id)}
			<li class="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
				<div class="flex items-center justify-between gap-2">
					<div>
						<p class="flex items-center gap-2 font-medium text-zinc-900 dark:text-zinc-100">
							{review.author_username ?? 'Anonymous'}
							{#if review.is_verified}
								<span
									class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
									aria-label="Verified review"
									title="Verified by a moderator"
								>
									✅ Verified
								</span>
							{/if}
						</p>
						<p class="text-xs text-zinc-500 dark:text-zinc-400">
							{new Date(review.created_at).toLocaleDateString()}
						</p>
					</div>
					<StarRating value={Number(review.score) / 2} size="sm" />
				</div>
				{#if review.comment}
					<p class="mt-3 text-sm text-zinc-700 dark:text-zinc-300">{review.comment}</p>
				{/if}
				{#if review.dish_image}
					<img
						src={review.dish_image}
						alt="Dish from this review"
						class="mt-3 max-h-60 rounded-lg object-cover"
					/>
				{/if}
				{#if !review.is_moderated}
					<p class="mt-2 text-xs italic text-amber-600">Awaiting moderation</p>
				{/if}

				<div class="mt-3 flex items-center justify-between gap-2">
					<button
						type="button"
						class="inline-flex items-center gap-1 rounded-full border border-zinc-200 px-2.5 py-1 text-xs font-medium text-zinc-700 transition hover:border-orange-300 hover:text-orange-700 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-200 dark:hover:border-orange-500 dark:hover:text-orange-400"
						aria-pressed={isVoted(review)}
						aria-label="Mark this review as helpful"
						disabled={!authStore.isAuthenticated ||
							review.author === authStore.user?.id ||
							voting === review.id}
						onclick={() => toggleHelpful(review)}
					>
						<span aria-hidden="true">👍</span>
						<span>Helpful</span>
						<span class="text-zinc-500 dark:text-zinc-400">({getCount(review)})</span>
					</button>
				</div>
			</li>
		{/each}
	</ul>
{/if}
