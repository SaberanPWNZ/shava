<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import LevelUpToast from '$lib/components/gamification/LevelUpToast.svelte';
	import Toaster from '$lib/components/ui/Toaster.svelte';
	import { authService } from '$lib/services/auth.service';
	import { registerServiceWorker } from '$lib/pwa';
	import { m } from '$lib/paraglide/messages';

	let { children } = $props();

	onMount(() => {
		void authService.hydrate();
		void registerServiceWorker();
	});
</script>

<div
	class="flex min-h-screen flex-col bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100"
>
	<a
		href="#main"
		class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-amber-700 focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white focus:shadow-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300"
	>
		{m.skip_to_content()}
	</a>
	<Header />
	<main id="main" class="mx-auto w-full flex-1 px-4 py-6 sm:px-6 sm:py-8 lg:px-10 2xl:px-16">
		{@render children()}
	</main>
	<footer class="border-t border-stone-200 bg-white dark:border-stone-800 dark:bg-stone-900">
		<div
			class="mx-auto flex w-full flex-col items-center justify-between gap-3 px-4 py-6 text-sm text-stone-500 sm:flex-row sm:px-6 lg:px-10 2xl:px-16 dark:text-stone-400"
		>
			<p>© {new Date().getFullYear()} {m.footer_tagline()}</p>
			<nav class="flex flex-wrap items-center gap-4" aria-label={m.footer_nav_label()}>
				<a href="/places" class="hover:text-amber-700 dark:hover:text-amber-400">{m.nav_places()}</a
				>
				<a href="/articles" class="hover:text-amber-700 dark:hover:text-amber-400"
					>{m.nav_articles()}</a
				>
				<a href="/leaderboard" class="hover:text-amber-700 dark:hover:text-amber-400"
					>{m.nav_leaderboard()}</a
				>
			</nav>
		</div>
	</footer>
	<LevelUpToast />
	<Toaster />
</div>
