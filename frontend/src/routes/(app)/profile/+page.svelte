<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import LevelProgressBar from '$lib/components/gamification/LevelProgressBar.svelte';
	import BadgeGrid from '$lib/components/gamification/BadgeGrid.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { gamificationStore } from '$lib/stores/gamification.svelte';
	import { gamificationService } from '$lib/services/gamification.service';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

	let firstName = $state(authStore.user?.first_name ?? '');
	let lastName = $state(authStore.user?.last_name ?? '');
	let saving = $state(false);
	let savedMessage = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});
	let formError = $state<string | null>(null);

	onMount(() => {
		void gamificationService.refreshMe();
	});

	const REASON_LABELS: Record<string, string> = {
		REVIEW_CREATED: 'Posted a review',
		REVIEW_FIRST_FOR_PLACE: 'First review for a place',
		REVIEW_PHOTO: 'Added a dish photo',
		REVIEW_VERIFIED: 'Review verified',
		REVIEW_HELPFUL_VOTE: 'Marked as helpful',
		BADGE_AWARDED: 'Badge bonus',
		MANUAL_ADJUSTMENT: 'Adjustment'
	};

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

<div class="mx-auto flex max-w-2xl flex-col gap-6 py-8">
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

	<Card title="Achievements">
		{#if gamificationStore.me}
			<div class="flex flex-col gap-6">
				<LevelProgressBar profile={gamificationStore.me} />

				<section class="flex flex-col gap-3">
					<h3 class="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Badges</h3>
					<BadgeGrid earned={gamificationStore.me.badges} />
				</section>

				<section class="flex flex-col gap-2">
					<h3 class="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
						Recent activity
					</h3>
					{#if gamificationStore.me.recent_transactions.length === 0}
						<p class="text-sm text-zinc-500 dark:text-zinc-400">
							No activity yet — leave your first review to earn points.
						</p>
					{:else}
						<ul class="flex flex-col gap-2 text-sm">
							{#each gamificationStore.me.recent_transactions as tx (tx.id)}
								<li
									class="flex items-center justify-between gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900"
								>
									<div class="flex flex-col">
										<span class="text-zinc-900 dark:text-zinc-100">
											{REASON_LABELS[tx.reason] ?? tx.reason}
										</span>
										<span class="text-xs text-zinc-500 dark:text-zinc-400">
											{new Date(tx.created_at).toLocaleString()}
										</span>
									</div>
									<span
										class="font-semibold {tx.amount >= 0
											? 'text-emerald-600 dark:text-emerald-400'
											: 'text-rose-600 dark:text-rose-400'}"
									>
										{tx.amount >= 0 ? '+' : ''}{tx.amount}
									</span>
								</li>
							{/each}
						</ul>
					{/if}
				</section>
			</div>
		{:else if gamificationStore.loading}
			<p class="text-sm text-zinc-500 dark:text-zinc-400">Loading achievements…</p>
		{:else}
			<p class="text-sm text-zinc-500 dark:text-zinc-400">
				Sign in and post a review to start earning points.
			</p>
		{/if}
	</Card>
</div>
