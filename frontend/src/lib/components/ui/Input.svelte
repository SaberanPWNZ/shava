<script lang="ts">
	import { m } from '$lib/paraglide/messages';

	let {
		id,
		label = '',
		type = 'text',
		value = $bindable(''),
		placeholder = '',
		autocomplete = '',
		required = false,
		hint = '',
		error = null
	} = $props<{
		id: string;
		label?: string;
		type?: string;
		value?: string;
		placeholder?: string;
		autocomplete?: string;
		required?: boolean;
		hint?: string;
		error?: string | string[] | null;
	}>();

	let errorText = $derived(Array.isArray(error) ? error.join(' ') : error);
	let showPassword = $state(false);
	let effectiveType = $derived(type === 'password' && showPassword ? 'text' : type);
	let describedBy = $derived(errorText ? `${id}-error` : hint ? `${id}-hint` : undefined);
</script>

<div class="flex flex-col gap-1.5">
	{#if label}
		<label for={id} class="text-sm font-medium text-stone-700 dark:text-stone-300">
			{label}{#if required}<span class="ml-0.5 text-amber-600" aria-hidden="true">*</span>{/if}
		</label>
	{/if}
	<div class="relative">
		<input
			{id}
			{placeholder}
			{autocomplete}
			{required}
			type={effectiveType}
			bind:value
			aria-invalid={errorText ? 'true' : undefined}
			aria-describedby={describedBy}
			class="w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-stone-900 shadow-sm transition placeholder:text-stone-400 focus:outline-none focus:ring-2 dark:bg-stone-900 dark:text-stone-100
				{errorText
				? 'border-red-400 focus:border-red-500 focus:ring-red-500/25 dark:border-red-700'
				: 'border-stone-300 focus:border-amber-500 focus:ring-amber-500/25 dark:border-stone-700'}
				{type === 'password' ? 'pr-11' : ''}"
		/>
		{#if type === 'password'}
			<button
				type="button"
				onclick={() => (showPassword = !showPassword)}
				class="absolute inset-y-0 right-0 flex w-11 items-center justify-center rounded-r-xl text-stone-400 transition hover:text-stone-600 focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:outline-none dark:hover:text-stone-300"
				aria-label={showPassword ? m.password_hide() : m.password_show()}
				aria-pressed={showPassword}
			>
				{#if showPassword}
					<svg
						viewBox="0 0 24 24"
						class="h-5 w-5"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M3 3l18 18M10.6 10.7a2.5 2.5 0 0 0 3.5 3.6M6.7 6.8C4.6 8.1 3.1 10 2.5 12c1.3 3.9 5.1 6.5 9.5 6.5 1.7 0 3.3-.4 4.7-1.1M9.9 5.7A10 10 0 0 1 12 5.5c4.4 0 8.2 2.6 9.5 6.5-.4 1.1-1 2.2-1.8 3.1"
						/>
					</svg>
				{:else}
					<svg
						viewBox="0 0 24 24"
						class="h-5 w-5"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M2.5 12C3.8 8.1 7.6 5.5 12 5.5s8.2 2.6 9.5 6.5c-1.3 3.9-5.1 6.5-9.5 6.5S3.8 15.9 2.5 12Z"
						/>
						<circle cx="12" cy="12" r="2.5" />
					</svg>
				{/if}
			</button>
		{/if}
	</div>
	{#if errorText}
		<p id="{id}-error" class="flex items-start gap-1 text-sm text-red-600 dark:text-red-400">
			<svg
				viewBox="0 0 24 24"
				class="mt-0.5 h-4 w-4 shrink-0"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				aria-hidden="true"
			>
				<circle cx="12" cy="12" r="9" />
				<path stroke-linecap="round" d="M12 8v4.5m0 3v.5" />
			</svg>
			{errorText}
		</p>
	{:else if hint}
		<p id="{id}-hint" class="text-sm text-stone-500 dark:text-stone-400">{hint}</p>
	{/if}
</div>
