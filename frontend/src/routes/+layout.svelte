<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import LevelUpToast from '$lib/components/gamification/LevelUpToast.svelte';
	import { authService } from '$lib/services/auth.service';

	let { children } = $props();

	onMount(() => {
		// Hydrate auth state once on the client.
		void authService.hydrate();
	});
</script>

<div class="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
	<Header />
	<main class="mx-auto max-w-6xl px-4 py-8">
		{@render children()}
	</main>
	<LevelUpToast />
</div>
