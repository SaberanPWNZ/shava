<script lang="ts">
	import { gamificationStore } from '$lib/stores/gamification.svelte';
	import { m } from '$lib/paraglide/messages';
</script>

{#if gamificationStore.me}
	<a
		href="/profile"
		class="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-700 transition hover:bg-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:hover:bg-amber-900/60"
		aria-label={m.points_badge_label()}
		title={m.points_badge_title({
			title: gamificationStore.me.level_title,
			points: gamificationStore.me.points
		})}
	>
		<span aria-hidden="true">⭐</span>
		<span>{gamificationStore.me.points}</span>
		<span class="hidden text-amber-500/80 sm:inline dark:text-amber-400/80">·</span>
		<span class="hidden sm:inline"
			>{m.points_badge_level({ level: gamificationStore.me.level })}</span
		>
	</a>
{/if}
