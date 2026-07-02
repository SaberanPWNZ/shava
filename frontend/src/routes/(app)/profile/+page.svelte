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
	import { m } from '$lib/paraglide/messages';

	const PAGE_SIZE = 10;

	type Tab = 'overview' | 'reviews' | 'places' | 'points';
	let activeTab = $state<Tab>('overview');

	let firstName = $state(authStore.user?.first_name ?? '');
	let lastName = $state(authStore.user?.last_name ?? '');
	let saving = $state(false);
	let savedMessage = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});
	let formError = $state<string | null>(null);

	let reviewsPage = $state(1);
	let reviewsData = $state<Paginated<Review> | null>(null);
	let reviewsLoading = $state(false);
	let reviewsError = $state<string | null>(null);

	let placesPage = $state(1);
	let placesData = $state<Paginated<Place> | null>(null);
	let placesLoading = $state(false);
	let placesError = $state<string | null>(null);

	let pointsPage = $state(1);
	let pointsData = $state<Paginated<PointsTransactionRecord> | null>(null);
	let pointsLoading = $state(false);
	let pointsError = $state<string | null>(null);

	const REASON_LABELS = $derived<Record<string, string>>({
		REVIEW_CREATED: m.points_reason_review_created(),
		REVIEW_FIRST_FOR_PLACE: m.points_reason_first_review(),
		REVIEW_PHOTO: m.points_reason_photo(),
		REVIEW_VERIFIED: m.points_reason_verified(),
		REVIEW_HELPFUL_VOTE: m.points_reason_helpful(),
		BADGE_AWARDED: m.points_reason_badge(),
		MANUAL_ADJUSTMENT: m.points_reason_adjustment()
	});

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
			reviewsError = e instanceof Error ? e.message : m.profile_reviews_load_failed();
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
			placesError = e instanceof Error ? e.message : m.profile_places_load_failed();
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
			pointsError = e instanceof Error ? e.message : m.profile_points_load_failed();
		} finally {
			pointsLoading = false;
		}
	}

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
			savedMessage = m.profile_updated();
			toasts.success(m.profile_updated());
		} catch (error) {
			if (error instanceof ApiError) {
				fieldErrors = error.fieldErrors;
				formError = Object.keys(error.fieldErrors).length ? null : error.message;
			} else {
				formError = m.profile_update_failed();
			}
			toasts.error(formError ?? m.profile_update_failed());
		} finally {
			saving = false;
		}
	}

	function fieldError(key: string): string | string[] | null {
		return fieldErrors[key] ?? null;
	}

	const tabs = $derived([
		{ id: 'overview', label: m.profile_tab_overview() },
		{ id: 'reviews', label: m.profile_tab_reviews() },
		{ id: 'places', label: m.profile_tab_places() },
		{ id: 'points', label: m.profile_tab_points() }
	]);
</script>

