<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import { reviewsApi } from '$lib/api/places.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toasts } from '$lib/stores/toasts.svelte';
	import type { ReviewReply } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let { reviewId } = $props<{ reviewId: number }>();

	let replies = $state<ReviewReply[]>([]);
	let loading = $state(true);
	let text = $state('');
	let sending = $state(false);

	onMount(async () => {
		try {
			const response = await reviewsApi.replies(reviewId);
			replies = response.results;
		} catch (e) {
			toasts.error((e as Error).message);
		} finally {
			loading = false;
		}
	});

	async function send(event: SubmitEvent) {
		event.preventDefault();
		const trimmed = text.trim();
		if (!trimmed || sending) return;
		sending = true;
		try {
			const reply = await reviewsApi.addReply(reviewId, trimmed);
			replies = [...replies, reply];
			text = '';
		} catch (e) {
			toasts.error((e as Error).message);
		} finally {
			sending = false;
		}
	}

	async function remove(reply: ReviewReply) {
		try {
			await reviewsApi.deleteReply(reply.id);
			replies = replies.filter((r) => r.id !== reply.id);
		} catch (e) {
			toasts.error((e as Error).message);
		}
	}
</script>

<div class="mt-3 border-l-2 border-stone-200 pl-4 dark:border-stone-700">
	{#if loading}
		<Skeleton class="h-4 w-2/3" lines={2} />
	{:else}
		{#if replies.length === 0}
			<p class="text-xs text-stone-500 dark:text-stone-400">{m.replies_empty()}</p>
		{:else}
			<ul class="flex flex-col gap-2">
				{#each replies as reply (reply.id)}
					<li class="rounded-lg bg-stone-50 px-3 py-2 dark:bg-stone-800/60">
						<div class="flex items-center justify-between gap-2">
							<a
								class="text-xs font-semibold text-stone-800 hover:text-amber-700 hover:underline dark:text-stone-200 dark:hover:text-amber-400"
								href={`/users/${reply.author}`}
							>
								{reply.author_username ?? m.reviews_anonymous()}
							</a>
							<span class="text-[10px] text-stone-500">
								{new Date(reply.created_at).toLocaleDateString()}
							</span>
						</div>
						<p class="mt-1 text-sm break-words text-stone-700 dark:text-stone-300">
							{reply.text}
						</p>
						{#if authStore.user && (reply.author === authStore.user.id || authStore.isAdmin)}
							<button
								type="button"
								class="mt-1 text-[11px] text-stone-400 hover:text-red-600 hover:underline"
								onclick={() => remove(reply)}
							>
								{m.replies_delete()}
							</button>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
		{#if authStore.isAuthenticated}
			<form class="mt-3 flex items-start gap-2" onsubmit={send}>
				<label class="sr-only" for={`reply-input-${reviewId}`}>{m.replies_placeholder()}</label>
				<textarea
					id={`reply-input-${reviewId}`}
					rows="1"
					maxlength="1000"
					placeholder={m.replies_placeholder()}
					bind:value={text}
					class="min-h-10 w-full flex-1 rounded-xl border border-stone-300 bg-white px-3 py-2 text-sm text-stone-900 shadow-sm transition focus:border-amber-500 focus:ring-2 focus:ring-amber-500/25 focus:outline-none dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
				></textarea>
				<Button type="submit" size="sm" loading={sending} disabled={!text.trim()}>
					{m.replies_send()}
				</Button>
			</form>
		{:else}
			<p class="mt-2 text-xs text-stone-500">
				<a class="text-amber-700 hover:underline" href="/login">{m.place_sign_in_link()}</a>
				{m.replies_sign_in_to_reply()}
			</p>
		{/if}
	{/if}
</div>
