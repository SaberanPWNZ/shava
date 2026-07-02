<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import { gamificationApi } from '$lib/api/gamification.api';
	import type { Leaderboard } from '$lib/types/gamification';
	import { m } from '$lib/paraglide/messages';

	type Period = 'week' | 'month' | 'all';
	const PERIODS: ReadonlyArray<{ value: Period; label: () => string }> = [
		{ value: 'week', label: m.leaderboard_period_week },
		{ value: 'month', label: m.leaderboard_period_month },
		{ value: 'all', label: m.leaderboard_period_all }
	];

	function paramPeriod(): Period {
		const raw = page.url.searchParams.get('period');
		return raw === 'week' || raw === 'month' || raw === 'all' ? raw : 'all';
	}

	let period = $state<Period>(paramPeriod());
	let board = $state<Leaderboard | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function load(next: Period) {
		loading = true;
		error = null;
		try {
			board = await gamificationApi.leaderboard(next);
		} catch (e) {
			error = (e as Error).message;
			board = null;
		} finally {
			loading = false;
		}
	}

	function selectPeriod(next: Period) {
		if (next === period) return;
		period = next;
		const url = new URL(page.url);
		if (next === 'all') {
			url.searchParams.delete('period');
		} else {
			url.searchParams.set('period', next);
		}
		void goto(`${url.pathname}${url.search}`, { replaceState: false, keepFocus: true });
		void load(next);
	}

	onMount(() => {
		void load(period);
	});
</script>

<Seo title={m.leaderboard_title()} description={m.leaderboard_seo_description()} />

<section class="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-8">
	<header class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-stone-900 dark:text-stone-100">{m.leaderboard_title()}</h1>
			<p class="text-sm text-stone-500 dark:text-stone-400">
				{m.leaderboard_subtitle()}
			</p>
		</div>
		<div
			class="inline-flex rounded-lg border border-stone-300 bg-white p-1 dark:border-stone-700 dark:bg-stone-900"
			role="tablist"
			aria-label={m.leaderboard_period_label()}
		>
			{#each PERIODS as p (p.value)}
				<button
					type="button"
					role="tab"
					aria-selected={period === p.value}
					onclick={() => selectPeriod(p.value)}
					class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors {period === p.value
						? 'bg-amber-700 text-white shadow-sm'
						: 'text-stone-700 hover:bg-stone-100 dark:text-stone-200 dark:hover:bg-stone-800'}"
				>
					{p.label()}
				</button>
			{/each}
		</div>
	</header>

	{#if error}
		<Alert variant="error">{error}</Alert>
	{/if}

	<Card>
		{#if loading}
			<p class="py-8 text-center text-sm text-stone-500 dark:text-stone-400">
				{m.loading_ellipsis()}
			</p>
		{:else if !board || board.results.length === 0}
			<p class="py-8 text-center text-sm text-stone-500 dark:text-stone-400">
				{m.leaderboard_empty()}
			</p>
		{:else}
			<ol class="divide-y divide-stone-200 dark:divide-stone-800">
				{#each board.results as entry, idx (entry.user_id)}
					<li class="flex items-center gap-4 py-3">
						<span
							class="w-8 shrink-0 text-right font-mono text-sm font-semibold {idx < 3
								? 'text-amber-700 dark:text-amber-400'
								: 'text-stone-500 dark:text-stone-400'}"
							aria-label={m.leaderboard_rank({ rank: idx + 1 })}
						>
							{idx + 1}
						</span>
						<div class="flex min-w-0 flex-1 flex-col">
							<span class="truncate text-sm font-semibold text-stone-900 dark:text-stone-100">
								{entry.username || m.leaderboard_user_fallback({ id: entry.user_id })}
							</span>
							<span class="text-xs text-stone-500 dark:text-stone-400">
								{m.level_label({ level: entry.level })} · {entry.level_title}
							</span>
						</div>
						<span
							class="shrink-0 rounded-full bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"
						>
							{m.level_points({ points: entry.points.toLocaleString() })}
						</span>
					</li>
				{/each}
			</ol>
		{/if}
	</Card>
</section>
