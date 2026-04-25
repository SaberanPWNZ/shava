<script lang="ts">
	type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';
	let {
		type = 'button',
		variant = 'primary' as Variant,
		loading = false,
		disabled = false,
		onclick,
		children
	} = $props<{
		type?: 'button' | 'submit' | 'reset';
		variant?: Variant;
		loading?: boolean;
		disabled?: boolean;
		onclick?: (e: MouseEvent) => void;
		children: import('svelte').Snippet;
	}>();

	const variants: Record<Variant, string> = {
		primary: 'bg-orange-600 text-white hover:bg-orange-700',
		secondary:
			'border border-zinc-300 bg-white text-zinc-800 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800',
		danger: 'bg-red-600 text-white hover:bg-red-700',
		ghost: 'text-zinc-700 hover:bg-zinc-100 dark:text-zinc-200 dark:hover:bg-zinc-800'
	};
</script>

<button
	{type}
	disabled={disabled || loading}
	{onclick}
	class="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-semibold shadow-sm transition disabled:opacity-50 {variants[
		variant as Variant
	]}"
>
	{#if loading}
		<span class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
	{/if}
	{@render children()}
</button>
