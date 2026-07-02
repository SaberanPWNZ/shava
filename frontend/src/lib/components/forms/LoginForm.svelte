<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authService } from '$lib/services/auth.service';
	import { ApiError, type FieldErrors } from '$lib/types/auth';
	import { m } from '$lib/paraglide/messages';

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
				formError = m.login_failed();
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
		id="login-email"
		label={m.field_email()}
		type="email"
		placeholder={m.field_email_placeholder()}
		autocomplete="email"
		required
		bind:value={email}
		error={fieldError('email')}
	/>
	<div class="flex flex-col gap-1.5">
		<Input
			id="login-password"
			label={m.field_password()}
			type="password"
			placeholder="••••••••"
			autocomplete="current-password"
			required
			bind:value={password}
			error={fieldError('password')}
		/>
		<p class="text-right text-sm">
			<a
				href="/forgot-password"
				class="font-medium text-amber-700 hover:underline dark:text-amber-400"
			>
				{m.login_forgot_password()}
			</a>
		</p>
	</div>
	<Button type="submit" size="lg" block loading={submitting}>{m.login_submit()}</Button>
</form>
