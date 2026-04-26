<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import Card from '$lib/components/ui/Card.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { ApiError } from '$lib/types/auth';

	type Status = 'pending' | 'success' | 'error';

	let status = $state<Status>('pending');
	let message = $state('');

	onMount(async () => {
		const token = page.params.token;
		if (!token) {
			status = 'error';
			message = 'Посилання недійсне.';
			return;
		}
		try {
			await authApi.confirmVerifyEmail(token);
			status = 'success';
			message = 'Адресу email підтверджено.';
		} catch (error) {
			status = 'error';
			message =
				error instanceof ApiError
					? 'Посилання недійсне або термін дії вичерпано.'
					: 'Не вдалося підтвердити email.';
		}
	});
</script>

<div class="mx-auto max-w-md py-12">
	<Card title="Підтвердження email">
		{#if status === 'pending'}
			<p class="text-sm text-zinc-600 dark:text-zinc-400">Перевіряємо посилання…</p>
		{:else if status === 'success'}
			<Alert variant="success">{message}</Alert>
			<p class="mt-4 text-center text-sm">
				<a href="/" class="font-medium text-orange-700 hover:underline">На головну</a>
			</p>
		{:else}
			<Alert variant="error">{message}</Alert>
			<p class="mt-4 text-center text-sm text-zinc-600 dark:text-zinc-400">
				<a href="/login" class="font-medium text-orange-700 hover:underline"
					>Повернутися до входу</a
				>
			</p>
		{/if}
	</Card>
</div>
