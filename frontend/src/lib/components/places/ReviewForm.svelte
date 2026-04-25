<script lang="ts">
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import StarRating from '$lib/components/places/StarRating.svelte';
	import { reviewsApi } from '$lib/api/places.api';
	import { ApiError } from '$lib/types/auth';

	let { placeId, oncreated } = $props<{ placeId: number; oncreated?: () => void }>();

	let stars = $state(5);
	let comment = $state('');
	let submitting = $state(false);
	let formError = $state<string | null>(null);
	let success = $state<string | null>(null);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		formError = null;
		success = null;
		try {
			// Backend stores 1-10 score; multiply stars (1-5) by 2.
			await reviewsApi.create(placeId, { score: (stars * 2).toFixed(1), comment });
			success = 'Thanks! Your review is awaiting moderation.';
			comment = '';
			stars = 5;
			oncreated?.();
		} catch (error) {
			formError =
				error instanceof ApiError ? error.message : 'Could not submit the review.';
		} finally {
			submitting = false;
		}
	}
</script>

<form
	class="flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
	onsubmit={submit}
>
	<h3 class="text-base font-semibold text-zinc-900 dark:text-zinc-100">Add a review</h3>

	{#if formError}
		<Alert variant="error">{formError}</Alert>
	{/if}
	{#if success}
		<Alert variant="success">{success}</Alert>
	{/if}

	<div class="flex items-center gap-2">
		<span class="text-sm font-medium text-zinc-700 dark:text-zinc-300">Your rating</span>
		<StarRating value={stars} interactive onchange={(n) => (stars = n)} />
	</div>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">Comment</span>
		<textarea
			rows="3"
			bind:value={comment}
			class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
		></textarea>
	</label>

	<Button type="submit" loading={submitting}>Submit review</Button>
</form>
