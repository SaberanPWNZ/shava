<script lang="ts">
	import StarRating from '$lib/components/places/StarRating.svelte';
	import type { Review } from '$lib/types';

	let { reviews = [] } = $props<{ reviews?: Review[] }>();
</script>

{#if reviews.length === 0}
	<p class="text-sm text-zinc-500 dark:text-zinc-400">Be the first to leave a review.</p>
{:else}
	<ul class="flex flex-col gap-4">
		{#each reviews as review (review.id)}
			<li class="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
				<div class="flex items-center justify-between gap-2">
					<div>
						<p class="font-medium text-zinc-900 dark:text-zinc-100">
							{review.author_username ?? 'Anonymous'}
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
				{#if !review.is_moderated}
					<p class="mt-2 text-xs italic text-amber-600">Awaiting moderation</p>
				{/if}
			</li>
		{/each}
	</ul>
{/if}
