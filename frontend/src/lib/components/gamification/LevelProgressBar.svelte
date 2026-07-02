<script lang="ts">
	import type { MeGamification, PublicGamification } from '$lib/types/gamification';
	import { m } from '$lib/paraglide/messages';

	let { profile } = $props<{ profile: MeGamification | PublicGamification }>();
</script>

<div class="flex flex-col gap-2">
	<div class="flex items-baseline justify-between gap-2">
		<span class="text-sm font-semibold text-stone-900 dark:text-stone-100">
			{m.level_label({ level: profile.level })} · {profile.level_title}
		</span>
		<span class="text-xs text-stone-500 dark:text-stone-400">
			{m.level_points({
				points: `${profile.points}${profile.next_threshold !== null ? ` / ${profile.next_threshold}` : ''}`
			})}
		</span>
	</div>
	<div
		class="h-2 w-full overflow-hidden rounded-full bg-stone-200 dark:bg-stone-700"
		role="progressbar"
		aria-valuemin="0"
		aria-valuemax="100"
		aria-valuenow={profile.progress_pct}
		aria-label={m.level_progress_label({ pct: profile.progress_pct })}
	>
		<div
			class="h-full rounded-full bg-gradient-to-r from-amber-500 to-amber-500 transition-all duration-500"
			style:width="{profile.progress_pct}%"
		></div>
	</div>
</div>
