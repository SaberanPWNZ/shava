<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { authService } from '$lib/services/auth.service';
	import PointsBadge from '$lib/components/gamification/PointsBadge.svelte';
	import { afterNavigate } from '$app/navigation';

	let menuOpen = $state(false);

	async function logout() {
		menuOpen = false;
		await authService.logout('/');
	}

	function toggleMenu() {
		menuOpen = !menuOpen;
	}

	// Close the mobile menu after every navigation so it never lingers.
	afterNavigate(() => {
		menuOpen = false;
	});
</script>

<header
	class="border-b border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
>
	<div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
		<a
			href="/"
			class="rounded-md text-lg font-bold text-orange-700 focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:ring-offset-2 focus-visible:outline-none dark:focus-visible:ring-offset-zinc-900"
		>
			Shava
		</a>

		<!-- Desktop nav -->
		<nav class="hidden flex-wrap items-center gap-4 text-sm md:flex" aria-label="Primary">
			<a href="/places" class="text-zinc-700 hover:text-orange-700 dark:text-zinc-200">Places</a>
			<a href="/articles" class="text-zinc-700 hover:text-orange-700 dark:text-zinc-200">Articles</a>
			<a href="/leaderboard" class="text-zinc-700 hover:text-orange-700 dark:text-zinc-200">
				Leaderboard
			</a>
			{#if authStore.isAuthenticated}
				<PointsBadge />
				<a href="/places/new" class="text-zinc-700 hover:text-orange-700 dark:text-zinc-200">
					Submit place
				</a>
				<a href="/profile" class="text-zinc-700 hover:text-orange-700 dark:text-zinc-200">Profile</a>
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
					class="text-zinc-700 hover:text-orange-700 dark:text-zinc-200"
				>
					Log out
				</button>
			{:else}
				<a href="/login" class="text-zinc-700 hover:text-orange-700 dark:text-zinc-200">Log in</a>
				<a
					href="/register"
					class="rounded-lg bg-orange-700 px-3 py-1.5 font-semibold text-white hover:bg-orange-800"
				>
					Sign up
				</a>
			{/if}
		</nav>

		<!-- Mobile toggle (visible <md). 44px square keeps the touch target accessible. -->
		<button
			type="button"
			class="inline-flex h-11 w-11 items-center justify-center rounded-md text-zinc-700 hover:bg-zinc-100 focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:outline-none md:hidden dark:text-zinc-200 dark:hover:bg-zinc-800"
			aria-label={menuOpen ? 'Close menu' : 'Open menu'}
			aria-expanded={menuOpen}
			aria-controls="mobile-nav"
			onclick={toggleMenu}
		>
			{#if menuOpen}
				<svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 6l12 12M6 18L18 6" />
				</svg>
			{:else}
				<svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
					<path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M4 12h16M4 17h16" />
				</svg>
			{/if}
		</button>
	</div>

	<!-- Mobile drawer -->
	<nav
		id="mobile-nav"
		class="border-t border-zinc-200 px-4 py-3 md:hidden dark:border-zinc-800"
		aria-label="Primary"
		hidden={!menuOpen}
	>
		<ul class="flex flex-col gap-1 text-sm">
			<li>
				<a
					href="/places"
					class="block min-h-11 rounded-md px-3 py-2 text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
				>
					Places
				</a>
			</li>
			<li>
				<a
					href="/articles"
					class="block min-h-11 rounded-md px-3 py-2 text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
				>
					Articles
				</a>
			</li>
			<li>
				<a
					href="/leaderboard"
					class="block min-h-11 rounded-md px-3 py-2 text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
				>
					Leaderboard
				</a>
			</li>
			{#if authStore.isAuthenticated}
				<li class="px-3 py-2"><PointsBadge /></li>
				<li>
					<a
						href="/places/new"
						class="block min-h-11 rounded-md px-3 py-2 text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
					>
						Submit place
					</a>
				</li>
				<li>
					<a
						href="/profile"
						class="block min-h-11 rounded-md px-3 py-2 text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
					>
						Profile
					</a>
				</li>
				{#if authStore.isAdmin}
					<li>
						<a
							href="/admin/moderation"
							class="block min-h-11 rounded-md px-3 py-2 font-semibold text-orange-700 hover:bg-orange-50 dark:text-orange-400 dark:hover:bg-orange-950"
						>
							Moderation
						</a>
					</li>
				{/if}
				<li>
					<button
						type="button"
						onclick={logout}
						class="block w-full min-h-11 rounded-md px-3 py-2 text-left text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
					>
						Log out
					</button>
				</li>
			{:else}
				<li>
					<a
						href="/login"
						class="block min-h-11 rounded-md px-3 py-2 text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800"
					>
						Log in
					</a>
				</li>
				<li>
					<a
						href="/register"
						class="block min-h-11 rounded-md bg-orange-700 px-3 py-2 font-semibold text-white hover:bg-orange-800"
					>
						Sign up
					</a>
				</li>
			{/if}
		</ul>
	</nav>
</header>
