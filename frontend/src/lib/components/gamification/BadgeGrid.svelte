<script lang="ts">
	import { onMount } from 'svelte';
	import BadgeCard from './BadgeCard.svelte';
	import { gamificationApi } from '$lib/api/gamification.api';
	import type { AwardedBadge, Badge } from '$lib/types/gamification';

	let { earned = [] } = $props<{ earned?: AwardedBadge[] }>();

	let catalogue = $state<Badge[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			catalogue = await gamificationApi.badges();
		} finally {
			loading = false;
		}
	});

	let earnedCodes = $derived(new Set(earned.map((b: AwardedBadge) => b.code)));
</script>

{#if loading}
	<p class="text-sm text-zinc-500 dark:text-zinc-400">Loading badges…</p>
{:else if catalogue.length === 0}
	<p class="text-sm text-zinc-500 dark:text-zinc-400">No badges available.</p>
{:else}
	<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
		{#each catalogue as badge (badge.code)}
			<BadgeCard {badge} awarded={earnedCodes.has(badge.code)} />
		{/each}
	</div>
{/if}
