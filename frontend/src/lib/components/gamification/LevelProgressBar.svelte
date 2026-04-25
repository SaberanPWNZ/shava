<script lang="ts">
	import type { MeGamification, PublicGamification } from '$lib/types/gamification';

	let { profile } = $props<{ profile: MeGamification | PublicGamification }>();
</script>

<div class="flex flex-col gap-2">
	<div class="flex items-baseline justify-between gap-2">
		<span class="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
			Level {profile.level} · {profile.level_title}
		</span>
		<span class="text-xs text-zinc-500 dark:text-zinc-400">
			{profile.points}
			{profile.next_threshold !== null ? `/ ${profile.next_threshold}` : ''} pts
		</span>
	</div>
	<div
		class="h-2 w-full overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700"
		role="progressbar"
		aria-valuemin="0"
		aria-valuemax="100"
		aria-valuenow={profile.progress_pct}
		aria-label={`Progress to next level: ${profile.progress_pct}%`}
	>
		<div
			class="h-full rounded-full bg-gradient-to-r from-orange-500 to-amber-500 transition-all duration-500"
			style:width="{profile.progress_pct}%"
		></div>
	</div>
</div>
