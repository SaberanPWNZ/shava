<script lang="ts">
	import Card from '$lib/components/ui/Card.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

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
				formError = 'Не вдалося надіслати запит.';
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
	<Card title="Скидання пароля">
		{#if submitted}
			<Alert variant="success">
				Якщо адреса зареєстрована — на неї надіслано лист із посиланням для скидання пароля.
			</Alert>
			<p class="mt-4 text-center text-sm">
				<a href="/login" class="font-medium text-orange-600 hover:underline"
					>Повернутися до входу</a
				>
			</p>
		{:else}
			{#if formError}
				<Alert variant="error">{formError}</Alert>
			{/if}
			<form class="flex flex-col gap-4" onsubmit={submit} novalidate>
				<Input
					id="forgot-email"
					label="Email"
					type="email"
					autocomplete="email"
					required
					bind:value={email}
					error={fieldError('email')}
				/>
				<Button type="submit" loading={submitting}>Надіслати посилання</Button>
			</form>
			<p class="mt-4 text-center text-sm text-zinc-600 dark:text-zinc-400">
				<a href="/login" class="font-medium text-orange-600 hover:underline"
					>Повернутися до входу</a
				>
			</p>
		{/if}
	</Card>
</div>
