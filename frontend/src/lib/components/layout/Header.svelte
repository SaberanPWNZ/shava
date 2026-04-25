<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { authService } from '$lib/services/auth.service';

	async function logout() {
		await authService.logout('/');
	}
</script>

<header
	class="border-b border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
>
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
		<a href="/" class="text-lg font-bold text-orange-600">Shava</a>
		<nav class="flex flex-wrap items-center gap-4 text-sm">
			<a href="/places" class="text-zinc-700 hover:text-orange-600 dark:text-zinc-200">Places</a>
			<a href="/articles" class="text-zinc-700 hover:text-orange-600 dark:text-zinc-200">Articles</a>
			{#if authStore.isAuthenticated}
				<a href="/places/new" class="text-zinc-700 hover:text-orange-600 dark:text-zinc-200">
					Submit place
				</a>
				<a href="/profile" class="text-zinc-700 hover:text-orange-600 dark:text-zinc-200">Profile</a>
				{#if authStore.isAdmin}
					<a
						href="/admin/moderation"
						class="font-semibold text-orange-700 hover:text-orange-800 dark:text-orange-400"
					>
						Moderation
					</a>
				{/if}
				<button
					type="button"
					onclick={logout}
					class="text-zinc-700 hover:text-orange-600 dark:text-zinc-200"
				>
					Log out
				</button>
			{:else}
				<a href="/login" class="text-zinc-700 hover:text-orange-600 dark:text-zinc-200">Log in</a>
				<a
					href="/register"
					class="rounded-lg bg-orange-600 px-3 py-1.5 font-semibold text-white hover:bg-orange-700"
				>
					Sign up
				</a>
			{/if}
		</nav>
	</div>
</header>
