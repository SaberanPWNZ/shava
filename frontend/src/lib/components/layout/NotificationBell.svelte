<script lang="ts">
	import { page } from '$app/state';
	import { notificationsApi } from '$lib/api/notifications.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { m } from '$lib/paraglide/messages';

	const POLL_MS = 60_000;

	let unread = $state(0);

	function refresh() {
		notificationsApi
			.unreadCount()
			.then((r) => (unread = r.unread))
			.catch(() => {});
	}

	// Refresh the badge on login and on every navigation — cheap COUNT query,
	// and it keeps the number honest after the user reads notifications.
	// While signed in, also poll and refresh when the tab regains focus so
	// the badge updates without navigating.
	$effect(() => {
		void page.url.pathname;
		if (!authStore.isAuthenticated) {
			unread = 0;
			return;
		}
		refresh();
		const timer = setInterval(() => {
			if (document.visibilityState === 'visible') refresh();
		}, POLL_MS);
		const onFocus = () => refresh();
		window.addEventListener('focus', onFocus);
		return () => {
			clearInterval(timer);
			window.removeEventListener('focus', onFocus);
		};
	});
</script>

<a
	href="/notifications"
	class="relative inline-flex h-11 w-11 items-center justify-center rounded-full text-stone-500 transition hover:bg-stone-100 hover:text-stone-700 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-200"
	aria-label={unread > 0
		? m.notifications_bell_label_unread({ count: unread })
		: m.notifications_bell_label()}
>
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
			d="M18 8a6 6 0 1 0-12 0c0 7-3 8-3 8h18s-3-1-3-8m-4.7 12a2 2 0 0 1-3.4 0"
		/>
	</svg>
	{#if unread > 0}
		<span
			class="absolute top-1 right-1 grid min-h-4.5 min-w-4.5 place-items-center rounded-full bg-red-600 px-1 text-[10px] leading-none font-bold text-white"
		>
			{unread > 99 ? '99+' : unread}
		</span>
	{/if}
</a>
