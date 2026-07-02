<script lang="ts">
	import { goto } from '$app/navigation';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { authService } from '$lib/services/auth.service';
	import { ApiError, type FieldErrors } from '$lib/types/auth';
	import { m } from '$lib/paraglide/messages';

	let email = $state('');
	let firstName = $state('');
	let lastName = $state('');
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
			fieldErrors = { confirm_password: m.register_passwords_mismatch() };
			submitting = false;
			return;
		}
		try {
			await authApi.register({
				email,
				password,
				first_name: firstName || undefined,
				last_name: lastName || undefined
			});
			await authService.login(email, password);
			await goto('/');
		} catch (error) {
			if (error instanceof ApiError) {
				fieldErrors = error.fieldErrors;
				formError = Object.keys(error.fieldErrors).length ? null : error.message;
			} else {
				formError = m.register_failed();
			}
		} finally {
			submitting = false;
		}
	}

	function fieldError(key: string): string | string[] | null {
		return fieldErrors[key] ?? null;
	}
</script>

{#if formError}
	<Alert variant="error">{formError}</Alert>
{/if}

<form class="flex flex-col gap-5" onsubmit={submit} novalidate>
	<Input
		id="register-email"
		label={m.field_email()}
		type="email"
		placeholder={m.field_email_placeholder()}
		autocomplete="email"
		required
		bind:value={email}
		error={fieldError('email')}
	/>
	<div class="grid gap-5 sm:grid-cols-2">
		<Input
			id="register-first-name"
			label={m.field_first_name()}
			placeholder={m.field_first_name_placeholder()}
			autocomplete="given-name"
			bind:value={firstName}
			error={fieldError('first_name')}
		/>
		<Input
			id="register-last-name"
			label={m.field_last_name()}
			placeholder={m.field_last_name_placeholder()}
			autocomplete="family-name"
			bind:value={lastName}
			error={fieldError('last_name')}
		/>
	</div>
	<Input
		id="register-password"
		label={m.field_password()}
		type="password"
		placeholder={m.register_password_placeholder()}
		autocomplete="new-password"
		required
		hint={m.register_password_hint()}
		bind:value={password}
		error={fieldError('password')}
	/>
	<Input
		id="register-confirm-password"
		label={m.field_confirm_password()}
		type="password"
		placeholder={m.register_confirm_placeholder()}
		autocomplete="new-password"
		required
		bind:value={confirmPassword}
		error={fieldError('confirm_password')}
	/>
	<Button type="submit" size="lg" block loading={submitting}>{m.register_submit()}</Button>
</form>
