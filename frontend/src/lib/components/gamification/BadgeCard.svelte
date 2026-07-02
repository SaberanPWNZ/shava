<script lang="ts">
	import type { AwardedBadge, Badge } from '$lib/types/gamification';
	import { m } from '$lib/paraglide/messages';

	let { badge, awarded = false } = $props<{
		badge: Badge | AwardedBadge;
		awarded?: boolean;
	}>();

	const tierClass: Record<string, string> = {
		bronze: 'border-amber-700/40 bg-amber-50 dark:border-amber-700/40 dark:bg-amber-900/20',
		silver: 'border-stone-400/50 bg-stone-50 dark:border-stone-500/40 dark:bg-stone-800/40',
		gold: 'border-yellow-500/60 bg-yellow-50 dark:border-yellow-500/40 dark:bg-yellow-900/20'
	};
</script>

<div
	class="flex items-start gap-3 rounded-xl border p-3 transition {tierClass[badge.tier] ??
		''} {awarded ? '' : 'opacity-50 grayscale'}"
	aria-label={awarded
		? m.badge_unlocked_label({ title: badge.title })
		: m.badge_locked_label({ title: badge.title })}
>
	<div class="text-2xl" aria-hidden="true">{badge.icon || '🏅'}</div>
	<div class="flex flex-col gap-0.5">
		<span class="text-sm font-semibold text-stone-900 dark:text-stone-100">{badge.title}</span>
		<span class="text-xs text-stone-600 dark:text-stone-400">{badge.description}</span>
		{#if !awarded}
			<span class="mt-1 text-[10px] uppercase tracking-wide text-stone-500">{m.badge_locked()}</span
			>
		{/if}
	</div>
</div>
