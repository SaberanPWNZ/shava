<script lang="ts">
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import StarRating from '$lib/components/places/StarRating.svelte';
	import { reviewsApi } from '$lib/api/places.api';
	import { gamificationService } from '$lib/services/gamification.service';
	import { ApiError } from '$lib/types/auth';

	let { placeId, oncreated } = $props<{ placeId: number; oncreated?: () => void }>();

	const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5 MB
	const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

	let stars = $state(5);
	let comment = $state('');
	let dishImage = $state<File | null>(null);
	let receiptImage = $state<File | null>(null);
	let submitting = $state(false);
	let formError = $state<string | null>(null);
	let success = $state<string | null>(null);

	function validateImage(file: File | null): string | null {
		if (!file) return null;
		if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
			return 'Image must be JPEG, PNG or WebP.';
		}
		if (file.size > MAX_IMAGE_SIZE) {
			return 'Image must be 5 MB or smaller.';
		}
		return null;
	}

	function pickFile(setter: (f: File | null) => void) {
		return (event: Event) => {
			const input = event.currentTarget as HTMLInputElement;
			const file = input.files?.[0] ?? null;
			const err = validateImage(file);
			if (err) {
				formError = err;
				input.value = '';
				setter(null);
				return;
			}
			formError = null;
			setter(file);
		};
	}

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		formError = null;
		success = null;
		try {
			const form = new FormData();
			// Backend stores 1-10 score; multiply stars (1-5) by 2.
			form.append('score', (stars * 2).toFixed(1));
			if (comment) form.append('comment', comment);
			if (dishImage) form.append('dish_image', dishImage);
			if (receiptImage) form.append('receipt_image', receiptImage);
			await reviewsApi.create(placeId, form);
			success = receiptImage
				? 'Thanks! Your review is awaiting moderation. The receipt photo will be checked for verification.'
				: 'Thanks! Your review is awaiting moderation.';
			comment = '';
			stars = 5;
			dishImage = null;
			receiptImage = null;
			// Refresh gamification state so the user sees the awarded points / badges.
			void gamificationService.refreshMe();
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

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">
			Dish photo <span class="text-xs text-zinc-500">(optional, +5 pts)</span>
		</span>
		<input
			type="file"
			accept="image/jpeg,image/png,image/webp"
			onchange={pickFile((f) => (dishImage = f))}
			class="text-sm"
		/>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-zinc-700 dark:text-zinc-300">
			Receipt photo <span class="text-xs text-zinc-500">(optional, +30 pts after verification)</span>
		</span>
		<input
			type="file"
			accept="image/jpeg,image/png,image/webp"
			onchange={pickFile((f) => (receiptImage = f))}
			class="text-sm"
		/>
	</label>

	<Button type="submit" loading={submitting}>Submit review</Button>
</form>
