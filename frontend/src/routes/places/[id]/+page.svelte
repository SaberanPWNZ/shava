<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import FavoriteButton from '$lib/components/places/FavoriteButton.svelte';
	import MenuList from '$lib/components/places/MenuList.svelte';
	import ReviewForm from '$lib/components/places/ReviewForm.svelte';
	import ReviewList from '$lib/components/places/ReviewList.svelte';
	import StarRating from '$lib/components/places/StarRating.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import { placesApi, reviewsApi } from '$lib/api/places.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toasts } from '$lib/stores/toasts.svelte';
	import type { PlaceDetail, Review, ReviewOrdering } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let place = $state<PlaceDetail | null>(null);
	let reviews = $state<Review[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let rateError = $state<string | null>(null);
	let reviewOrdering = $state<ReviewOrdering>('newest');
	let reviewsLoading = $state(false);

	let id = $derived(Number(page.params.id));

	const sortOptions = $derived([
		{ value: 'newest', label: m.reviews_sort_newest() },
		{ value: 'helpful', label: m.reviews_sort_helpful() },
		{ value: 'top', label: m.reviews_sort_top() },
		{ value: 'low', label: m.reviews_sort_low() },
		{ value: 'oldest', label: m.reviews_sort_oldest() }
	]);

	async function load() {
		loading = true;
		error = null;
		try {
			place = await placesApi.detail(id);
			const reviewResp = await reviewsApi.listForPlace(id, { ordering: reviewOrdering });
			reviews = reviewResp.results;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function reloadReviews() {
		reviewsLoading = true;
		try {
			const reviewResp = await reviewsApi.listForPlace(id, { ordering: reviewOrdering });
			reviews = reviewResp.results;
		} catch (e) {
			toasts.error((e as Error).message);
		} finally {
			reviewsLoading = false;
		}
	}

	async function rate(stars: number) {
		rateError = null;
		if (!authStore.isAuthenticated) {
			rateError = m.rate_sign_in_required();
			toasts.error(rateError);
			return;
		}
		if (!place) return;
		const previous = { stars: place.stars, ratings_count: place.ratings_count };
		place = { ...place, stars, ratings_count: place.ratings_count + 1 };
		try {
			await placesApi.rate(id, stars);
			toasts.success(m.rate_success({ stars }));
			place = await placesApi.detail(id);
		} catch (e) {
			place = place ? { ...place, ...previous } : place;
			rateError = (e as Error).message;
			toasts.error(rateError);
		}
	}

	function onReviewCreated(optimistic: Review) {
		reviews = [optimistic, ...reviews];
		void load();
	}

	onMount(load);
</script>

<Seo
	title={place?.name ?? m.place_fallback_title()}
	description={place?.description ??
		(place
			? m.place_seo_description({
					name: place.name,
					stars: place.stars?.toFixed(1) ?? '?',
					count: place.ratings_count
				})
			: m.place_seo_fallback())}
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
			<h1 class="text-2xl font-bold text-stone-900 sm:text-3xl dark:text-stone-100">
				{place.name}
			</h1>
			<p class="text-stone-600 dark:text-stone-300">{place.address}</p>
			<div class="flex flex-wrap items-center gap-3">
				<StarRating value={place.stars ?? 0} size="md" />
				<span class="text-sm text-stone-500"
					>{m.place_ratings_count({ count: place.ratings_count })}</span
				>
				<FavoriteButton placeId={id} favorited={place.is_favorited} count={place.favorites_count} />
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
			<p class="text-stone-700 dark:text-stone-300">{place.description}</p>
		{/if}

		<section
			class="rounded-xl border border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900"
		>
			<h2 class="mb-3 text-lg font-semibold">{m.rating_rate_this_place()}</h2>
			{#if rateError}
				<Alert variant="error">{rateError}</Alert>
			{/if}
			{#if place.viewer_rating != null}
				<p class="mb-2 text-sm text-stone-600 dark:text-stone-400">
					{m.place_your_rating({ stars: place.viewer_rating })}
				</p>
			{/if}
			<StarRating
				value={place.viewer_rating ?? place.stars ?? 0}
				interactive
				size="lg"
				onchange={rate}
			/>
		</section>

		<section>
			<h2 class="mb-3 text-xl font-semibold">{m.place_menu_title()}</h2>
			<MenuList items={place.menu ?? []} />
		</section>

		<section class="flex flex-col gap-4">
			<div class="flex flex-wrap items-center justify-between gap-3">
				<h2 class="text-xl font-semibold">{m.place_reviews_title()}</h2>
				{#if reviews.length > 1}
					<div class="w-44">
						<Select
							id="review-sort"
							label={m.reviews_sort_label()}
							bind:value={reviewOrdering}
							onchange={reloadReviews}
						>
							{#each sortOptions as option (option.value)}
								<option value={option.value}>{option.label}</option>
							{/each}
						</Select>
					</div>
				{/if}
			</div>
			{#if authStore.isAuthenticated}
				{#if place.viewer_review_id != null}
					<p class="text-sm text-stone-500 dark:text-stone-400">
						{m.place_already_reviewed()}
						<a class="text-amber-700 hover:underline dark:text-amber-400" href="/profile">
							{m.place_already_reviewed_link()}
						</a>
					</p>
				{:else}
					<ReviewForm placeId={id} oncreated={onReviewCreated} />
				{/if}
			{:else}
				<p class="text-sm text-stone-500">
					<a class="text-amber-700 hover:underline" href={`/login?next=/places/${id}`}>
						{m.place_sign_in_link()}
					</a>
					{m.place_sign_in_to_review()}
				</p>
			{/if}
			<div class:opacity-60={reviewsLoading}>
				<ReviewList {reviews} />
			</div>
		</section>
	</article>
{/if}
