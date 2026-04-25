<script lang="ts">
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import MapPicker from '$lib/components/places/MapPicker.svelte';
	import { placesApi } from '$lib/api/places.api';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

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
			formError = 'Please pick a location on the map.';
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
				formError = 'Could not submit the place.';
			}
		} finally {
			submitting = false;
		}
	}
</script>

<div class="mx-auto max-w-2xl py-8">
	<Card title="Submit a new place">
		{#if success}
			<Alert variant="success">
				Thanks! Your place has been submitted and is awaiting moderation.
			</Alert>
		{/if}
		{#if formError}
			<Alert variant="error">{formError}</Alert>
		{/if}

		<form class="flex flex-col gap-4" onsubmit={submit} novalidate>
			<Input id="place-name" label="Name" required bind:value={name} error={fieldError('name')} />
			<Input
				id="place-city"
				label="City"
				required
				bind:value={city}
				error={fieldError('city')}
			/>
			<Input
				id="place-address"
				label="Address"
				required
				bind:value={address}
				error={fieldError('address')}
			/>
			<label class="flex flex-col gap-1 text-sm">
				<span class="font-medium text-zinc-700 dark:text-zinc-300">Description</span>
				<textarea
					rows="4"
					bind:value={description}
					class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
				></textarea>
			</label>
			<label class="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
				<input type="checkbox" bind:checked={delivery} class="rounded" />
				Delivery available
			</label>

			<div class="flex flex-col gap-1 text-sm">
				<span class="font-medium text-zinc-700 dark:text-zinc-300">
					Location <span class="text-red-600">*</span>
				</span>
				<p class="text-xs text-zinc-500 dark:text-zinc-400">
					Click on the map or drag the marker to pin the exact spot.
				</p>
				<MapPicker bind:value={coords} />
				{#if coords}
					<p class="text-xs text-zinc-600 dark:text-zinc-400">
						Selected: {coords.lat.toFixed(6)}, {coords.lng.toFixed(6)}
					</p>
				{/if}
				{#if fieldError('latitude') || fieldError('longitude')}
					<p class="text-sm text-red-600">
						{fieldError('latitude') ?? fieldError('longitude')}
					</p>
				{/if}
			</div>

			<label class="flex flex-col gap-1 text-sm">
				<span class="font-medium text-zinc-700 dark:text-zinc-300">Main image</span>
				<input type="file" accept="image/*" onchange={onFile} class="text-sm" />
				{#if fieldError('main_image')}
					<p class="text-sm text-red-600">{fieldError('main_image')}</p>
				{/if}
			</label>
			<Button type="submit" loading={submitting}>Submit place</Button>
		</form>
	</Card>
</div>
