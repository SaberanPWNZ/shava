<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import LevelUpToast from '$lib/components/gamification/LevelUpToast.svelte';
	import Toaster from '$lib/components/ui/Toaster.svelte';
	import { authService } from '$lib/services/auth.service';

	let { children } = $props();

	onMount(() => {
		// Hydrate auth state once on the client.
		void authService.hydrate();
	});
</script>

<div class="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
	<Header />
	<main id="main" class="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
		{@render children()}
	</main>
	<LevelUpToast />
	<Toaster />
</div>

