<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Card from '$lib/components/ui/Card.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

	let password = $state('');
	let confirmPassword = $state('');
	let submitting = $state(false);
	let formError = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		formError = null;
		fieldErrors = {};
		if (password !== confirmPassword) {
			fieldErrors = { confirm_password: 'Паролі не збігаються.' };
			submitting = false;
			return;
		}
		const token = page.params.token;
		if (!token) {
			formError = 'Посилання недійсне.';
			submitting = false;
			return;
		}
		try {
			await authApi.confirmPasswordReset(token, password);
			await goto('/login?reset=1');
		} catch (error) {
			if (error instanceof ApiError) {
				if (error.status === 400 && !Object.keys(error.fieldErrors).length) {
					formError = 'Посилання недійсне або термін дії вичерпано.';
				} else {
					fieldErrors = error.fieldErrors;
					formError = Object.keys(error.fieldErrors).length ? null : error.message;
				}
			} else {
				formError = 'Не вдалося скинути пароль.';
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
	<Card title="Новий пароль">
		{#if formError}
			<Alert variant="error">{formError}</Alert>
		{/if}
		<form class="flex flex-col gap-4" onsubmit={submit} novalidate>
			<Input
				id="reset-password"
				label="Новий пароль"
				type="password"
				autocomplete="new-password"
				required
				bind:value={password}
				error={fieldError('new_password')}
			/>
			<Input
				id="reset-confirm-password"
				label="Підтвердження пароля"
				type="password"
				autocomplete="new-password"
				required
				bind:value={confirmPassword}
				error={fieldError('confirm_password')}
			/>
			<Button type="submit" loading={submitting}>Зберегти пароль</Button>
		</form>
	</Card>
</div>
