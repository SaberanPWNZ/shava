<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import MenuList from '$lib/components/places/MenuList.svelte';
	import ReviewForm from '$lib/components/places/ReviewForm.svelte';
	import ReviewList from '$lib/components/places/ReviewList.svelte';
	import StarRating from '$lib/components/places/StarRating.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import { placesApi, reviewsApi } from '$lib/api/places.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toasts } from '$lib/stores/toasts.svelte';
	import type { PlaceDetail, Review } from '$lib/types';

	let place = $state<PlaceDetail | null>(null);
	let reviews = $state<Review[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let rateError = $state<string | null>(null);

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
		if (!authStore.isAuthenticated) {
			rateError = 'Please sign in to rate places.';
			toasts.error(rateError);
			return;
		}
		if (!place) return;
		// Optimistic: reflect the new star count immediately; rollback on error.
		const previous = { stars: place.stars, ratings_count: place.ratings_count };
		place = { ...place, stars, ratings_count: place.ratings_count + 1 };
		try {
			await placesApi.rate(id, stars);
			toasts.success(`Rated ${stars} stars.`);
			// Refresh aggregate values from the server (other ratings may have shifted them).
			place = await placesApi.detail(id);
		} catch (e) {
			place = place ? { ...place, ...previous } : place;
			rateError = (e as Error).message;
			toasts.error(rateError);
		}
	}

	function onReviewCreated(optimistic: Review) {
		// Show the user's pending review immediately at the top; the
		// authoritative server copy is fetched in the background.
		reviews = [optimistic, ...reviews];
		void load();
	}

	onMount(load);
</script>

<Seo
	title={place?.name ?? 'Place'}
	description={place?.description ??
		(place
			? `${place.name} — ${place.stars?.toFixed(1) ?? '?'}★ from ${place.ratings_count} ratings on Shava.`
			: 'Place details on Shava.')}
	image={place?.main_image ?? ''}
	type="article"
/>

{#if loading}
	<div class="flex flex-col gap-6" aria-busy="true">
		<Skeleton class="h-8 w-2/3" rounded="md" />
		<Skeleton class="h-4 w-1/2" />
		<Skeleton class="h-64 w-full" rounded="xl" />
		<Skeleton class="h-4 w-full" lines={3} />
	</div>
{:else if error}
	<Alert variant="error">{error}</Alert>
{:else if place}
	<article class="flex flex-col gap-6">
		<header class="flex flex-col gap-3">
			<h1 class="text-2xl font-bold text-zinc-900 sm:text-3xl dark:text-zinc-100">
				{place.name}
			</h1>
			<p class="text-zinc-600 dark:text-zinc-300">{place.address}</p>
			<div class="flex flex-wrap items-center gap-3">
				<StarRating value={place.stars ?? 0} size="md" />
				<span class="text-sm text-zinc-500">{place.ratings_count} ratings</span>
			</div>
		</header>

		{#if place.main_image}
			<img
				src={place.main_image}
				alt={place.name}
				class="max-h-96 w-full rounded-xl object-cover"
			/>
		{/if}

		{#if place.description}
			<p class="text-zinc-700 dark:text-zinc-300">{place.description}</p>
		{/if}

		<section
			class="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
		>
			<h2 class="mb-3 text-lg font-semibold">Rate this place</h2>
			{#if rateError}
				<Alert variant="error">{rateError}</Alert>
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
				<ReviewForm placeId={id} oncreated={onReviewCreated} />
			{:else}
				<p class="text-sm text-zinc-500">
					<a class="text-orange-700 hover:underline" href={`/login?next=/places/${id}`}>
						Sign in
					</a>
					to leave a review.
				</p>
			{/if}
			<ReviewList {reviews} />
		</section>
	</article>
{/if}
