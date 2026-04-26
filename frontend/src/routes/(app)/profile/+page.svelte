<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';
	import LevelProgressBar from '$lib/components/gamification/LevelProgressBar.svelte';
	import BadgeGrid from '$lib/components/gamification/BadgeGrid.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { placesApi, reviewsApi } from '$lib/api/places.api';
	import { gamificationApi } from '$lib/api/gamification.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { gamificationStore } from '$lib/stores/gamification.svelte';
	import { gamificationService } from '$lib/services/gamification.service';
	import { toasts } from '$lib/stores/toasts.svelte';
	import { ApiError, type FieldErrors } from '$lib/types/auth';
	import type { Place, Review, Paginated } from '$lib/types';
	import type { PointsTransactionRecord } from '$lib/types/gamification';

	const PAGE_SIZE = 10;

	type Tab = 'overview' | 'reviews' | 'places' | 'points';
	let activeTab = $state<Tab>('overview');

	let firstName = $state(authStore.user?.first_name ?? '');
	let lastName = $state(authStore.user?.last_name ?? '');
	let saving = $state(false);
	let savedMessage = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});
	let formError = $state<string | null>(null);

	// My reviews tab
	let reviewsPage = $state(1);
	let reviewsData = $state<Paginated<Review> | null>(null);
	let reviewsLoading = $state(false);
	let reviewsError = $state<string | null>(null);

	// My places tab
	let placesPage = $state(1);
	let placesData = $state<Paginated<Place> | null>(null);
	let placesLoading = $state(false);
	let placesError = $state<string | null>(null);

	// Points history tab
	let pointsPage = $state(1);
	let pointsData = $state<Paginated<PointsTransactionRecord> | null>(null);
	let pointsLoading = $state(false);
	let pointsError = $state<string | null>(null);

	const REASON_LABELS: Record<string, string> = {
		REVIEW_CREATED: 'Posted a review',
		REVIEW_FIRST_FOR_PLACE: 'First review for a place',
		REVIEW_PHOTO: 'Added a dish photo',
		REVIEW_VERIFIED: 'Review verified',
		REVIEW_HELPFUL_VOTE: 'Marked as helpful',
		BADGE_AWARDED: 'Badge bonus',
		MANUAL_ADJUSTMENT: 'Adjustment'
	};

	onMount(() => {
		void gamificationService.refreshMe();
	});

	async function loadReviews(p = reviewsPage) {
		reviewsLoading = true;
		reviewsError = null;
		try {
			reviewsData = await reviewsApi.myList(p);
			reviewsPage = p;
		} catch (e) {
			reviewsError = e instanceof Error ? e.message : 'Could not load reviews.';
		} finally {
			reviewsLoading = false;
		}
	}

	async function loadPlaces(p = placesPage) {
		placesLoading = true;
		placesError = null;
		try {
			placesData = await placesApi.myList(p);
			placesPage = p;
		} catch (e) {
			placesError = e instanceof Error ? e.message : 'Could not load places.';
		} finally {
			placesLoading = false;
		}
	}

	async function loadPoints(p = pointsPage) {
		pointsLoading = true;
		pointsError = null;
		try {
			pointsData = await gamificationApi.myTransactions(p);
			pointsPage = p;
		} catch (e) {
			pointsError = e instanceof Error ? e.message : 'Could not load points history.';
		} finally {
			pointsLoading = false;
		}
	}

	// Lazy-load each tab's data on first activation.
	$effect(() => {
		if (activeTab === 'reviews' && reviewsData === null && !reviewsLoading) {
			void loadReviews(1);
		}
		if (activeTab === 'places' && placesData === null && !placesLoading) {
			void loadPlaces(1);
		}
		if (activeTab === 'points' && pointsData === null && !pointsLoading) {
			void loadPoints(1);
		}
	});

	async function save(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		fieldErrors = {};
		formError = null;
		savedMessage = null;
		try {
			const updated = await authApi.updateMe({ first_name: firstName, last_name: lastName });
			authStore.setUser(updated);
			savedMessage = 'Profile updated.';
			toasts.success('Profile updated.');
		} catch (error) {
			if (error instanceof ApiError) {
				fieldErrors = error.fieldErrors;
				formError = Object.keys(error.fieldErrors).length ? null : error.message;
			} else {
				formError = 'Could not update profile.';
			}
			toasts.error(formError ?? 'Could not update profile.');
		} finally {
			saving = false;
		}
	}

	function fieldError(key: string): string | string[] | null {
		return fieldErrors[key] ?? null;
	}

	const tabs = [
		{ id: 'overview', label: 'Overview' },
		{ id: 'reviews', label: 'My reviews' },
		{ id: 'places', label: 'My places' },
		{ id: 'points', label: 'Points history' }
	];
