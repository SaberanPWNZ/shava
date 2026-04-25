<script lang="ts">
	import Alert from '$lib/components/ui/Alert.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { placesApi } from '$lib/api/places.api';
	import { ApiError, type FieldErrors } from '$lib/types/auth';

	let name = $state('');
	let district = $state('Unknown');
	let address = $state('');
	let description = $state('');
	let delivery = $state(false);
	let mainImage = $state<File | null>(null);

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
		try {
			const data = new FormData();
			data.set('name', name);
			data.set('district', district);
			data.set('address', address);
			data.set('description', description);
			data.set('delivery', String(delivery));
			if (mainImage) data.set('main_image', mainImage);
			await placesApi.create(data);
			success = true;
			name = '';
			district = 'Unknown';
			address = '';
			description = '';
			delivery = false;
			mainImage = null;
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
			<label class="flex flex-col gap-1 text-sm">
				<span class="font-medium text-zinc-700 dark:text-zinc-300">District</span>
				<select
					bind:value={district}
					class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
				>
					<option value="Unknown">Unknown</option>
					<option value="Dnipro">Дніпровський</option>
					<option value="Desna">Деснянський</option>
					<option value="Solomyanka">Солом'янський</option>
					<option value="Shevchenko">Шевченківський</option>
					<option value="Pechersk">Печерський</option>
					<option value="Obolon">Оболонський</option>
					<option value="Podil">Подільський</option>
					<option value="Svyatoshyn">Святошинський</option>
					<option value="Holosiiv">Голосіївський</option>
					<option value="Darnytsia">Дарницький</option>
				</select>
			</label>
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
