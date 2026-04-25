<script lang="ts">
	import type { AwardedBadge, Badge } from '$lib/types/gamification';

	let { badge, awarded = false } = $props<{
		badge: Badge | AwardedBadge;
		awarded?: boolean;
	}>();

	const tierClass: Record<string, string> = {
		bronze: 'border-amber-700/40 bg-amber-50 dark:border-amber-700/40 dark:bg-amber-900/20',
		silver: 'border-zinc-400/50 bg-zinc-50 dark:border-zinc-500/40 dark:bg-zinc-800/40',
		gold: 'border-yellow-500/60 bg-yellow-50 dark:border-yellow-500/40 dark:bg-yellow-900/20'
	};
</script>

<div
	class="flex items-start gap-3 rounded-xl border p-3 transition {tierClass[badge.tier] ?? ''} {awarded
		? ''
		: 'opacity-50 grayscale'}"
	aria-label={awarded ? `Badge unlocked: ${badge.title}` : `Locked badge: ${badge.title}`}
>
	<div class="text-2xl" aria-hidden="true">{badge.icon || '🏅'}</div>
	<div class="flex flex-col gap-0.5">
		<span class="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{badge.title}</span>
		<span class="text-xs text-zinc-600 dark:text-zinc-400">{badge.description}</span>
		{#if !awarded}
			<span class="mt-1 text-[10px] uppercase tracking-wide text-zinc-500">Locked</span>
		{/if}
	</div>
</div>
