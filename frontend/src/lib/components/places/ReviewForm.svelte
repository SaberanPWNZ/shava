<script lang="ts">
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import StarRating from '$lib/components/places/StarRating.svelte';
	import { reviewsApi } from '$lib/api/places.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { toasts } from '$lib/stores/toasts.svelte';
	import { gamificationService } from '$lib/services/gamification.service';
	import { ApiError } from '$lib/types/auth';
	import type { Review } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let { placeId, oncreated } = $props<{ placeId: number; oncreated?: (review: Review) => void }>();

	const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
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
			return m.review_image_type_error();
		}
		if (file.size > MAX_IMAGE_SIZE) {
			return m.review_image_size_error();
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
			form.append('score', (stars * 2).toFixed(1));
			if (comment) form.append('comment', comment);
			if (dishImage) form.append('dish_image', dishImage);
			if (receiptImage) form.append('receipt_image', receiptImage);
			const created = await reviewsApi.create(placeId, form);
			success = receiptImage ? m.review_success_with_receipt() : m.review_success();
			toasts.success(m.review_toast_submitted());
			const optimistic: Review =
				(created as Review) ??
				({
					id: Date.now() * -1,
					place: placeId,
					author: authStore.user?.id ?? 0,
					author_username: authStore.user?.username,
					score: (stars * 2).toFixed(1),
					comment: comment || null,
					created_at: new Date().toISOString(),
					is_moderated: false
				} as Review);
			comment = '';
			stars = 5;
			dishImage = null;
			receiptImage = null;
			void gamificationService.refreshMe();
			oncreated?.(optimistic);
		} catch (error) {
			formError = error instanceof ApiError ? error.message : m.review_submit_failed();
			toasts.error(formError);
		} finally {
			submitting = false;
		}
	}
</script>

<form
	class="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900"
	onsubmit={submit}
>
	<h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">
		{m.review_form_title()}
	</h3>

	{#if formError}
		<Alert variant="error">{formError}</Alert>
	{/if}
	{#if success}
		<Alert variant="success">{success}</Alert>
	{/if}

	<div class="flex items-center gap-2">
		<span class="text-sm font-medium text-stone-700 dark:text-stone-300"
			>{m.review_your_rating()}</span
		>
		<StarRating value={stars} interactive onchange={(n) => (stars = n)} />
	</div>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">{m.review_comment()}</span>
		<textarea
			rows="3"
			bind:value={comment}
			class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
		></textarea>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">
			{m.review_dish_photo()}
			<span class="text-xs text-stone-500">{m.review_dish_photo_hint()}</span>
		</span>
		<input
			type="file"
			accept="image/jpeg,image/png,image/webp"
			onchange={pickFile((f) => (dishImage = f))}
			class="text-sm"
		/>
	</label>

	<label class="flex flex-col gap-1 text-sm">
		<span class="font-medium text-stone-700 dark:text-stone-300">
			{m.review_receipt_photo()}
			<span class="text-xs text-stone-500">{m.review_receipt_photo_hint()}</span>
		</span>
		<input
			type="file"
			accept="image/jpeg,image/png,image/webp"
			onchange={pickFile((f) => (receiptImage = f))}
			class="text-sm"
		/>
	</label>

	<Button type="submit" loading={submitting}>{m.review_submit()}</Button>
</form>
