<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import { gamificationApi } from '$lib/api/gamification.api';
	import type { Leaderboard } from '$lib/types/gamification';

	type Period = 'week' | 'month' | 'all';
	const PERIODS: ReadonlyArray<{ value: Period; label: string }> = [
		{ value: 'week', label: 'This week' },
		{ value: 'month', label: 'This month' },
		{ value: 'all', label: 'All time' }
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
		// Keep period in the URL so the view is shareable / back-button
		// navigation restores the user's last filter.
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

<Seo title="Leaderboard" description="Top contributors on Shava ranked by points." />

<section class="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-8">
	<header class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Leaderboard</h1>
			<p class="text-sm text-zinc-500 dark:text-zinc-400">
				Top 50 contributors by points earned for reviews and helpful votes.
			</p>
		</div>
		<div
			class="inline-flex rounded-lg border border-zinc-300 bg-white p-1 dark:border-zinc-700 dark:bg-zinc-900"
			role="tablist"
			aria-label="Leaderboard period"
		>
			{#each PERIODS as p (p.value)}
				<button
					type="button"
					role="tab"
					aria-selected={period === p.value}
					onclick={() => selectPeriod(p.value)}
					class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors {period === p.value
						? 'bg-orange-700 text-white shadow-sm'
						: 'text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800'}"
				>
					{p.label}
				</button>
			{/each}
		</div>
	</header>

	{#if error}
		<Alert variant="error">{error}</Alert>
	{/if}

	<Card>
		{#if loading}
			<p class="py-8 text-center text-sm text-zinc-500 dark:text-zinc-400">Loading…</p>
		{:else if !board || board.results.length === 0}
			<p class="py-8 text-center text-sm text-zinc-500 dark:text-zinc-400">
				No activity yet for this period.
			</p>
		{:else}
			<ol class="divide-y divide-zinc-200 dark:divide-zinc-800">
				{#each board.results as entry, idx (entry.user_id)}
					<li class="flex items-center gap-4 py-3">
						<span
							class="w-8 shrink-0 text-right font-mono text-sm font-semibold {idx < 3
								? 'text-orange-700 dark:text-orange-400'
								: 'text-zinc-500 dark:text-zinc-400'}"
							aria-label={`Rank ${idx + 1}`}
						>
							{idx + 1}
						</span>
						<div class="flex min-w-0 flex-1 flex-col">
							<span
								class="truncate text-sm font-semibold text-zinc-900 dark:text-zinc-100"
							>
								{entry.username || `user #${entry.user_id}`}
							</span>
							<span class="text-xs text-zinc-500 dark:text-zinc-400">
								Level {entry.level} · {entry.level_title}
							</span>
						</div>
						<span
							class="shrink-0 rounded-full bg-orange-100 px-3 py-1 text-sm font-semibold text-orange-700 dark:bg-orange-900/40 dark:text-orange-300"
						>
							{entry.points.toLocaleString()} pts
						</span>
					</li>
				{/each}
			</ol>
		{/if}
	</Card>
</section>
