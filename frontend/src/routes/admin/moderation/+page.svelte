<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';
	import { placesApi, reviewsApi } from '$lib/api/places.api';
	import { toasts } from '$lib/stores/toasts.svelte';
	import type { ModerationLogEntry, Paginated, Place, Review } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

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
		const message =
			action === 'reject'
				? m.moderation_reject_reason_prompt()
				: m.moderation_approve_note_prompt();
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
			toasts.success(
				action === 'approve'
					? m.moderation_place_approved({ id })
					: m.moderation_place_rejected({ id })
			);
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
			toasts.success(
				action === 'approve'
					? m.moderation_review_approved({ id })
					: m.moderation_review_rejected({ id })
			);
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
		{ id: 'places', label: `${m.places_title()} (${pendingPlaces.length})` },
		{ id: 'reviews', label: `${m.place_reviews_title()} (${pendingReviews.length})` },
		{ id: 'log', label: m.moderation_activity_log() }
	]);
</script>

<section class="flex flex-col gap-4">
	<header class="flex flex-wrap items-center justify-between gap-2">
		<h1 class="text-2xl font-bold text-stone-900 dark:text-stone-100">{m.nav_moderation()}</h1>
	</header>

	<Tabs {tabs} bind:value={tab} ariaLabel={m.moderation_sections_label()}>
		{#snippet panel(id)}
			{#if error}
				<Alert variant="error">{error}</Alert>
			{/if}

			{#if id === 'places'}
				{#if loading}
					<p class="text-sm text-stone-500">{m.loading_ellipsis()}</p>
				{:else if pendingPlaces.length === 0}
					<p class="text-sm text-stone-500">{m.moderation_empty()}</p>
				{:else}
					<ul class="flex flex-col gap-3">
						{#each pendingPlaces as place (place.id)}
							<li
								class="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between dark:border-stone-800 dark:bg-stone-900"
							>
								<div>
									<p class="font-semibold text-stone-900 dark:text-stone-100">{place.name}</p>
									<p class="text-sm text-stone-600 dark:text-stone-400">{place.address}</p>
									{#if place.description}
										<p class="mt-1 text-sm text-stone-500 dark:text-stone-400">
											{place.description}
										</p>
									{/if}
								</div>
								<div class="flex gap-2">
									<Button variant="primary" onclick={() => handlePlace(place.id, 'approve')}>
										{m.moderation_approve()}
									</Button>
									<Button variant="danger" onclick={() => handlePlace(place.id, 'reject')}>
										{m.moderation_reject()}
									</Button>
								</div>
							</li>
						{/each}
					</ul>
				{/if}
			{:else if id === 'reviews'}
				{#if loading}
					<p class="text-sm text-stone-500">{m.loading_ellipsis()}</p>
				{:else if pendingReviews.length === 0}
					<p class="text-sm text-stone-500">{m.moderation_empty()}</p>
				{:else}
					<ul class="flex flex-col gap-3">
						{#each pendingReviews as review (review.id)}
							<li
								class="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900"
							>
								<div class="flex items-center justify-between">
									<p class="font-semibold text-stone-900 dark:text-stone-100">
										{review.author_username ?? m.reviews_anonymous()} — {review.place_name ??
											m.place_fallback_ref({ id: review.place })}
									</p>
									<span class="text-sm text-stone-500"
										>{m.moderation_score({ score: review.score })}</span
									>
								</div>
								{#if review.comment}
									<p class="text-sm text-stone-700 dark:text-stone-300">{review.comment}</p>
								{/if}
								<div class="flex gap-2">
									<Button variant="primary" onclick={() => handleReview(review.id, 'approve')}>
										{m.moderation_approve()}
									</Button>
									<Button variant="danger" onclick={() => handleReview(review.id, 'reject')}>
										{m.moderation_reject()}
									</Button>
								</div>
							</li>
						{/each}
					</ul>
				{/if}
			{:else if id === 'log'}
				{#if logLoading && logEntries.length === 0}
					<p class="text-sm text-stone-500">{m.loading_ellipsis()}</p>
				{:else if logEntries.length === 0}
					<p class="text-sm text-stone-500">{m.moderation_log_empty()}</p>
				{:else}
					<ul class="flex flex-col gap-2">
						{#each logEntries as entry (entry.id)}
							<li
								class="flex flex-col gap-1 rounded-xl border border-stone-200 bg-white p-3 text-sm dark:border-stone-800 dark:bg-stone-900"
							>
								<div class="flex flex-wrap items-center gap-2">
									<span
										class="rounded-md px-2 py-0.5 text-xs font-semibold {entry.action === 'approve'
											? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200'
											: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-200'}"
									>
										{entry.action === 'approve' ? m.moderation_approve() : m.moderation_reject()}
									</span>
									<span class="text-stone-700 dark:text-stone-200">
										{entry.target_type} #{entry.target_id}
									</span>
									<span class="text-stone-500">
										{m.moderation_by({ actor: entry.actor_username || m.moderation_system() })}
									</span>
									<time class="ml-auto text-xs text-stone-500" datetime={entry.created_at}>
										{new Date(entry.created_at).toLocaleString()}
									</time>
								</div>
								{#if entry.reason}
									<p class="text-stone-600 dark:text-stone-300">{entry.reason}</p>
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
