<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import MenuList from '$lib/components/places/MenuList.svelte';
	import ReviewForm from '$lib/components/places/ReviewForm.svelte';
	import ReviewList from '$lib/components/places/ReviewList.svelte';
	import StarRating from '$lib/components/places/StarRating.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { placesApi, reviewsApi } from '$lib/api/places.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import type { PlaceDetail, Review } from '$lib/types';

	let place = $state<PlaceDetail | null>(null);
	let reviews = $state<Review[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let rateError = $state<string | null>(null);
	let rateSuccess = $state<string | null>(null);

	let id = $derived(Number(page.params.id));

	async function load() {
		loading = true;
		error = null;
		try {
			place = await placesApi.detail(id);
			const reviewResp = await reviewsApi.listForPlace(id);
			reviews = reviewResp.results;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function rate(stars: number) {
		rateError = null;
		rateSuccess = null;
		if (!authStore.isAuthenticated) {
			rateError = 'Please sign in to rate places.';
			return;
		}
		try {
			await placesApi.rate(id, stars);
			rateSuccess = `Rated ${stars} stars.`;
			place = await placesApi.detail(id);
		} catch (e) {
			rateError = (e as Error).message;
		}
	}

	onMount(load);
</script>

{#if loading}
	<p class="text-sm text-zinc-500">Loading…</p>
{:else if error}
	<Alert variant="error">{error}</Alert>
{:else if place}
	<article class="flex flex-col gap-6">
		<header class="flex flex-col gap-3">
			<h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100">{place.name}</h1>
			<p class="text-zinc-600 dark:text-zinc-300">{place.address}</p>
			<div class="flex items-center gap-3">
				<StarRating value={place.stars ?? 0} size="md" />
				<span class="text-sm text-zinc-500">{place.ratings_count} ratings</span>
			</div>
		</header>

		{#if place.main_image}
			<img src={place.main_image} alt={place.name} class="max-h-96 w-full rounded-xl object-cover" />
		{/if}

		{#if place.description}
			<p class="text-zinc-700 dark:text-zinc-300">{place.description}</p>
		{/if}

		<section class="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
			<h2 class="mb-3 text-lg font-semibold">Rate this place</h2>
			{#if rateError}
				<Alert variant="error">{rateError}</Alert>
			{/if}
			{#if rateSuccess}
				<Alert variant="success">{rateSuccess}</Alert>
			{/if}
			<StarRating value={place.stars ?? 0} interactive size="lg" onchange={rate} />
		</section>

		<section>
			<h2 class="mb-3 text-xl font-semibold">Menu</h2>
			<MenuList items={place.menu ?? []} />
		</section>

		<section class="flex flex-col gap-4">
			<h2 class="text-xl font-semibold">Reviews</h2>
			{#if authStore.isAuthenticated}
				<ReviewForm placeId={id} oncreated={load} />
			{:else}
				<p class="text-sm text-zinc-500">
					<a class="text-orange-600 hover:underline" href={`/login?next=/places/${id}`}>Sign in</a>
					to leave a review.
				</p>
			{/if}
			<ReviewList {reviews} />
		</section>
	</article>
{/if}
