<script lang="ts">
	let {
		id,
		label = '',
		type = 'text',
		value = $bindable(''),
		placeholder = '',
		autocomplete = '',
		required = false,
		error = null
	} = $props<{
		id: string;
		label?: string;
		type?: string;
		value?: string;
		placeholder?: string;
		autocomplete?: string;
		required?: boolean;
		error?: string | string[] | null;
	}>();

	let errorText = $derived(Array.isArray(error) ? error.join(' ') : error);
</script>

<div class="flex flex-col gap-1">
	{#if label}
		<label for={id} class="text-sm font-medium text-zinc-700 dark:text-zinc-300">{label}</label>
	{/if}
	<input
		{id}
		{type}
		{placeholder}
		{autocomplete}
		{required}
		bind:value
		class="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
		class:border-red-500={errorText}
	/>
	{#if errorText}
		<p class="text-sm text-red-600 dark:text-red-400">{errorText}</p>
	{/if}
</div>
