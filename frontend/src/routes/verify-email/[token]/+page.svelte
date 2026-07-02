<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import Card from '$lib/components/ui/Card.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { ApiError } from '$lib/types/auth';
	import { m } from '$lib/paraglide/messages';

	type Status = 'pending' | 'success' | 'error';

	let status = $state<Status>('pending');
	let message = $state('');

	onMount(async () => {
		const token = page.params.token;
		if (!token) {
			status = 'error';
			message = m.token_invalid();
			return;
		}
		try {
			await authApi.confirmVerifyEmail(token);
			status = 'success';
			message = m.verify_email_success();
		} catch (error) {
			status = 'error';
			message = error instanceof ApiError ? m.token_invalid_or_expired() : m.verify_email_failed();
		}
	});
</script>

<div class="mx-auto max-w-md py-12">
	<Card title={m.verify_email_title()}>
		{#if status === 'pending'}
			<p class="text-sm text-stone-600 dark:text-stone-400">{m.verify_email_checking()}</p>
		{:else if status === 'success'}
			<Alert variant="success">{message}</Alert>
			<p class="mt-4 text-center text-sm">
				<a href="/" class="font-medium text-amber-700 hover:underline">{m.go_home()}</a>
			</p>
		{:else}
			<Alert variant="error">{message}</Alert>
			<p class="mt-4 text-center text-sm text-stone-600 dark:text-stone-400">
				<a href="/login" class="font-medium text-amber-700 hover:underline"
					>{m.forgot_back_to_login()}</a
				>
			</p>
		{/if}
	</Card>
</div>
