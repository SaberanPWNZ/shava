<script lang="ts">
	import Card from '$lib/components/ui/Card.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { ApiError, type FieldErrors } from '$lib/types/auth';
	import { m } from '$lib/paraglide/messages';

	let email = $state('');
	let submitting = $state(false);
	let submitted = $state(false);
	let formError = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		formError = null;
		fieldErrors = {};
		try {
			await authApi.requestPasswordReset(email);
			submitted = true;
		} catch (error) {
			if (error instanceof ApiError) {
				fieldErrors = error.fieldErrors;
				formError = Object.keys(error.fieldErrors).length ? null : error.message;
			} else {
				formError = m.forgot_request_failed();
			}
		} finally {
			submitting = false;
		}
	}

	function fieldError(key: string): string | string[] | null {
		return fieldErrors[key] ?? null;
	}
</script>

<div class="mx-auto max-w-md py-12">
	<Card title={m.forgot_title()}>
		{#if submitted}
			<Alert variant="success">
				{m.forgot_success()}
			</Alert>
			<p class="mt-4 text-center text-sm">
				<a href="/login" class="font-medium text-amber-700 hover:underline"
					>{m.forgot_back_to_login()}</a
				>
			</p>
		{:else}
			{#if formError}
				<Alert variant="error">{formError}</Alert>
			{/if}
			<form class="flex flex-col gap-4" onsubmit={submit} novalidate>
				<Input
					id="forgot-email"
					label={m.field_email()}
					type="email"
					autocomplete="email"
					required
					bind:value={email}
					error={fieldError('email')}
				/>
				<Button type="submit" loading={submitting}>{m.forgot_submit()}</Button>
			</form>
			<p class="mt-4 text-center text-sm text-stone-600 dark:text-stone-400">
				<a href="/login" class="font-medium text-amber-700 hover:underline"
					>{m.forgot_back_to_login()}</a
				>
			</p>
		{/if}
	</Card>
</div>