<div class="mx-auto flex w-full max-w-3xl flex-col gap-6 py-6 sm:py-8">
	<h1 class="text-2xl font-bold text-stone-900 sm:text-3xl dark:text-stone-100">
		{m.profile_title()}
	</h1>

	<Tabs {tabs} bind:value={activeTab} ariaLabel={m.profile_sections_label()}>
		{#snippet panel(id)}
			{#if id === 'overview'}
				<div class="flex flex-col gap-6">
					<Card title={m.profile_account_title()}>
						{#if authStore.user}
							<dl class="mb-6 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
								<div>
									<dt class="font-medium text-stone-500 dark:text-stone-400">{m.field_email()}</dt>
									<dd class="break-words text-stone-900 dark:text-stone-100">
										{authStore.user.email}
									</dd>
								</div>
								<div>
									<dt class="font-medium text-stone-500 dark:text-stone-400">
										{m.profile_verified()}
									</dt>
									<dd class="text-stone-900 dark:text-stone-100">
										{authStore.user.is_verified ? m.yes() : m.no()}
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
									label={m.field_first_name()}
									autocomplete="given-name"
									bind:value={firstName}
									error={fieldError('first_name')}
								/>
								<Input
									id="profile-last-name"
									label={m.field_last_name()}
									autocomplete="family-name"
									bind:value={lastName}
									error={fieldError('last_name')}
								/>
							</div>
							<Button type="submit" loading={saving}>{m.profile_save()}</Button>
						</form>
					</Card>

					<Card title={m.profile_achievements_title()}>
						{#if gamificationStore.me}
							<div class="flex flex-col gap-6">
								<LevelProgressBar profile={gamificationStore.me} />

								<section class="flex flex-col gap-3">
									<h3 class="text-sm font-semibold text-stone-900 dark:text-stone-100">
										{m.profile_badges_title()}
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
							<p class="text-sm text-stone-500 dark:text-stone-400">
								{m.profile_gamification_empty()}
							</p>
						{/if}
					</Card>
				</div>
			{:else if id === 'reviews'}
				<Card title={m.profile_tab_reviews()}>
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
						<p class="text-sm text-stone-500 dark:text-stone-400">
							{m.profile_reviews_empty()}
						</p>
					{:else if reviewsData}
						<ul class="flex flex-col gap-3">
							{#each reviewsData.results as review (review.id)}
								<li
									class="flex flex-col gap-1 rounded-lg border border-stone-200 bg-white p-3 dark:border-stone-800 dark:bg-stone-900"
								>
									<div class="flex items-center justify-between gap-2 text-sm">
										<a
											class="font-medium text-amber-700 hover:underline dark:text-amber-400"
											href={`/places/${review.place}`}
										>
											{review.place_name ?? m.place_fallback_ref({ id: review.place })}
										</a>
										<span class="text-xs text-stone-500">
											{new Date(review.created_at).toLocaleDateString()}
										</span>
									</div>
									<p class="text-sm text-stone-700 dark:text-stone-300">
										{review.score}★ — {review.comment ?? m.profile_no_comment()}
									</p>
									{#if !review.is_moderated}
										<span
											class="self-start rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800 dark:bg-amber-900 dark:text-amber-200"
										>
											{m.reviews_awaiting_moderation()}
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
				<Card title={m.profile_tab_places()}>
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
						<p class="text-sm text-stone-500 dark:text-stone-400">
							{m.profile_places_empty()}
							<a class="text-amber-700 hover:underline" href="/places/new"
								>{m.profile_places_submit_one()}</a
							>.
						</p>
					{:else if placesData}
						<ul class="flex flex-col gap-3">
							{#each placesData.results as place (place.id)}
								<li
									class="flex flex-col gap-1 rounded-lg border border-stone-200 bg-white p-3 dark:border-stone-800 dark:bg-stone-900"
								>
									<div class="flex items-center justify-between gap-2">
										<a
											class="font-medium text-amber-700 hover:underline dark:text-amber-400"
											href={`/places/${place.id}`}
										>
											{place.name}
										</a>
										<span
											class="rounded bg-stone-100 px-2 py-0.5 text-xs text-stone-700 dark:bg-stone-800 dark:text-stone-300"
										>
											{place.status}
										</span>
									</div>
									<p class="text-xs text-stone-500">{place.address}</p>
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
				<Card title={m.profile_tab_points()}>
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
						<p class="text-sm text-stone-500 dark:text-stone-400">{m.profile_points_empty()}</p>
					{:else if pointsData}
						<ul class="flex flex-col gap-2 text-sm">
							{#each pointsData.results as tx (tx.id)}
								<li
									class="flex items-center justify-between gap-2 rounded-lg border border-stone-200 bg-white px-3 py-2 dark:border-stone-800 dark:bg-stone-900"
								>
									<div class="flex flex-col">
										<span class="text-stone-900 dark:text-stone-100">
											{REASON_LABELS[tx.reason] ?? tx.reason}
										</span>
										<span class="text-xs text-stone-500 dark:text-stone-400">
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
