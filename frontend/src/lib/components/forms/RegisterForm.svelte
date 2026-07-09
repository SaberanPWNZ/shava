<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { authApi } from '$lib/api/auth.api';
	import { citiesApi } from '$lib/api/places.api';
	import { authService } from '$lib/services/auth.service';
	import { ApiError, type FieldErrors } from '$lib/types/auth';
	import type { City } from '$lib/types';
	import { m } from '$lib/paraglide/messages';

	let email = $state('');
	let firstName = $state('');
	let lastName = $state('');
	let phone = $state('');
	let cityId = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let termsAccepted = $state(false);
	let marketingOptIn = $state(false);
	let submitting = $state(false);
	let formError = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});

	let cities = $state<City[]>([]);

	onMount(async () => {
		try {
			cities = await citiesApi.list();
		} catch {
			// City selection is a nice-to-have — registration must still work
			// if the reference list can't be fetched (e.g. backend hiccup).
			cities = [];
		}
	});

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
		if (!termsAccepted) {
			fieldErrors = { terms_accepted: m.register_terms_required() };
			submitting = false;
			return;
		}
		try {
			await authApi.register({
				email,
				password,
				first_name: firstName || undefined,
				last_name: lastName || undefined,
				phone: phone || undefined,
				city: cityId ? Number(cityId) : undefined,
				terms_accepted: termsAccepted,
				marketing_opt_in: marketingOptIn
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
	<div class="grid gap-5 sm:grid-cols-2">
		<Input
			id="register-phone"
			label={m.field_phone()}
			type="tel"
			placeholder={m.field_phone_placeholder()}
			autocomplete="tel"
			hint={m.field_phone_hint()}
			bind:value={phone}
			error={fieldError('phone')}
		/>
		<Select
			id="register-city"
			label={m.field_city()}
			placeholder={m.field_city_placeholder()}
			bind:value={cityId}
			error={fieldError('city')}
		>
			{#each cities as city (city.id)}
				<option value={String(city.id)}>{city.name}</option>
			{/each}
		</Select>
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

	<div class="flex flex-col gap-3 border-t border-stone-200 pt-4 dark:border-stone-800">
		<label class="flex items-start gap-3 text-sm text-stone-700 dark:text-stone-300">
			<input
				type="checkbox"
				required
				bind:checked={termsAccepted}
				aria-invalid={fieldError('terms_accepted') ? 'true' : undefined}
				aria-describedby={fieldError('terms_accepted') ? 'register-terms-error' : undefined}
				class="mt-0.5 h-4 w-4 shrink-0 rounded border-stone-300 text-amber-600 focus:ring-2 focus:ring-amber-500/40 dark:border-stone-600 dark:bg-stone-800"
			/>
			<span>
				{m.register_terms_prefix()}
				<a
					href="/terms"
					target="_blank"
					rel="noopener"
					class="font-medium text-amber-700 hover:underline dark:text-amber-400"
				>
					{m.register_terms_link()}
				</a>
			</span>
		</label>
		{#if fieldError('terms_accepted')}
			<p id="register-terms-error" class="-mt-2 ml-7 text-sm text-red-600 dark:text-red-400">
				{fieldError('terms_accepted')}
			</p>
		{/if}

		<label class="flex items-start gap-3 text-sm text-stone-700 dark:text-stone-300">
			<input
				type="checkbox"
				bind:checked={marketingOptIn}
				class="mt-0.5 h-4 w-4 shrink-0 rounded border-stone-300 text-amber-600 focus:ring-2 focus:ring-amber-500/40 dark:border-stone-600 dark:bg-stone-800"
			/>
			<span>{m.register_marketing_opt_in()}</span>
		</label>
	</div>

	<Button type="submit" size="lg" block loading={submitting}>{m.register_submit()}</Button>
</form>
