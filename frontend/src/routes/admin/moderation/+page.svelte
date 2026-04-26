<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';
	import { placesApi, reviewsApi } from '$lib/api/places.api';
	import { toasts } from '$lib/stores/toasts.svelte';
	import type { ModerationLogEntry, Paginated, Place, Review } from '$lib/types';

	let tab = $state<string>('places');

	let pendingPlaces = $state<Place[]>([]);
	let pendingReviews = $state<Review[]>([]);
	let logEntries = $state<ModerationLogEntry[]>([]);
	let logCount = $state(0);
	let logPage = $state(1);
	const logPageSize = 10;

	let loading = $state(true);
	let logLoading = $state(false);
	let error = $state<string | null>(null);

	async function loadQueues() {
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

	async function loadLog(page = logPage) {
		logLoading = true;
		try {
			const result: Paginated<ModerationLogEntry> = await placesApi.moderationLog(page);
			logEntries = result.results;
			logCount = result.count;
			logPage = page;
		} catch (e) {
			toasts.error((e as Error).message);
		} finally {
			logLoading = false;
		}
	}

	function promptReason(action: 'approve' | 'reject'): string | null {
		// `prompt()` is the smallest accessible way to capture a short reason
		// without introducing a modal component. Returns null if cancelled.
		const message =
			action === 'reject'
				? 'Reason for rejection (visible in the audit log):'
				: 'Optional note (visible in the audit log):';
		const value = typeof window !== 'undefined' ? window.prompt(message, '') : '';
		if (value === null) return null;
		return value;
	}

	async function handlePlace(id: number, action: 'approve' | 'reject') {
		const reason = promptReason(action);
		if (reason === null) return;
		try {
			if (action === 'approve') await placesApi.approve(id, reason);
			else await placesApi.reject(id, reason);
			toasts.success(`Place ${id} ${action}d.`);
			await Promise.all([loadQueues(), loadLog(1)]);
		} catch (e) {
			toasts.error((e as Error).message);
		}
	}

	async function handleReview(id: number, action: 'approve' | 'reject') {
		const reason = promptReason(action);
		if (reason === null) return;
		try {
			if (action === 'approve') await reviewsApi.approve(id, reason);
			else await reviewsApi.reject(id, reason);
			toasts.success(`Review ${id} ${action}d.`);
			await Promise.all([loadQueues(), loadLog(1)]);
		} catch (e) {
			toasts.error((e as Error).message);
		}
	}

	onMount(() => {
		void loadQueues();
		void loadLog(1);
	});

	const tabs = $derived([
		{ id: 'places', label: `Places (${pendingPlaces.length})` },
		{ id: 'reviews', label: `Reviews (${pendingReviews.length})` },
		{ id: 'log', label: 'Activity log' }
	]);
</script>

<section class="flex flex-col gap-4">
	<header class="flex flex-wrap items-center justify-between gap-2">
		<h1 class="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Moderation</h1>
	</header>

	<Tabs {tabs} bind:value={tab} ariaLabel="Moderation sections">
		{#snippet panel(id)}
			{#if error}
				<Alert variant="error">{error}</Alert>
			{/if}

			{#if id === 'places'}
				{#if loading}
					<p class="text-sm text-zinc-500">Loading…</p>
				{:else if pendingPlaces.length === 0}
					<p class="text-sm text-zinc-500">Nothing to moderate.</p>
				{:else}
					<ul class="flex flex-col gap-3">
						{#each pendingPlaces as place (place.id)}
							<li
								class="flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between dark:border-zinc-800 dark:bg-zinc-900"
							>
								<div>
									<p class="font-semibold text-zinc-900 dark:text-zinc-100">{place.name}</p>
									<p class="text-sm text-zinc-600 dark:text-zinc-400">{place.address}</p>
									{#if place.description}
										<p class="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
											{place.description}
										</p>
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
			{:else if id === 'reviews'}
				{#if loading}
					<p class="text-sm text-zinc-500">Loading…</p>
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
										{review.author_username ?? 'Anonymous'} on {review.place_name ??
											`Place ${review.place}`}
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
			{:else if id === 'log'}
				{#if logLoading && logEntries.length === 0}
					<p class="text-sm text-zinc-500">Loading…</p>
				{:else if logEntries.length === 0}
					<p class="text-sm text-zinc-500">No moderation actions recorded yet.</p>
				{:else}
					<ul class="flex flex-col gap-2">
						{#each logEntries as entry (entry.id)}
							<li
								class="flex flex-col gap-1 rounded-xl border border-zinc-200 bg-white p-3 text-sm dark:border-zinc-800 dark:bg-zinc-900"
							>
								<div class="flex flex-wrap items-center gap-2">
									<span
										class="rounded-md px-2 py-0.5 text-xs font-semibold {entry.action ===
										'approve'
											? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200'
											: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-200'}"
									>
										{entry.action}
									</span>
									<span class="text-zinc-700 dark:text-zinc-200">
										{entry.target_type} #{entry.target_id}
									</span>
									<span class="text-zinc-500">
										by {entry.actor_username || 'system'}
									</span>
									<time class="ml-auto text-xs text-zinc-500" datetime={entry.created_at}>
										{new Date(entry.created_at).toLocaleString()}
									</time>
								</div>
								{#if entry.reason}
									<p class="text-zinc-600 dark:text-zinc-300">{entry.reason}</p>
								{/if}
							</li>
						{/each}
					</ul>
					<Pagination
						page={logPage}
						count={logCount}
						pageSize={logPageSize}
						onchange={(p) => loadLog(p)}
					/>
				{/if}
			{/if}
		{/snippet}
	</Tabs>
</section>

