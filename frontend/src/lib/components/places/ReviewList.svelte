<script lang="ts">
	import StarRating from '$lib/components/places/StarRating.svelte';
	import ReviewReplies from '$lib/components/places/ReviewReplies.svelte';
	import { reviewsHelpfulApi } from '$lib/api/gamification.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { ApiError } from '$lib/types/auth';
	import type { Review } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let { reviews = [] } = $props<{ reviews?: Review[] }>();

	let openReplies = $state<Record<number, boolean>>({});

	const voted = $derived<Record<number, boolean>>(
		Object.fromEntries(reviews.map((r: Review) => [r.id, r.viewer_voted ?? false]))
	);
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
			if (!(error instanceof ApiError)) throw error;
		} finally {
			voting = null;
		}
	}
</script>

{#if reviews.length === 0}
	<p class="text-sm text-stone-500 dark:text-stone-400">{m.reviews_empty()}</p>
{:else}
	<ul class="flex flex-col gap-4">
		{#each reviews as review (review.id)}
			<li
				class="rounded-lg border border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900"
			>
				<div class="flex items-center justify-between gap-2">
					<div>
						<p class="flex items-center gap-2 font-medium text-stone-900 dark:text-stone-100">
							<a
								class="hover:text-amber-700 hover:underline dark:hover:text-amber-400"
								href={`/users/${review.author}`}
							>
								{review.author_username ?? m.reviews_anonymous()}
							</a>
							{#if review.is_verified}
								<span
									class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
									aria-label={m.reviews_verified_label()}
									title={m.reviews_verified_title()}
								>
									✅ {m.reviews_verified()}
								</span>
							{/if}
						</p>
						<p class="text-xs text-stone-500 dark:text-stone-400">
							{new Date(review.created_at).toLocaleDateString()}
						</p>
					</div>
					<StarRating value={Number(review.score) / 2} size="sm" />
				</div>
				{#if review.comment}
					<p class="mt-3 text-sm text-stone-700 dark:text-stone-300">{review.comment}</p>
				{/if}
				{#if review.dish_image}
					<img
						src={review.dish_image}
						alt={m.reviews_dish_alt()}
						class="mt-3 max-h-60 rounded-lg object-cover"
					/>
				{/if}
				{#if !review.is_moderated}
					<p class="mt-2 text-xs italic text-amber-600">{m.reviews_awaiting_moderation()}</p>
				{/if}

				<div class="mt-3 flex items-center justify-between gap-2">
					<button
						type="button"
						class="inline-flex items-center gap-1 rounded-full border border-stone-200 px-2.5 py-1 text-xs font-medium text-stone-700 transition hover:border-amber-300 hover:text-amber-700 disabled:opacity-50 dark:border-stone-700 dark:text-stone-200 dark:hover:border-amber-500 dark:hover:text-amber-400"
						aria-pressed={isVoted(review)}
						aria-label={m.reviews_helpful_label()}
						disabled={!authStore.isAuthenticated ||
							review.author === authStore.user?.id ||
							voting === review.id}
						onclick={() => toggleHelpful(review)}
					>
						<span aria-hidden="true">👍</span>
						<span>{m.reviews_helpful()}</span>
						<span class="text-stone-500 dark:text-stone-400">({getCount(review)})</span>
					</button>
					{#if review.is_moderated}
						<button
							type="button"
							class="inline-flex items-center gap-1 rounded-full border border-stone-200 px-2.5 py-1 text-xs font-medium text-stone-700 transition hover:border-amber-300 hover:text-amber-700 dark:border-stone-700 dark:text-stone-200 dark:hover:border-amber-500 dark:hover:text-amber-400"
							aria-expanded={openReplies[review.id] ?? false}
							onclick={() => (openReplies[review.id] = !(openReplies[review.id] ?? false))}
						>
							<span aria-hidden="true">💬</span>
							<span>{m.replies_toggle({ count: review.replies_count ?? 0 })}</span>
						</button>
					{/if}
				</div>
				{#if openReplies[review.id]}
					<ReviewReplies reviewId={review.id} />
				{/if}
			</li>
		{/each}
	</ul>
{/if}
