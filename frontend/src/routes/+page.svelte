<script lang="ts">
	import Seo from '$lib/components/Seo.svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { m } from '$lib/paraglide/messages';

	const features = $derived([
		{
			icon: '🔍',
			title: m.home_feature_find_title(),
			text: m.home_feature_find_text()
		},
		{
			icon: '⭐',
			title: m.home_feature_rate_title(),
			text: m.home_feature_rate_text()
		},
		{
			icon: '🏆',
			title: m.home_feature_points_title(),
			text: m.home_feature_points_text()
		}
	]);
</script>

<Seo title={m.app_name()} description={m.home_seo_description()} />

<section
	class="relative -mx-4 -mt-6 overflow-hidden bg-gradient-to-br from-amber-500 via-orange-500 to-orange-700 px-4 py-20 text-white sm:-mx-6 sm:-mt-8 sm:px-6 sm:py-28 lg:-mx-10 lg:px-10 2xl:-mx-16 2xl:px-16"
>
	<div
		class="pointer-events-none absolute inset-0 opacity-20 [background-image:radial-gradient(circle_at_20%_20%,white_0,transparent_40%),radial-gradient(circle_at_80%_60%,white_0,transparent_35%)]"
		aria-hidden="true"
	></div>
	<div class="relative mx-auto flex max-w-4xl flex-col items-center gap-6 text-center">
		<span
			class="rounded-full border border-white/30 bg-white/10 px-4 py-1.5 text-sm font-medium backdrop-blur-sm"
		>
			🌯 {m.home_hero_badge()}
		</span>
		<h1 class="text-4xl font-extrabold tracking-tight text-balance sm:text-6xl">
			{m.home_hero_title_prefix()}
			<span class="underline decoration-amber-200 decoration-4 underline-offset-4"
				>{m.home_hero_title_accent()}</span
			>
		</h1>
		<p class="max-w-2xl text-lg text-amber-50 sm:text-xl">
			{m.home_hero_subtitle()}
		</p>
		<div class="mt-2 flex flex-wrap items-center justify-center gap-3">
			<a
				href="/places"
				class="inline-flex min-h-12 items-center rounded-full bg-white px-7 py-3 text-base font-semibold text-orange-700 shadow-lg transition hover:bg-amber-50 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-orange-600 focus-visible:outline-none"
			>
				{m.home_browse_places()}
			</a>
			{#if !authStore.isAuthenticated}
				<a
					href="/register"
					class="inline-flex min-h-12 items-center rounded-full border-2 border-white/60 px-7 py-3 text-base font-semibold text-white transition hover:border-white hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-white focus-visible:outline-none"
				>
					{m.home_join_free()}
				</a>
			{:else}
				<a
					href="/places/new"
					class="inline-flex min-h-12 items-center rounded-full border-2 border-white/60 px-7 py-3 text-base font-semibold text-white transition hover:border-white hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-white focus-visible:outline-none"
				>
					{m.nav_submit_place()}
				</a>
			{/if}
		</div>
	</div>
</section>

<section class="mx-auto max-w-6xl py-14 sm:py-20">
	<h2 class="text-center text-3xl font-bold tracking-tight text-stone-900 dark:text-stone-50">
		{m.home_how_it_works()}
	</h2>
	<div class="mt-10 grid gap-6 sm:grid-cols-3">
		{#each features as feature (feature.title)}
			<article
				class="flex flex-col gap-3 rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-stone-800 dark:bg-stone-900"
			>
				<span
					class="grid h-12 w-12 place-items-center rounded-xl bg-amber-100 text-2xl dark:bg-amber-950"
					aria-hidden="true"
				>
					{feature.icon}
				</span>
				<h3 class="text-lg font-semibold text-stone-900 dark:text-stone-100">{feature.title}</h3>
				<p class="text-sm leading-relaxed text-stone-600 dark:text-stone-400">{feature.text}</p>
			</article>
		{/each}
	</div>
	<div class="mt-12 text-center">
		<a href="/leaderboard" class="font-semibold text-amber-700 hover:underline dark:text-amber-400">
			{m.home_leaderboard_link()}
		</a>
	</div>
</section>
