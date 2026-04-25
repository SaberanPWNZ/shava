<script lang="ts">
	import { goto } from '$app/navigation';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { authService } from '$lib/services/auth.service';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

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
			fieldErrors = { confirm_password: 'Passwords do not match.' };
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
				formError = 'Could not register.';
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

<form class="flex flex-col gap-4" onsubmit={submit} novalidate>
	<Input
		id="register-email"
		label="Email"
		type="email"
		autocomplete="email"
		required
		bind:value={email}
		error={fieldError('email')}
	/>
	<div class="grid gap-4 sm:grid-cols-2">
		<Input
			id="register-first-name"
			label="First name"
			autocomplete="given-name"
			bind:value={firstName}
			error={fieldError('first_name')}
		/>
		<Input
			id="register-last-name"
			label="Last name"
			autocomplete="family-name"
			bind:value={lastName}
			error={fieldError('last_name')}
		/>
	</div>
	<Input
		id="register-password"
		label="Password"
		type="password"
		autocomplete="new-password"
		required
		bind:value={password}
		error={fieldError('password')}
	/>
	<Input
		id="register-confirm-password"
		label="Confirm password"
		type="password"
		autocomplete="new-password"
		required
		bind:value={confirmPassword}
		error={fieldError('confirm_password')}
	/>
	<Button type="submit" loading={submitting}>Create account</Button>
</form>
