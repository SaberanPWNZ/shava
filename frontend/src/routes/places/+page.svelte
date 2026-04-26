<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import PlaceCard from '$lib/components/places/PlaceCard.svelte';
	import PlaceFilters from '$lib/components/places/PlaceFilters.svelte';
	import { placesApi } from '$lib/api/places.api';
	import type { Place, PlaceFilters as Filters } from '$lib/types';

	let filters = $state<Filters>({});
	let places = $state<Place[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	// Set once the initial URL → state hydration finishes so the
	// auto-debounce effect doesn't double-fire the first request.
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
		const params = new URLSearchParams();
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
		// Manual flush from the Apply button — cancel any pending
		// debounce so the request fires exactly once.
		clearTimeout(debounceTimer);
		writeFiltersToUrl();
		void load();
	}

	// Debounced auto-apply: as the user types in search / city or
	// flips a checkbox, schedule a single request 300 ms after the
	// last change. Skips the very first run so we don't reload on
	// hydration of the URL params.
	$effect(() => {
		// Read every filter so the effect tracks them all.
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

<div class="grid gap-6 lg:grid-cols-[280px_1fr]">
	<aside>
		<PlaceFilters bind:filters onapply={applyFilters} />
	</aside>
	<section>
		<header class="mb-4 flex items-center justify-between">
			<h1 class="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Places</h1>
			<a
				href="/places/new"
				class="rounded-lg bg-orange-600 px-4 py-2 text-sm font-semibold text-white hover:bg-orange-700"
			>
				+ Submit a place
			</a>
		</header>

		{#if error}
			<p class="text-sm text-red-600">{error}</p>
		{/if}

		{#if loading}
			<p class="text-sm text-zinc-500">Loading…</p>
		{:else if places.length === 0}
			<p class="text-sm text-zinc-500">No places match your filters.</p>
		{:else}
			<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
				{#each places as place (place.id)}
					<PlaceCard {place} />
				{/each}
			</div>
		{/if}
	</section>
</div>
