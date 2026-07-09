<script lang="ts">
	let {
		id,
		label = '',
		value = $bindable(''),
		required = false,
		placeholder = '',
		error = null,
		children
	} = $props<{
		id: string;
		label?: string;
		value?: string | number;
		required?: boolean;
		placeholder?: string;
		error?: string | string[] | null;
		children: import('svelte').Snippet;
	}>();

	let errorText = $derived(Array.isArray(error) ? error.join(' ') : error);
</script>

<div class="flex flex-col gap-1.5">
	{#if label}
		<label for={id} class="text-sm font-medium text-stone-700 dark:text-stone-300">
			{label}{#if required}<span class="ml-0.5 text-amber-600" aria-hidden="true">*</span>{/if}
		</label>
	{/if}
	<select
		{id}
		{required}
		bind:value
		aria-invalid={errorText ? 'true' : undefined}
		aria-describedby={errorText ? `${id}-error` : undefined}
		class="w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-stone-900 shadow-sm transition focus:outline-none focus:ring-2 dark:bg-stone-900 dark:text-stone-100
			{errorText
			? 'border-red-400 focus:border-red-500 focus:ring-red-500/25 dark:border-red-700'
			: 'border-stone-300 focus:border-amber-500 focus:ring-amber-500/25 dark:border-stone-700'}"
	>
		{#if placeholder}
			<option value="">{placeholder}</option>
		{/if}
		{@render children()}
	</select>
	{#if errorText}
		<p id="{id}-error" class="text-sm text-red-600 dark:text-red-400">{errorText}</p>
	{/if}
</div>
