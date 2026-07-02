<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { SvelteURLSearchParams } from 'svelte/reactivity';
	import PlaceCard from '$lib/components/places/PlaceCard.svelte';
	import PlaceFilters from '$lib/components/places/PlaceFilters.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import { placesApi } from '$lib/api/places.api';
	import type { Place, PlaceFilters as Filters } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let filters = $state<Filters>({});
	let places = $state<Place[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let initialised = $state(false);

	function readFiltersFromUrl() {
		const params = page.url.searchParams;
		filters.search = params.get('search') ?? '';
		filters.city = params.get('city') ?? '';
		filters.district = params.get('district') ?? '';
		const minStars = params.get('min_stars');
		filters.min_stars = minStars ? Number(minStars) : undefined;
		filters.delivery = params.get('delivery') === 'true';
		filters.is_featured = params.get('is_featured') === 'true';
		filters.has_menu = params.get('has_menu') === 'true';
		filters.ordering = params.get('ordering') ?? '';
	}

	function writeFiltersToUrl() {
		const params = new SvelteURLSearchParams();
		if (filters.search) params.set('search', filters.search);
		if (filters.city) params.set('city', filters.city);
		if (filters.district) params.set('district', filters.district);
		if (filters.min_stars) params.set('min_stars', String(filters.min_stars));
		if (filters.delivery) params.set('delivery', 'true');
		if (filters.is_featured) params.set('is_featured', 'true');
		if (filters.has_menu) params.set('has_menu', 'true');
		if (filters.ordering) params.set('ordering', filters.ordering);
		const qs = params.toString();
		const target = qs ? `/places?${qs}` : '/places';
		void goto(target, { replaceState: true, keepFocus: true, noScroll: true });
	}

	async function load() {
		loading = true;
		error = null;
		try {
			const result = await placesApi.list(filters);
			places = result.results;
		} catch (e) {
			error = (e as Error).message;
			places = [];
		} finally {
			loading = false;
		}
	}

	let debounceTimer: ReturnType<typeof setTimeout> | undefined;

	function applyFilters() {
		clearTimeout(debounceTimer);
		writeFiltersToUrl();
		void load();
	}

	$effect(() => {
		void filters.search;
		void filters.city;
		void filters.district;
		void filters.min_stars;
		void filters.delivery;
		void filters.is_featured;
		void filters.has_menu;
		void filters.ordering;
		if (!initialised) return;
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => {
			writeFiltersToUrl();
			void load();
		}, 300);
		return () => clearTimeout(debounceTimer);
	});

	onMount(() => {
		readFiltersFromUrl();
		void load();
		initialised = true;
	});
</script>

<div class="grid gap-6 lg:grid-cols-[300px_1fr] 2xl:grid-cols-[320px_1fr]">
	<Seo title={m.places_title()} description={m.places_seo_description()} />
	<aside class="lg:sticky lg:top-20 lg:self-start">
		<PlaceFilters bind:filters onapply={applyFilters} />
	</aside>
	<section>
		<header class="mb-4 flex flex-wrap items-center justify-between gap-3">
			<h1 class="text-3xl font-bold tracking-tight text-stone-900 dark:text-stone-100">
				{m.places_title()}
			</h1>
			<a
				href="/places/new"
				class="inline-flex min-h-11 items-center rounded-full bg-gradient-to-br from-amber-500 to-orange-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:from-amber-600 hover:to-orange-700 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2 focus-visible:outline-none dark:focus-visible:ring-offset-stone-950"
			>
				{m.nav_submit_place()}
			</a>
		</header>

		{#if error}
			<p class="text-sm text-red-600" role="alert">{error}</p>
		{/if}

		{#if loading}
			<ul class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4" aria-busy="true">
				{#each Array.from({ length: 6 }, (_, i) => i) as i (i)}
					<li
						class="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900"
					>
						<Skeleton class="h-32 w-full" rounded="lg" />
						<Skeleton class="h-4 w-2/3" />
						<Skeleton class="h-3 w-full" lines={2} />
					</li>
				{/each}
			</ul>
		{:else if places.length === 0}
			<p class="text-sm text-stone-500">{m.places_empty()}</p>
		{:else}
			<div class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
				{#each places as place (place.id)}
					<PlaceCard {place} />
				{/each}
			</div>
		{/if}
	</section>
</div>
