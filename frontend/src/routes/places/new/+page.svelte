<script lang="ts">
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import MapPicker from '$lib/components/places/MapPicker.svelte';
	import { placesApi } from '$lib/api/places.api';
	import { ApiError, type FieldErrors } from '$lib/types/auth';
	import { m } from '$lib/paraglide/messages';

	let name = $state('');
	let city = $state('Київ');
	let address = $state('');
	let description = $state('');
	let delivery = $state(false);
	let mainImage = $state<File | null>(null);
	let coords = $state<{ lat: number; lng: number } | null>(null);

	let submitting = $state(false);
	let success = $state(false);
	let formError = $state<string | null>(null);
	let fieldErrors = $state<FieldErrors>({});

	function fieldError(key: string): string | string[] | null {
		return fieldErrors[key] ?? null;
	}

	function onFile(event: Event) {
		const input = event.target as HTMLInputElement;
		mainImage = input.files?.[0] ?? null;
	}

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		formError = null;
		fieldErrors = {};
		success = false;

		if (!coords) {
			formError = m.new_place_location_required();
			submitting = false;
			return;
		}

		try {
			const data = new FormData();
			data.set('name', name);
			data.set('city', city);
			data.set('address', address);
			data.set('description', description);
			data.set('delivery', String(delivery));
			data.set('latitude', coords.lat.toFixed(6));
			data.set('longitude', coords.lng.toFixed(6));
			if (mainImage) data.set('main_image', mainImage);
			await placesApi.create(data);
			success = true;
			name = '';
			city = 'Київ';
			address = '';
			description = '';
			delivery = false;
			mainImage = null;
			coords = null;
		} catch (error) {
			if (error instanceof ApiError) {
				fieldErrors = error.fieldErrors;
				formError = Object.keys(error.fieldErrors).length ? null : error.message;
			} else {
				formError = m.new_place_submit_failed();
			}
		} finally {
			submitting = false;
		}
	}
</script>

<div class="mx-auto max-w-2xl py-8">
	<Card title={m.new_place_title()}>
		{#if success}
			<Alert variant="success">
				{m.new_place_success()}
			</Alert>
		{/if}
		{#if formError}
			<Alert variant="error">{formError}</Alert>
		{/if}

		<form class="flex flex-col gap-4" onsubmit={submit} novalidate>
			<Input
				id="place-name"
				label={m.new_place_name()}
				required
				bind:value={name}
				error={fieldError('name')}
			/>
			<Input
				id="place-city"
				label={m.filters_city()}
				required
				bind:value={city}
				error={fieldError('city')}
			/>
			<Input
				id="place-address"
				label={m.new_place_address()}
				required
				bind:value={address}
				error={fieldError('address')}
			/>
			<label class="flex flex-col gap-1 text-sm">
				<span class="font-medium text-stone-700 dark:text-stone-300"
					>{m.new_place_description()}</span
				>
				<textarea
					rows="4"
					bind:value={description}
					class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm dark:border-stone-700 dark:bg-stone-900"
				></textarea>
			</label>
			<label class="flex items-center gap-2 text-sm text-stone-700 dark:text-stone-300">
				<input type="checkbox" bind:checked={delivery} class="rounded" />
				{m.filters_delivery_available()}
			</label>

			<div class="flex flex-col gap-1 text-sm">
				<span class="font-medium text-stone-700 dark:text-stone-300">
					{m.new_place_location()} <span class="text-red-600">*</span>
				</span>
				<p class="text-xs text-stone-500 dark:text-stone-400">
					{m.new_place_location_hint()}
				</p>
				<MapPicker bind:value={coords} />
				{#if coords}
					<p class="text-xs text-stone-600 dark:text-stone-400">
						{m.new_place_selected({ coords: `${coords.lat.toFixed(6)}, ${coords.lng.toFixed(6)}` })}
					</p>
				{/if}
				{#if fieldError('latitude') || fieldError('longitude')}
					<p class="text-sm text-red-600">
						{fieldError('latitude') ?? fieldError('longitude')}
					</p>
				{/if}
			</div>

			<label class="flex flex-col gap-1 text-sm">
				<span class="font-medium text-stone-700 dark:text-stone-300"
					>{m.new_place_main_image()}</span
				>
				<input type="file" accept="image/*" onchange={onFile} class="text-sm" />
				{#if fieldError('main_image')}
					<p class="text-sm text-red-600">{fieldError('main_image')}</p>
				{/if}
			</label>
			<Button type="submit" loading={submitting}>{m.new_place_submit()}</Button>
		</form>
	</Card>
</div>
