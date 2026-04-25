<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authService } from '$lib/services/auth.service';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

	let email = $state('');
	let password = $state('');
	let submitting = $state(false);
	let formError = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		formError = null;
		fieldErrors = {};
		try {
			await authService.login(email, password);
			const next = page.url.searchParams.get('next') || '/';
			await goto(next);
		} catch (error) {
			if (error instanceof ApiError) {
				fieldErrors = error.fieldErrors;
				formError = Object.keys(error.fieldErrors).length ? null : error.message;
			} else {
				formError = 'Could not sign in.';
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
		id="login-email"
		label="Email"
		type="email"
		autocomplete="email"
		required
		bind:value={email}
		error={fieldError('email')}
	/>
	<Input
		id="login-password"
		label="Password"
		type="password"
		autocomplete="current-password"
		required
		bind:value={password}
		error={fieldError('password')}
	/>
	<Button type="submit" loading={submitting}>Sign in</Button>
</form>
