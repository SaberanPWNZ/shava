<script lang="ts">
	import { page } from '$app/state';
	import { afterNavigate } from '$app/navigation';
	import { slide } from 'svelte/transition';
	import { authStore } from '$lib/stores/auth.svelte';
	import { authService } from '$lib/services/auth.service';
	import { themeStore } from '$lib/stores/theme.svelte';
	import NotificationBell from '$lib/components/layout/NotificationBell.svelte';
	import PointsBadge from '$lib/components/gamification/PointsBadge.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale, setLocale } from '$lib/paraglide/runtime';

	let menuOpen = $state(false);

	const navLinks = $derived([
		{ href: '/places', label: m.nav_places() },
		{ href: '/articles', label: m.nav_articles() },
		{ href: '/leaderboard', label: m.nav_leaderboard() }
	]);

	const otherLocale = $derived(getLocale() === 'uk' ? 'en' : 'uk');

	function isActive(href: string): boolean {
		return page.url.pathname === href || page.url.pathname.startsWith(href + '/');
	}

	async function logout() {
		menuOpen = false;
		await authService.logout('/');
	}

	afterNavigate(() => {
		menuOpen = false;
	});
</script>

{#snippet themeToggle()}
	<button
		type="button"
		onclick={() => themeStore.toggle()}
		class="inline-flex h-11 w-11 items-center justify-center rounded-full text-stone-500 transition hover:bg-stone-100 hover:text-stone-700 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-200"
		aria-label={themeStore.current === 'dark' ? m.theme_switch_light() : m.theme_switch_dark()}
	>
		{#if themeStore.current === 'dark'}
			<svg
				viewBox="0 0 24 24"
				class="h-5 w-5"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				aria-hidden="true"
			>
				<circle cx="12" cy="12" r="4" />
				<path
					stroke-linecap="round"
					d="M12 3v2m0 14v2M5.6 5.6l1.5 1.5m9.8 9.8 1.5 1.5M3 12h2m14 0h2M5.6 18.4l1.5-1.5m9.8-9.8 1.5-1.5"
				/>
			</svg>
		{:else}
			<svg
				viewBox="0 0 24 24"
				class="h-5 w-5"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				aria-hidden="true"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.6 6.6 0 0 0 9.8 9.8Z"
				/>
			</svg>
		{/if}
	</button>
{/snippet}

{#snippet localeSwitcher()}
	<button
		type="button"
		onclick={() => setLocale(otherLocale)}
		class="inline-flex h-11 min-w-11 items-center justify-center rounded-full px-2 text-sm font-semibold text-stone-500 uppercase transition hover:bg-stone-100 hover:text-stone-700 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-200"
		aria-label={m.locale_switch_label()}
	>
		{otherLocale}
	</button>
{/snippet}

<header
	class="sticky top-0 z-40 border-b border-stone-200/70 bg-white/85 backdrop-blur-md dark:border-stone-800/70 dark:bg-stone-950/85"
>
	<div
		class="mx-auto flex w-full items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-10 2xl:px-16"
	>
		<a
			href="/"
			class="flex items-center gap-2 rounded-md text-xl font-extrabold tracking-tight text-stone-900 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2 focus-visible:outline-none dark:text-stone-50 dark:focus-visible:ring-offset-stone-950"
		>
			<span
				class="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 text-lg text-white shadow-sm"
				aria-hidden="true"
			>
				🌯
			</span>
			<span>{m.app_name()}</span>
		</a>

		<nav class="hidden items-center gap-1 md:flex" aria-label={m.nav_primary_label()}>
			{#each navLinks as link (link.href)}
				<a
					href={link.href}
					aria-current={isActive(link.href) ? 'page' : undefined}
					class="rounded-full px-4 py-2 text-sm font-medium transition focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none
						{isActive(link.href)
						? 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200'
						: 'text-stone-600 hover:bg-stone-100 hover:text-stone-900 dark:text-stone-300 dark:hover:bg-stone-800 dark:hover:text-stone-100'}"
				>
					{link.label}
				</a>
			{/each}
			{#if authStore.isAdmin}
				<a
					href="/admin/moderation"
					aria-current={isActive('/admin/moderation') ? 'page' : undefined}
					class="rounded-full px-4 py-2 text-sm font-semibold text-amber-700 transition hover:bg-amber-50 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-amber-400 dark:hover:bg-amber-950"
				>
					{m.nav_moderation()}
				</a>
			{/if}
		</nav>

		<div class="hidden items-center gap-2 md:flex">
			{@render localeSwitcher()}
			{@render themeToggle()}
			{#if authStore.isAuthenticated}
				<PointsBadge />
				<NotificationBell />
				<a
					href="/places/new"
					class="inline-flex min-h-11 items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-stone-800 shadow-sm transition hover:border-amber-400 hover:text-amber-700 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100 dark:hover:border-amber-600 dark:hover:text-amber-400"
				>
					{m.nav_submit_place()}
				</a>
				<a
					href="/profile"
					aria-current={isActive('/profile') ? 'page' : undefined}
					class="inline-flex min-h-11 items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-stone-600 transition hover:bg-stone-100 hover:text-stone-900 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-stone-300 dark:hover:bg-stone-800 dark:hover:text-stone-100"
				>
					<svg
						viewBox="0 0 24 24"
						class="h-5 w-5"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						aria-hidden="true"
					>
						<circle cx="12" cy="8" r="3.5" />
						<path stroke-linecap="round" d="M4.5 20a7.5 7.5 0 0 1 15 0" />
					</svg>
					{m.nav_profile()}
				</a>
				<button
					type="button"
					onclick={logout}
					class="inline-flex min-h-11 items-center rounded-full px-3 py-2 text-sm font-medium text-stone-500 transition hover:bg-stone-100 hover:text-stone-800 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-100"
				>
					{m.nav_log_out()}
				</button>
			{:else}
				<a
					href="/login"
					class="inline-flex min-h-11 items-center rounded-full px-4 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-stone-200 dark:hover:bg-stone-800"
				>
					{m.nav_log_in()}
				</a>
				<a
					href="/register"
					class="inline-flex min-h-11 items-center rounded-full bg-gradient-to-br from-amber-500 to-orange-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:from-amber-600 hover:to-orange-700 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2 focus-visible:outline-none dark:focus-visible:ring-offset-stone-950"
				>
					{m.nav_sign_up()}
				</a>
			{/if}
		</div>

		<div class="flex items-center gap-1 md:hidden">
			{@render localeSwitcher()}
			{@render themeToggle()}
			{#if authStore.isAuthenticated}
				<NotificationBell />
			{/if}
			<button
				type="button"
				class="inline-flex h-11 w-11 items-center justify-center rounded-full text-stone-700 transition hover:bg-stone-100 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-stone-200 dark:hover:bg-stone-800"
				aria-label={menuOpen ? m.menu_close() : m.menu_open()}
				aria-expanded={menuOpen}
				aria-controls="mobile-nav"
				onclick={() => (menuOpen = !menuOpen)}
			>
				{#if menuOpen}
					<svg
						viewBox="0 0 24 24"
						class="h-6 w-6"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						aria-hidden="true"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 6l12 12M6 18L18 6" />
					</svg>
				{:else}
					<svg
						viewBox="0 0 24 24"
						class="h-6 w-6"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						aria-hidden="true"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M4 12h16M4 17h16" />
					</svg>
				{/if}
			</button>
		</div>
	</div>

	{#if menuOpen}
		<nav
			id="mobile-nav"
			class="border-t border-stone-200 px-4 pt-2 pb-4 md:hidden dark:border-stone-800"
			aria-label={m.nav_primary_label()}
			transition:slide={{ duration: 180 }}
		>
			<ul class="flex flex-col gap-1">
				{#each navLinks as link (link.href)}
					<li>
						<a
							href={link.href}
							aria-current={isActive(link.href) ? 'page' : undefined}
							class="block min-h-11 rounded-xl px-4 py-3 text-base font-medium transition
								{isActive(link.href)
								? 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200'
								: 'text-stone-700 hover:bg-stone-100 dark:text-stone-200 dark:hover:bg-stone-800'}"
						>
							{link.label}
						</a>
					</li>
				{/each}
				{#if authStore.isAuthenticated}
					<li class="px-4 py-2"><PointsBadge /></li>
					<li>
						<a
							href="/places/new"
							class="block min-h-11 rounded-xl px-4 py-3 text-base font-medium text-stone-700 hover:bg-stone-100 dark:text-stone-200 dark:hover:bg-stone-800"
						>
							{m.nav_submit_place()}
						</a>
					</li>
					<li>
						<a
							href="/profile"
							class="block min-h-11 rounded-xl px-4 py-3 text-base font-medium text-stone-700 hover:bg-stone-100 dark:text-stone-200 dark:hover:bg-stone-800"
						>
							{m.nav_profile()}
						</a>
					</li>
					{#if authStore.isAdmin}
						<li>
							<a
								href="/admin/moderation"
								class="block min-h-11 rounded-xl px-4 py-3 text-base font-semibold text-amber-700 hover:bg-amber-50 dark:text-amber-400 dark:hover:bg-amber-950"
							>
								{m.nav_moderation()}
							</a>
						</li>
					{/if}
					<li class="mt-2 border-t border-stone-200 pt-2 dark:border-stone-800">
						<button
							type="button"
							onclick={logout}
							class="block min-h-11 w-full rounded-xl px-4 py-3 text-left text-base font-medium text-stone-500 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800"
						>
							{m.nav_log_out()}
						</button>
					</li>
				{:else}
					<li class="mt-2 flex flex-col gap-2 border-t border-stone-200 pt-3 dark:border-stone-800">
						<a
							href="/login"
							class="block min-h-11 rounded-xl border border-stone-300 px-4 py-3 text-center text-base font-semibold text-stone-800 hover:bg-stone-100 dark:border-stone-700 dark:text-stone-100 dark:hover:bg-stone-800"
						>
							{m.nav_log_in()}
						</a>
						<a
							href="/register"
							class="block min-h-11 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 px-4 py-3 text-center text-base font-semibold text-white shadow-sm hover:from-amber-600 hover:to-orange-700"
						>
							{m.nav_sign_up()}
						</a>
					</li>
				{/if}
			</ul>
		</nav>
	{/if}
</header>
