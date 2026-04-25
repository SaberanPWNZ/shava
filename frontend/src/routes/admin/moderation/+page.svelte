<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { placesApi, reviewsApi } from '$lib/api/places.api';
	import type { Place, Review } from '$lib/types';

	type Tab = 'places' | 'reviews';
	let tab = $state<Tab>('places');

	let pendingPlaces = $state<Place[]>([]);
	let pendingReviews = $state<Review[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let actionMessage = $state<string | null>(null);

	async function load() {
		loading = true;
		error = null;
		try {
			const [places, reviews] = await Promise.all([
				placesApi.moderationList(),
				reviewsApi.moderationList()
			]);
			pendingPlaces = places.results;
			pendingReviews = reviews.results;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function handlePlace(id: number, action: 'approve' | 'reject') {
		actionMessage = null;
		try {
			if (action === 'approve') await placesApi.approve(id);
			else await placesApi.reject(id);
			actionMessage = `Place ${id} ${action}d.`;
			await load();
		} catch (e) {
			error = (e as Error).message;
		}
	}

	async function handleReview(id: number, action: 'approve' | 'reject') {
		actionMessage = null;
		try {
			if (action === 'approve') await reviewsApi.approve(id);
			else await reviewsApi.reject(id);
			actionMessage = `Review ${id} ${action}d.`;
			await load();
		} catch (e) {
			error = (e as Error).message;
		}
	}

	onMount(load);
</script>

<section class="flex flex-col gap-4">
	<header class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Moderation</h1>
		<nav class="flex gap-2">
			<button
				type="button"
				class="rounded-lg px-3 py-1.5 text-sm font-semibold transition {tab === 'places' ? 'bg-orange-600 text-white' : 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200'}"
				onclick={() => (tab = 'places')}
			>
				Places ({pendingPlaces.length})
			</button>
			<button
				type="button"
				class="rounded-lg px-3 py-1.5 text-sm font-semibold transition {tab === 'reviews' ? 'bg-orange-600 text-white' : 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200'}"
				onclick={() => (tab = 'reviews')}
			>
				Reviews ({pendingReviews.length})
			</button>
		</nav>
	</header>

	{#if actionMessage}
		<Alert variant="success">{actionMessage}</Alert>
	{/if}
	{#if error}
		<Alert variant="error">{error}</Alert>
	{/if}

	{#if loading}
		<p class="text-sm text-zinc-500">Loading…</p>
	{:else if tab === 'places'}
		{#if pendingPlaces.length === 0}
			<p class="text-sm text-zinc-500">Nothing to moderate.</p>
		{:else}
			<ul class="flex flex-col gap-3">
				{#each pendingPlaces as place (place.id)}
					<li
						class="flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900 sm:flex-row sm:items-center sm:justify-between"
					>
						<div>
							<p class="font-semibold text-zinc-900 dark:text-zinc-100">{place.name}</p>
							<p class="text-sm text-zinc-600 dark:text-zinc-400">{place.address}</p>
							{#if place.description}
								<p class="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{place.description}</p>
							{/if}
						</div>
						<div class="flex gap-2">
							<Button variant="primary" onclick={() => handlePlace(place.id, 'approve')}>
								Approve
							</Button>
							<Button variant="danger" onclick={() => handlePlace(place.id, 'reject')}>
								Reject
							</Button>
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	{:else if pendingReviews.length === 0}
		<p class="text-sm text-zinc-500">Nothing to moderate.</p>
	{:else}
		<ul class="flex flex-col gap-3">
			{#each pendingReviews as review (review.id)}
				<li
					class="flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
				>
					<div class="flex items-center justify-between">
						<p class="font-semibold text-zinc-900 dark:text-zinc-100">
							{review.author_username ?? 'Anonymous'} on {review.place_name ?? `Place ${review.place}`}
						</p>
						<span class="text-sm text-zinc-500">Score: {review.score}</span>
					</div>
					{#if review.comment}
						<p class="text-sm text-zinc-700 dark:text-zinc-300">{review.comment}</p>
					{/if}
					<div class="flex gap-2">
						<Button variant="primary" onclick={() => handleReview(review.id, 'approve')}>
							Approve
						</Button>
						<Button variant="danger" onclick={() => handleReview(review.id, 'reject')}>
							Reject
						</Button>
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</section>
