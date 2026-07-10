<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';
	import Seo from '$lib/components/Seo.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import { notificationsApi } from '$lib/api/notifications.api';
	import type { AppNotification, Paginated } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	const PAGE_SIZE = 10;

	let data = $state<Paginated<AppNotification> | null>(null);
	let page = $state(1);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const ICONS: Record<AppNotification['type'], string> = {
		review_approved: '✅',
		review_rejected: '❌',
		place_approved: '🏪',
		place_rejected: '🚫',
		review_reply: '💬',
		favorite_place_review: '⭐'
	};

	function messageFor(note: AppNotification): string {
		const place = note.data.place_name ?? '';
		switch (note.type) {
			case 'review_approved':
				return m.notifications_review_approved({ place });
			case 'review_rejected':
				return m.notifications_review_rejected({ place });
			case 'place_approved':
				return m.notifications_place_approved({ place });
			case 'place_rejected':
				return m.notifications_place_rejected({ place });
			case 'review_reply':
				return m.notifications_review_reply({
					author: note.data.reply_author ?? '',
					place
				});
			case 'favorite_place_review':
				return m.notifications_favorite_place_review({
					author: note.data.review_author ?? '',
					place
				});
		}
	}

	function linkFor(note: AppNotification): string | null {
		if (note.data.place_id) return `/places/${note.data.place_id}`;
		return null;
	}

	async function load(p = 1) {
		loading = true;
		error = null;
		try {
			data = await notificationsApi.list(p);
			page = p;
			// Opening the page reads everything — the bell resets on next
			// navigation, matching what the user expects from an inbox.
			const hasUnread = data.results.some((n) => !n.is_read);
			if (hasUnread) void notificationsApi.markRead().catch(() => {});
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(() => void load(1));
</script>

<Seo title={m.notifications_title()} description={m.notifications_title()} />

<div class="mx-auto flex w-full max-w-2xl flex-col gap-6 py-6 sm:py-8">
	<h1 class="text-2xl font-bold text-stone-900 sm:text-3xl dark:text-stone-100">
		{m.notifications_title()}
	</h1>

	{#if error}
		<Alert variant="error">{error}</Alert>
	{/if}

	{#if loading && !data}
		<div class="flex flex-col gap-3" aria-busy="true">
			{#each Array.from({ length: 5 }, (_, i) => i) as i (i)}
				<Skeleton class="h-16 w-full" rounded="lg" />
			{/each}
		</div>
	{:else if data && data.results.length === 0}
		<p class="text-sm text-stone-500 dark:text-stone-400">{m.notifications_empty()}</p>
	{:else if data}
		<ul class="flex flex-col gap-3">
			{#each data.results as note (note.id)}
				<li
					class="flex items-start gap-3 rounded-xl border p-4 {note.is_read
						? 'border-stone-200 bg-white dark:border-stone-800 dark:bg-stone-900'
						: 'border-amber-300 bg-amber-50/60 dark:border-amber-800 dark:bg-amber-950/40'}"
				>
					<span class="text-xl" aria-hidden="true">{ICONS[note.type]}</span>
					<div class="flex min-w-0 flex-1 flex-col gap-1">
						<p class="text-sm text-stone-800 dark:text-stone-200">{messageFor(note)}</p>
						{#if note.data.text_preview}
							<p class="truncate text-xs text-stone-500 italic dark:text-stone-400">
								“{note.data.text_preview}”
							</p>
						{/if}
						{#if note.data.reason}
							<p class="text-xs text-stone-500 dark:text-stone-400">
								{m.notifications_reason({ reason: note.data.reason })}
							</p>
						{/if}
						<div class="flex items-center justify-between gap-2">
							<span class="text-xs text-stone-500">
								{new Date(note.created_at).toLocaleString()}
							</span>
							{#if linkFor(note)}
								<a
									class="text-xs font-semibold text-amber-700 hover:underline dark:text-amber-400"
									href={linkFor(note)}
								>
									{m.notifications_open_link()}
								</a>
							{/if}
						</div>
					</div>
				</li>
			{/each}
		</ul>
		<Pagination {page} count={data.count} pageSize={PAGE_SIZE} onchange={(p) => load(p)} />
	{/if}
</div>
