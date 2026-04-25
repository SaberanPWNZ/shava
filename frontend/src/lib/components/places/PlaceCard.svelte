<script lang="ts">
	import StarRating from '$lib/components/places/StarRating.svelte';
	import type { Place } from '$lib/types';

	let { place } = $props<{ place: Place }>();
</script>

<a
	href={`/places/${place.id}`}
	class="block overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm transition hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
>
	{#if place.main_image}
		<img
			src={place.main_image}
			alt={place.name}
			class="h-40 w-full object-cover"
			loading="lazy"
		/>
	{:else}
		<div class="flex h-40 items-center justify-center bg-zinc-100 text-zinc-400 dark:bg-zinc-800">
			No image
		</div>
	{/if}
	<div class="p-4">
		<div class="flex items-start justify-between gap-2">
			<h3 class="text-lg font-semibold text-zinc-900 dark:text-zinc-100">{place.name}</h3>
			{#if place.is_featured}
				<span class="rounded-full bg-orange-100 px-2 py-0.5 text-xs font-semibold text-orange-700">
					Featured
				</span>
			{/if}
		</div>
		<p class="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{place.address}</p>
		<div class="mt-3 flex items-center justify-between">
			<StarRating value={place.stars ?? 0} size="sm" />
			<span class="text-xs text-zinc-500 dark:text-zinc-400">
				{place.reviews_count ?? 0} reviews
			</span>
		</div>
		{#if place.delivery}
			<span
				class="mt-2 inline-block rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700"
			>
				Delivery
			</span>
		{/if}
	</div>
</a>
