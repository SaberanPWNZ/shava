<script lang="ts">
	import { gamificationStore } from '$lib/stores/gamification.svelte';
</script>

{#if gamificationStore.me}
	<a
		href="/profile"
		class="inline-flex items-center gap-1 rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-semibold text-orange-700 transition hover:bg-orange-200 dark:bg-orange-900/40 dark:text-orange-300 dark:hover:bg-orange-900/60"
		aria-label="Your points and level"
		title={`${gamificationStore.me.level_title} — ${gamificationStore.me.points} points`}
	>
		<span aria-hidden="true">⭐</span>
		<span>{gamificationStore.me.points}</span>
		<span class="hidden text-orange-500/80 sm:inline dark:text-orange-400/80">·</span>
		<span class="hidden sm:inline">Lv {gamificationStore.me.level}</span>
	</a>
{/if}