</script>

<div class="mx-auto flex w-full max-w-3xl flex-col gap-6 py-6 sm:py-8">
	<h1 class="text-2xl font-bold text-zinc-900 sm:text-3xl dark:text-zinc-100">Your profile</h1>

	<Tabs {tabs} bind:value={activeTab} ariaLabel="Profile sections">
		{#snippet panel(id)}
			{#if id === 'overview'}
				<div class="flex flex-col gap-6">
					<Card title="Account">
						{#if authStore.user}
							<dl class="mb-6 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
								<div>
									<dt class="font-medium text-zinc-500 dark:text-zinc-400">Email</dt>
									<dd class="break-words text-zinc-900 dark:text-zinc-100">
										{authStore.user.email}
									</dd>
								</div>
								<div>
									<dt class="font-medium text-zinc-500 dark:text-zinc-400">Verified</dt>
									<dd class="text-zinc-900 dark:text-zinc-100">
										{authStore.user.is_verified ? 'Yes' : 'No'}
									</dd>
								</div>
							</dl>
						{/if}

						{#if savedMessage}
							<Alert variant="success">{savedMessage}</Alert>
						{/if}
						{#if formError}
							<Alert variant="error">{formError}</Alert>
						{/if}

						<form class="mt-4 flex flex-col gap-4" onsubmit={save} novalidate>
							<div class="grid gap-4 sm:grid-cols-2">
								<Input
									id="profile-first-name"
									label="First name"
									autocomplete="given-name"
									bind:value={firstName}
									error={fieldError('first_name')}
								/>
								<Input
									id="profile-last-name"
									label="Last name"
									autocomplete="family-name"
									bind:value={lastName}
									error={fieldError('last_name')}
								/>
							</div>
							<Button type="submit" loading={saving}>Save changes</Button>
						</form>
					</Card>

					<Card title="Achievements">
						{#if gamificationStore.me}
							<div class="flex flex-col gap-6">
								<LevelProgressBar profile={gamificationStore.me} />

								<section class="flex flex-col gap-3">
									<h3 class="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
										Badges
									</h3>
									<BadgeGrid earned={gamificationStore.me.badges} />
								</section>
							</div>
						{:else if gamificationStore.loading}
							<div class="flex flex-col gap-3">
								<Skeleton class="h-3 w-2/3" />
								<Skeleton class="h-3 w-full" />
								<Skeleton class="h-20 w-full" rounded="lg" />
							</div>
						{:else}
							<p class="text-sm text-zinc-500 dark:text-zinc-400">
								Sign in and post a review to start earning points.
							</p>
						{/if}
					</Card>
				</div>
			{:else if id === 'reviews'}
				<Card title="My reviews">
					{#if reviewsError}
						<Alert variant="error">{reviewsError}</Alert>
					{/if}
					{#if reviewsLoading && !reviewsData}
						<div class="flex flex-col gap-3">
							{#each Array.from({ length: 4 }, (_, i) => i) as i (i)}
								<Skeleton class="h-16 w-full" rounded="lg" />
							{/each}
						</div>
					{:else if reviewsData && reviewsData.results.length === 0}
						<p class="text-sm text-zinc-500 dark:text-zinc-400">
							You haven't posted any reviews yet.
						</p>
					{:else if reviewsData}
						<ul class="flex flex-col gap-3">
							{#each reviewsData.results as review (review.id)}
								<li
									class="flex flex-col gap-1 rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900"
								>
									<div class="flex items-center justify-between gap-2 text-sm">
										<a
											class="font-medium text-orange-700 hover:underline dark:text-orange-400"
											href={`/places/${review.place}`}
										>
											{review.place_name ?? `Place #${review.place}`}
										</a>
										<span class="text-xs text-zinc-500">
											{new Date(review.created_at).toLocaleDateString()}
										</span>
									</div>
									<p class="text-sm text-zinc-700 dark:text-zinc-300">
										{review.score}★ — {review.comment ?? '(no comment)'}
									</p>
									{#if !review.is_moderated}
										<span
											class="self-start rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800 dark:bg-amber-900 dark:text-amber-200"
										>
											Pending moderation
										</span>
									{/if}
								</li>
							{/each}
						</ul>
						<Pagination
							page={reviewsPage}
							count={reviewsData.count}
							pageSize={PAGE_SIZE}
							onchange={(p) => loadReviews(p)}
						/>
					{/if}
				</Card>
			{:else if id === 'places'}
				<Card title="My places">
					{#if placesError}
						<Alert variant="error">{placesError}</Alert>
					{/if}
					{#if placesLoading && !placesData}
						<div class="flex flex-col gap-3">
							{#each Array.from({ length: 4 }, (_, i) => i) as i (i)}
								<Skeleton class="h-16 w-full" rounded="lg" />
							{/each}
						</div>
					{:else if placesData && placesData.results.length === 0}
						<p class="text-sm text-zinc-500 dark:text-zinc-400">
							You haven't submitted any places yet.
							<a class="text-orange-600 hover:underline" href="/places/new">Submit one</a>.
						</p>
					{:else if placesData}
						<ul class="flex flex-col gap-3">
							{#each placesData.results as place (place.id)}
								<li
									class="flex flex-col gap-1 rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900"
								>
									<div class="flex items-center justify-between gap-2">
										<a
											class="font-medium text-orange-700 hover:underline dark:text-orange-400"
											href={`/places/${place.id}`}
										>
											{place.name}
										</a>
										<span
											class="rounded bg-zinc-100 px-2 py-0.5 text-xs text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
										>
											{place.status}
										</span>
									</div>
									<p class="text-xs text-zinc-500">{place.address}</p>
								</li>
							{/each}
						</ul>
						<Pagination
							page={placesPage}
							count={placesData.count}
							pageSize={PAGE_SIZE}
							onchange={(p) => loadPlaces(p)}
						/>
					{/if}
				</Card>
			{:else if id === 'points'}
				<Card title="Points history">
					{#if pointsError}
						<Alert variant="error">{pointsError}</Alert>
					{/if}
					{#if pointsLoading && !pointsData}
						<div class="flex flex-col gap-2">
							{#each Array.from({ length: 6 }, (_, i) => i) as i (i)}
								<Skeleton class="h-10 w-full" rounded="md" />
							{/each}
						</div>
					{:else if pointsData && pointsData.results.length === 0}
						<p class="text-sm text-zinc-500 dark:text-zinc-400">No activity yet.</p>
					{:else if pointsData}
						<ul class="flex flex-col gap-2 text-sm">
							{#each pointsData.results as tx (tx.id)}
								<li
									class="flex items-center justify-between gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900"
								>
									<div class="flex flex-col">
										<span class="text-zinc-900 dark:text-zinc-100">
											{REASON_LABELS[tx.reason] ?? tx.reason}
										</span>
										<span class="text-xs text-zinc-500 dark:text-zinc-400">
											{new Date(tx.created_at).toLocaleString()}
										</span>
									</div>
									<span
										class="font-semibold {tx.amount >= 0
											? 'text-emerald-600 dark:text-emerald-400'
											: 'text-rose-600 dark:text-rose-400'}"
									>
										{tx.amount >= 0 ? '+' : ''}{tx.amount}
									</span>
								</li>
							{/each}
						</ul>
						<Pagination
							page={pointsPage}
							count={pointsData.count}
							pageSize={PAGE_SIZE}
							onchange={(p) => loadPoints(p)}
						/>
					{/if}
				</Card>
			{/if}
		{/snippet}
	</Tabs>
</div>

