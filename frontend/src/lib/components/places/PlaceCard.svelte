<script lang="ts">
	import ResponsiveImage from '$lib/components/ResponsiveImage.svelte';
	import StarRating from '$lib/components/places/StarRating.svelte';
	import type { Place } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let { place } = $props<{ place: Place }>();
</script>

<a
	href={`/places/${place.id}`}
	class="group block overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm transition hover:-translate-y-0.5 hover:border-amber-300 hover:shadow-md focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:border-stone-800 dark:bg-stone-900 dark:hover:border-amber-800"
>
	<ResponsiveImage
		thumbnails={place.main_image_thumbnails}
		src={place.main_image}
		alt={place.name}
		sizes="(min-width: 768px) 33vw, 100vw"
		class="h-44 w-full object-cover transition duration-300 group-hover:scale-[1.03]"
	>
		{#snippet fallback()}
			<div class="flex h-44 items-center justify-center bg-stone-100 text-4xl dark:bg-stone-800">
				<span aria-hidden="true">🌯</span>
				<span class="sr-only">{m.no_image()}</span>
			</div>
		{/snippet}
	</ResponsiveImage>
	<div class="p-4">
		<div class="flex items-start justify-between gap-2">
			<h3 class="text-lg font-semibold text-stone-900 dark:text-stone-100">{place.name}</h3>
			{#if place.is_featured}
				<span class="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700">
					{m.place_featured()}
				</span>
			{/if}
		</div>
		<p class="mt-1 text-sm text-stone-600 dark:text-stone-400">{place.address}</p>
		<div class="mt-3 flex items-center justify-between">
			<StarRating value={place.stars ?? 0} size="sm" />
			<span class="text-xs text-stone-500 dark:text-stone-400">
				{m.place_reviews_count({ count: place.reviews_count ?? 0 })}
			</span>
		</div>
		{#if place.delivery}
			<span
				class="mt-2 inline-block rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700"
			>
				{m.place_delivery()}
			</span>
		{/if}
	</div>
</a>
