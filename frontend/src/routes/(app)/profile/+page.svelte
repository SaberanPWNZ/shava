<script lang="ts">
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

	let firstName = $state(authStore.user?.first_name ?? '');
	let lastName = $state(authStore.user?.last_name ?? '');
	let saving = $state(false);
	let savedMessage = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});
	let formError = $state<string | null>(null);

	async function save(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		fieldErrors = {};
		formError = null;
		savedMessage = null;
		try {
			const updated = await authApi.updateMe({ first_name: firstName, last_name: lastName });
			authStore.setUser(updated);
			savedMessage = 'Profile updated.';
		} catch (error) {
			if (error instanceof ApiError) {
				fieldErrors = error.fieldErrors;
				formError = Object.keys(error.fieldErrors).length ? null : error.message;
			} else {
				formError = 'Could not update profile.';
			}
		} finally {
			saving = false;
		}
	}

	function fieldError(key: string): string | string[] | null {
		return fieldErrors[key] ?? null;
	}
</script>

<div class="mx-auto max-w-2xl py-8">
	<Card title="Your profile">
		{#if authStore.user}
			<dl class="mb-6 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
				<div>
					<dt class="font-medium text-zinc-500 dark:text-zinc-400">Email</dt>
					<dd class="text-zinc-900 dark:text-zinc-100">{authStore.user.email}</dd>
				</div>
				<div>
					<dt class="font-medium text-zinc-500 dark:text-zinc-400">Verified</dt>
					<dd class="text-zinc-900 dark:text-zinc-100">
						{authStore.user.is_verified ? 'Yes' : 'No'}
					</dd>
				</div>
			</dl>
		{/if}

		{#if savedMessage}
			<Alert variant="success">{savedMessage}</Alert>
		{/if}
		{#if formError}
			<Alert variant="error">{formError}</Alert>
		{/if}

		<form class="mt-4 flex flex-col gap-4" onsubmit={save} novalidate>
			<div class="grid gap-4 sm:grid-cols-2">
				<Input
					id="profile-first-name"
					label="First name"
					autocomplete="given-name"
					bind:value={firstName}
					error={fieldError('first_name')}
				/>
				<Input
					id="profile-last-name"
					label="Last name"
					autocomplete="family-name"
					bind:value={lastName}
					error={fieldError('last_name')}
				/>
			</div>
			<Button type="submit" loading={saving}>Save changes</Button>
		</form>
	</Card>
</div>
