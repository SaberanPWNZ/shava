<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import ReviewList from '$lib/components/places/ReviewList.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import BadgeGrid from '$lib/components/gamification/BadgeGrid.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { reviewsApi } from '$lib/api/places.api';
	import { gamificationApi } from '$lib/api/gamification.api';
	import type { Paginated, Review, UserPublicProfile } from '$lib/types';
	import type { PublicGamification } from '$lib/types/gamification';
	import { m } from '$lib/paraglide/messages';

	const PAGE_SIZE = 10;

	let profile = $state<UserPublicProfile | null>(null);
	let stats = $state<PublicGamification | null>(null);
	let reviewsData = $state<Paginated<Review> | null>(null);
	let reviewsPage = $state(1);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let id = $derived(page.params.id ?? '');

	const displayName = $derived(
		profile
			? profile.username ||
					[profile.first_name, profile.last_name].filter(Boolean).join(' ') ||
					m.leaderboard_user_fallback({ id: profile.id })
			: ''
	);

	async function loadReviews(p = 1) {
		reviewsData = await reviewsApi.byUser(id, p);
		reviewsPage = p;
	}

	onMount(async () => {
		try {
			profile = await authApi.publicProfile(id);
			// Stats and reviews are progressive enhancement — don't block the
			// page if one of them fails.
			const [statsResult, reviewsResult] = await Promise.allSettled([
				gamificationApi.publicProfile(id),
				reviewsApi.byUser(id, 1)
			]);
			if (statsResult.status === 'fulfilled') stats = statsResult.value;
			if (reviewsResult.status === 'fulfilled') {
				reviewsData = reviewsResult.value;
				reviewsPage = 1;
			}
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<Seo
	title={displayName || m.public_profile_fallback_title()}
	description={profile?.bio ?? m.public_profile_seo_description()}
	type="profile"
/>

<div class="mx-auto flex w-full max-w-3xl flex-col gap-6 py-6 sm:py-8">
	{#if loading}
		<div class="flex flex-col gap-4" aria-busy="true">
			<Skeleton class="h-8 w-1/2" rounded="md" />
			<Skeleton class="h-4 w-2/3" />
			<Skeleton class="h-40 w-full" rounded="xl" />
		</div>
	{:else if error}
		<Alert variant="error">{error}</Alert>
	{:else if profile}
		<header class="flex items-start gap-4">
			{#if profile.avatar}
				<img src={profile.avatar} alt={displayName} class="h-16 w-16 rounded-full object-cover" />
			{:else}
				<span
					class="grid h-16 w-16 place-items-center rounded-full bg-amber-100 text-3xl dark:bg-amber-950"
					aria-hidden="true"
				>
					🌯
				</span>
			{/if}
			<div class="flex min-w-0 flex-col gap-1">
				<h1 class="text-2xl font-bold text-stone-900 sm:text-3xl dark:text-stone-100">
					{displayName}
				</h1>
				<p class="text-sm text-stone-500 dark:text-stone-400">
					{m.public_profile_member_since({
						date: new Date(profile.member_since).toLocaleDateString()
					})}
					{#if profile.city}
						· {profile.city.name}
					{/if}
				</p>
				{#if profile.bio}
					<p class="mt-1 text-sm text-stone-700 dark:text-stone-300">{profile.bio}</p>
				{/if}
			</div>
		</header>

		{#if stats}
			<section
				class="flex flex-wrap items-center gap-6 rounded-xl border border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900"
				aria-label={m.public_profile_stats_label()}
			>
				<div>
					<p class="text-xs text-stone-500 dark:text-stone-400">{m.public_profile_points()}</p>
					<p class="text-xl font-bold text-stone-900 dark:text-stone-100">{stats.points}</p>
				</div>
				<div>
					<p class="text-xs text-stone-500 dark:text-stone-400">{m.public_profile_level()}</p>
					<p class="text-xl font-bold text-stone-900 dark:text-stone-100">
						{stats.level} · {stats.level_title}
					</p>
				</div>
				{#if stats.badges?.length}
					<div class="w-full">
						<p class="mb-2 text-xs text-stone-500 dark:text-stone-400">
							{m.profile_badges_title()}
						</p>
						<BadgeGrid earned={stats.badges} />
					</div>
				{/if}
			</section>
		{/if}

		<section class="flex flex-col gap-4">
			<h2 class="text-xl font-semibold text-stone-900 dark:text-stone-100">
				{m.public_profile_reviews_title({ count: reviewsData?.count ?? 0 })}
			</h2>
			{#if reviewsData && reviewsData.results.length > 0}
				<ReviewList reviews={reviewsData.results} />
				<Pagination
					page={reviewsPage}
					count={reviewsData.count}
					pageSize={PAGE_SIZE}
					onchange={(p) => loadReviews(p)}
				/>
			{:else}
				<p class="text-sm text-stone-500 dark:text-stone-400">
					{m.public_profile_no_reviews()}
				</p>
			{/if}
		</section>
	{/if}
</div>
